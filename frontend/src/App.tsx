import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'settings'>('dashboard');

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="navbar-brand">Quant Trading Fleet</div>
        <div className="nav-links">
          <button 
            className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={`nav-link ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            Settings
          </button>
        </div>
      </nav>
      <main className="main-content">
        {activeTab === 'dashboard' ? <Dashboard /> : <Settings />}
      </main>
    </div>
  );
};

export default App;
