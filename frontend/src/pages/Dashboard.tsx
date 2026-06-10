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
    <div className="dashboard-container">
      <header className="page-header">
        <h1 className="page-title">Market Overview</h1>
        <p style={{color: 'var(--text-muted)'}}>Real-time monitoring and execution dashboard</p>
      </header>

      <div className="dashboard-grid">
        {/* Portfolio Stats */}
        <section className="card portfolio-card">
          <h2 className="card-title">
            <span className="icon">📊</span> Wallet Balances
          </h2>
          {portfolio && (
            <div className="portfolio-stats">
              <div className="stat-item">
                <span className="stat-label">KIS Domestic</span>
                <div className="stat-value">
                  {portfolio.kis_broker.balance_krw} 
                  <span className="currency">KRW</span>
                </div>
                <div className={`mode-badge ${portfolio.kis_broker.mode}`}>{portfolio.kis_broker.mode}</div>
              </div>
              <div className="stat-item divider"></div>
              <div className="stat-item">
                <span className="stat-label">Binance Futures</span>
                <div className="stat-value">
                  {portfolio.binance_broker.balance_usdt} 
                  <span className="currency">USDT</span>
                </div>
                <div className={`mode-badge ${portfolio.binance_broker.mode}`}>{portfolio.binance_broker.mode}</div>
              </div>
            </div>
          )}
        </section>

        {/* Bot Controls */}
        <section className="card bots-card">
          <h2 className="card-title">
            <span className="icon">🤖</span> Active Fleet
          </h2>
          <div className="bot-grid">
            {bots.map(bot => (
              <div key={bot.id} className="bot-card-inner">
                <div className="bot-meta">
                  <div className="bot-main-info">
                    <span className="bot-name">{bot.name.replace(/_/g, ' ')}</span>
                    <span className="bot-symbol">{bot.symbol}</span>
                  </div>
                  <span className={`status-badge ${bot.is_running ? 'status-running' : 'status-stopped'}`}>
                    {bot.is_running ? 'Active' : 'Idle'}
                  </span>
                </div>
                <button 
                  className={bot.is_running ? 'btn-danger full-width' : 'btn-success full-width'}
                  onClick={() => toggleBot(bot.name, bot.is_running)}
                >
                  {bot.is_running ? 'Deactivate' : 'Launch Bot'}
                </button>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Trade History */}
      <section className="card trade-history-card" style={{marginTop: '2rem'}}>
        <h2 className="card-title">
          <span className="icon">📝</span> Recent Executions
        </h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Source</th>
                <th>Asset</th>
                <th>Side</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Notional</th>
              </tr>
            </thead>
            <tbody>
              {trades.map(trade => (
                <tr key={trade.id}>
                  <td className="timestamp-cell">
                    {new Date(trade.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    <span className="date-sub">{new Date(trade.timestamp).toLocaleDateString()}</span>
                  </td>
                  <td><span className={`broker-tag ${trade.broker_type}`}>{trade.broker_type}</span></td>
                  <td className="symbol-cell">{trade.symbol}</td>
                  <td>
                    <span className={`side-badge ${trade.side}`}>
                      {trade.side}
                    </span>
                  </td>
                  <td className="price-cell">{trade.price.toLocaleString()}</td>
                  <td>{trade.qty}</td>
                  <td className="total-cell">{trade.total_amount.toLocaleString()}</td>
                </tr>
              ))}
              {trades.length === 0 && (
                <tr>
                  <td colSpan={7} className="empty-state">No execution data available.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <style>{`
        .dashboard-container { animation: fadeIn 0.5s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .portfolio-stats { display: flex; align-items: center; justify-content: space-around; padding: 1rem 0; }
        .stat-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 0.55rem; }
        .stat-item.divider { flex: 0; width: 1px; height: 64px; background: var(--border-color); }
        .stat-label { font-size: 0.72rem; color: var(--text-faint); font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
        .stat-value { font-size: 1.7rem; font-weight: 800; color: var(--text-main); display: flex; align-items: baseline; gap: 0.3rem; font-family: var(--mono); }
        .stat-value .currency { font-size: 0.8rem; font-weight: 500; color: var(--text-muted); }

        .mode-badge { font-size: 0.62rem; font-weight: 700; padding: 3px 9px; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em; }
        .mode-badge.mock, .mode-badge.testnet { background: var(--warning-soft); color: var(--warning-color); border: 1px solid rgba(245,176,66,0.3); }
        .mode-badge.real { background: var(--success-soft); color: var(--success-color); border: 1px solid rgba(46,204,143,0.3); }

        .bot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.9rem; }
        .bot-card-inner { background: var(--card-bg-2); padding: 1.1rem; border-radius: 12px; border: 1px solid var(--border-color); transition: border-color 0.2s, transform 0.2s; }
        .bot-card-inner:hover { border-color: var(--border-strong); transform: translateY(-2px); }
        .bot-meta { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.1rem; }
        .bot-main-info { display: flex; flex-direction: column; gap: 0.15rem; }
        .bot-name { font-weight: 700; font-size: 0.9rem; text-transform: capitalize; color: var(--text-main); }
        .bot-symbol { font-size: 0.74rem; color: var(--text-muted); font-weight: 500; font-family: var(--mono); }
        .full-width { width: 100%; }

        .timestamp-cell { display: flex; flex-direction: column; line-height: 1.2; font-family: var(--mono); }
        .date-sub { font-size: 0.68rem; color: var(--text-faint); }
        .symbol-cell { font-weight: 700; color: var(--text-main); }
        .price-cell, .total-cell { font-family: var(--mono); font-weight: 500; text-align: right; }

        .broker-tag { font-size: 0.66rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.04em; }
        .broker-tag.kis { background: rgba(91,140,255,0.14); color: #8db0ff; }
        .broker-tag.binance { background: var(--warning-soft); color: var(--warning-color); }

        .side-badge { font-size: 0.66rem; font-weight: 800; padding: 3px 10px; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em; }
        .side-badge.buy { background: var(--success-soft); color: var(--success-color); border: 1px solid rgba(46,204,143,0.35); }
        .side-badge.sell { background: var(--danger-soft); color: var(--danger-color); border: 1px solid rgba(255,93,108,0.35); }

        .empty-state { text-align: center; padding: 3rem !important; color: var(--text-faint); font-style: italic; }
      `}</style>
    </div>
  );
};

export default Dashboard;
