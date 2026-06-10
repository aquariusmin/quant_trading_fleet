# Quant Trading Fleet 🚀

A professional-grade, multi-market automated trading fleet. Supports KOSPI, US Stocks, and Crypto using various quantitative strategies.

## Features
- **Multi-Market**: Integrated with Korea Investment & Securities (KIS) for Domestic/US stocks and CCXT for Crypto.
- **Strategies**: 
  - Short-Term Volatility Breakout (Intraday)
  - Long-Term Dual Momentum (Rebalancing)
- **Production Ready**: Built with Docker Compose, Pydantic configuration, and rotating loggers.
- **Environment Modes**: Easy toggle between `mock/testnet` and `real` money.

## Quick Start

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Fill in your API keys in .env
   ```

2. **Launch with Docker**:
   ```bash
   docker-compose up -d
   ```

3. **Monitor Logs**:
   ```bash
   tail -f logs/quant_fleet.log
   ```

## Architecture
- `brokers/`: API wrappers for KIS and Binance.
- `strategies/`: Core quantitative logic.
- `core/`: Logging and base utilities.
- `config/`: Environment and settings management.

## Disclaimer
Trading involves significant risk. This software is for educational purposes. Use it at your own risk.
