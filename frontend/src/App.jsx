import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ModeSelection from './pages/ModeSelection';
import Dashboard from './pages/Dashboard';
import { applyTheme } from './theme';
import ThemeSwitcher from './components/ThemeSwitcher';

function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<ModeSelection />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
      <ThemeSwitcher theme={theme} setTheme={setTheme} />
    </Router>
  );
}

export default App;
