import React, { useState, useEffect } from 'react';
import { BotStatus, TradeHistory, PortfolioSummary } from '../types';

const Dashboard: React.FC = () => {
  const [bots, setBots] = useState<BotStatus[]>([]);
  const [trades, setTrades] = useState<TradeHistory[]>([]);
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [botsRes, tradesRes, portfolioRes] = await Promise.all([
        fetch('/api/bots/'),
        fetch('/api/portfolio/trades'),
        fetch('/api/portfolio/')
      ]);
      
      const botsData = await botsRes.json();
      const tradesData = await tradesRes.json();
      const portfolioData = await portfolioRes.json();

      setBots(botsData);
      setTrades(tradesData);
      setPortfolio(portfolioData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const toggleBot = async (name: string, isRunning: boolean) => {
    const action = isRunning ? 'stop' : 'start';
    try {
      const res = await fetch(`/api/bots/${name}/${action}`, { method: 'POST' });
      if (res.ok) {
        fetchData();
      }
    } catch (error) {
      console.error(`Error ${action}ing bot ${name}:`, error);
    }
  };

  if (loading && !portfolio) return <div className="loading">Loading dashboard...</div>;

  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        {/* Portfolio Section */}
        <section className="card portfolio-card">
          <h2 className="card-title">Portfolio Summary</h2>
          {portfolio && (
            <div className="portfolio-info">
              <div className="broker-item">
                <strong>KIS (Stock):</strong> {portfolio.kis_broker.balance_krw}
                <span className="mode-tag">{portfolio.kis_broker.mode}</span>
              </div>
              <div className="broker-item">
                <strong>Binance (Crypto):</strong> {portfolio.binance_broker.balance_usdt}
                <span className="mode-tag">{portfolio.binance_broker.mode}</span>
              </div>
            </div>
          )}
        </section>

        {/* Bot Controls Section */}
        <section className="card bots-card">
          <h2 className="card-title">Bot Control Panel</h2>
          <div className="bot-list">
            {bots.map(bot => (
              <div key={bot.id} className="bot-item card">
                <div className="bot-info">
                  <h3>{bot.name}</h3>
                  <p>{bot.symbol} ({bot.broker_type.toUpperCase()})</p>
                  <span className={`status-badge ${bot.is_running ? 'status-running' : 'status-stopped'}`}>
                    {bot.is_running ? 'RUNNING' : 'STOPPED'}
                  </span>
                </div>
                <div className="bot-actions">
                  <button 
                    className={bot.is_running ? 'btn-danger' : 'btn-success'}
                    onClick={() => toggleBot(bot.name, bot.is_running)}
                  >
                    {bot.is_running ? 'Stop Bot' : 'Start Bot'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Trade History Section */}
      <section className="card trade-history-card">
        <h2 className="card-title">Recent Trades</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Bot</th>
                <th>Symbol</th>
                <th>Side</th>
                <th>Price</th>
                <th>Qty</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {trades.map(trade => (
                <tr key={trade.id}>
                  <td>{new Date(trade.timestamp).toLocaleString()}</td>
                  <td>{trade.bot_name}</td>
                  <td>{trade.symbol}</td>
                  <td className={trade.side === 'buy' ? 'trade-buy' : 'trade-sell'}>
                    {trade.side.toUpperCase()}
                  </td>
                  <td>{trade.price.toLocaleString()}</td>
                  <td>{trade.qty}</td>
                  <td>{trade.total_amount.toLocaleString()}</td>
                </tr>
              ))}
              {trades.length === 0 && (
                <tr>
                  <td colSpan={7} style={{textAlign: 'center'}}>No trades recorded yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <style>{`
        .portfolio-info { display: flex; flex-direction: column; gap: 1rem; }
        .broker-item { display: flex; justify-content: space-between; align-items: center; }
        .mode-tag { font-size: 0.7rem; background: #eee; padding: 2px 6px; border-radius: 4px; }
        .bot-list { display: flex; flex-direction: column; gap: 1rem; }
        .bot-item { display: flex; justify-content: space-between; align-items: center; padding: 1rem; margin-bottom: 0; }
        .bot-info h3 { margin-bottom: 0.25rem; font-size: 1.1rem; }
        .bot-info p { color: #666; font-size: 0.9rem; margin-bottom: 0.5rem; }
        .table-container { overflow-x: auto; }
      `}</style>
    </div>
  );
};

export default Dashboard;
