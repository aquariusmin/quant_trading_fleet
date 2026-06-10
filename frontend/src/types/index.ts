export interface BotStatus {
  id: number;
  name: string;
  symbol: string;
  broker_type: 'kis' | 'binance';
  is_overseas: boolean;
  is_running: boolean;
}

export interface TradeHistory {
  id: number;
  timestamp: string;
  bot_name: string;
  symbol: string;
  side: 'buy' | 'sell';
  price: number;
  qty: number;
  total_amount: number;
  broker_type: string;
}

export interface PortfolioSummary {
  kis_broker: {
    mode: string;
    balance_krw: string;
  };
  binance_broker: {
    mode: string;
    balance_usdt: string;
  };
}
