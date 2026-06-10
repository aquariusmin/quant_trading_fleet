import time
import requests
import pandas as pd
from typing import Dict, Optional
from config.settings import config
from core.logger import get_logger

logger = get_logger("kis_broker")

class KISBroker:
    def __init__(self):
        self.mode = config.STOCK_MODE
        
        if self.mode == "mock":
            self.base_url = "https://openapivts.koreainvestment.com:29443"
            logger.info("KIS Broker initialized in MOCK mode.")
        else:
            self.base_url = "https://openapi.koreainvestment.com:9443"
            logger.warning("KIS Broker initialized in REAL mode. Real money will be used.")

        self.app_key = config.KIS_APP_KEY
        self.app_secret = config.KIS_APP_SECRET
        self.cano = config.KIS_CANO
        self.acnt_prdt_cd = config.KIS_ACNT_PRDT_CD
        
        self.access_token = None
        self.token_expires_at = 0
        self._authenticate()

    def _authenticate(self):
        """
        Generate OAuth2 Access Token for KIS API.
        """
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }

        try:
            res = requests.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            self.access_token = data.get("access_token")
            expires_in = data.get("expires_in", 86400)
            self.token_expires_at = time.time() + int(expires_in) - 60  # 1 min buffer
            logger.info("Successfully authenticated with KIS API.")
        except Exception as e:
            logger.error(f"Failed to authenticate with KIS API: {e}")
            raise

    def _get_headers(self, tr_id: str) -> Dict[str, str]:
        if time.time() > self.token_expires_at:
            self._authenticate()
            
        return {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id
        }

    def get_ticker_price(self, symbol: str, is_overseas: bool = False) -> float:
        """
        Get the current price. 
        is_overseas=True for US stocks (e.g., 'AAPL').
        """
        if not is_overseas:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = self._get_headers(tr_id="FHKST01010100")
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": symbol
            }
        else:
            url = f"{self.base_url}/uapi/overseas-stock/v1/quotations/price"
            headers = self._get_headers(tr_id="HHDFS70100100")
            # For US stocks, exchange code is required. NASD/NYSE/AMEX
            # We assume NASD for simplicity or can be extended.
            params = {
                "AUTH": "",
                "EXCD": "NASD", 
                "SYMB": symbol
            }
        
        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
            data = res.json()
            if data["rt_cd"] != "0":
                raise Exception(data.get("msg1"))
            
            if not is_overseas:
                return float(data["output"]["stck_prpr"])
            else:
                return float(data["output"]["last"])
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise

    def get_ohlcv(self, symbol: str, start_date: str, end_date: str, is_overseas: bool = False) -> pd.DataFrame:
        """
        Fetch Daily OHLCV data.
        """
        if not is_overseas:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
            headers = self._get_headers(tr_id="FHKST03010100")
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": symbol,
                "fid_input_date_1": start_date,
                "fid_input_date_2": end_date,
                "fid_period_div_code": "D",
                "fid_org_adj_prc": "0"
            }
        else:
            url = f"{self.base_url}/uapi/overseas-stock/v1/quotations/dailyprice"
            headers = self._get_headers(tr_id="HHDFS76240000")
            params = {
                "AUTH": "",
                "EXCD": "NAS", # NAS for NASDAQ
                "SYMB": symbol,
                "GUBN": "0", # 0: Daily
                "BYMD": end_date,
                "MODP": "1" # Adjusted price
            }
        
        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
            data = res.json()
            if data["rt_cd"] != "0":
                raise Exception(data.get("msg1"))
            
            records = data.get("output2" if not is_overseas else "output", [])
            df = pd.DataFrame(records)
            
            if not is_overseas:
                df.rename(columns={
                    'stck_bsop_date': 'date',
                    'stck_oprc': 'open',
                    'stck_hgpr': 'high',
                    'stck_lwpr': 'low',
                    'stck_clpr': 'close',
                    'acml_vol': 'volume'
                }, inplace=True)
            else:
                # Overseas column names
                df.rename(columns={
                    'xymd': 'date',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'last': 'close',
                    'tvol': 'volume'
                }, inplace=True)
            
            df['date'] = pd.to_datetime(df['date'])
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise

    def place_market_order(self, symbol: str, side: str, qty: int, is_overseas: bool = False):
        """
        Place a market order.
        """
        if not is_overseas:
            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
            tr_id = ("VTTC0802U" if side == "buy" else "VTTC0801U") if self.mode == "mock" else ("TTTC0802U" if side == "buy" else "TTTC0801U")
            payload = {
                "CANO": self.cano,
                "ACNT_PRDT_CD": self.acnt_prdt_cd,
                "PDNO": symbol,
                "ORD_DVSN": "01",
                "ORD_QTY": str(qty),
                "ORD_UNPR": "0"
            }
        else:
            url = f"{self.base_url}/uapi/overseas-stock/v1/trading/order"
            tr_id = ("VTTT1002U" if side == "buy" else "VTTT1001U") if self.mode == "mock" else ("JTTT1002U" if side == "buy" else "JTTT1001U")
            payload = {
                "CANO": self.cano,
                "ACNT_PRDT_CD": self.acnt_prdt_cd,
                "OVRS_EXCG_CD": "NASD",
                "PDNO": symbol,
                "ORD_QTY": str(qty),
                "OVRS_ORD_UNPR": "0",
                "ORD_SVR_DVSN_CD": "0",
                "ORD_DVSN": "00" # 00: Market order for US
            }
            
        headers = self._get_headers(tr_id=tr_id)
        
        try:
            logger.info(f"Placing {side} {'overseas' if is_overseas else 'domestic'} market order for {qty} shares of {symbol}...")
            res = requests.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            if data["rt_cd"] != "0":
                raise Exception(data.get("msg1"))
            logger.info(f"Order successful. Data: {data['output']}")
            return data['output']
        except Exception as e:
            logger.error(f"Error placing {side} order for {symbol}: {e}")
            raise
