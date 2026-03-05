import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { applyTheme } from '../theme';

const ThemeSwitcher = ({ theme, setTheme }) => {
  const handleSwitch = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  return (
    <button
      className="btn-secondary"
      style={{ border: 'none', background: 'none', color: 'var(--accent-blue)', fontSize: '1.2rem', padding: '0.5rem' }}
      onClick={handleSwitch}
      title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
      <span style={{ marginLeft: 8 }}>{theme === 'dark' ? 'Light' : 'Dark'} Mode</span>
    </button>
  );
};

export default ThemeSwitcher;
