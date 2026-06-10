import React, { useState, useEffect } from 'react';

interface Setting {
  id: number;
  key: string;
  value: string;
  description: string;
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<Setting[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSettings = async () => {
    try {
      const res = await fetch('/api/settings/');
      const data = await res.json();
      setSettings(data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const updateSetting = async (key: string, value: string) => {
    try {
      await fetch(`/api/settings/${key}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value })
      });
      fetchSettings();
    } catch (error) {
      console.error('Error updating setting:', error);
    }
  };

  if (loading) return <div>Loading settings...</div>;

  return (
    <div className="card">
      <h2 className="card-title">Strategy & API Settings</h2>
      <div className="settings-list">
        {settings.map(s => (
          <div key={s.id} className="setting-item">
            <div className="setting-info">
              <label><strong>{s.key}</strong></label>
              <p className="setting-desc">{s.description}</p>
            </div>
            <div className="setting-input">
              <input 
                type="text" 
                defaultValue={s.value} 
                onBlur={(e) => updateSetting(s.key, e.target.value)}
              />
            </div>
          </div>
        ))}
      </div>
      <style>{`
        .settings-list { display: flex; flex-direction: column; gap: 0.85rem; }
        .setting-item {
          display: flex; justify-content: space-between; align-items: center; gap: 2rem;
          background: var(--card-bg-2); border: 1px solid var(--border-color);
          border-radius: 12px; padding: 1.1rem 1.25rem; transition: border-color 0.2s;
        }
        .setting-item:hover { border-color: var(--border-strong); }
        .setting-info { flex: 1; }
        .setting-info label strong { font-family: var(--mono); font-size: 0.9rem; color: var(--text-main); }
        .setting-desc { font-size: 0.82rem; color: var(--text-muted); margin-top: 0.3rem; }
        .setting-input input { width: 220px; text-align: right; font-family: var(--mono); }
      `}</style>
    </div>
  );
};

export default Settings;
