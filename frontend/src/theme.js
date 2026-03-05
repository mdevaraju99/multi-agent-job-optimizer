export const themes = {
  dark: {
    '--bg-dark': '#0f172a',
    '--bg-card': '#1e293b',
    '--bg-card-hover': '#334155',
    '--text-primary': '#f8fafc',
    '--text-secondary': '#94a3b8',
    '--accent-blue': '#3b82f6',
    '--accent-cyan': '#06b6d4',
    '--status-success': '#22c55e',
    '--status-warning': '#eab308',
    '--status-error': '#ef4444',
    '--border-color': '#334155',
  },
  light: {
    '--bg-dark': '#f8fafc',
    '--bg-card': '#ffffff',
    '--bg-card-hover': '#e2e8f0',
    '--text-primary': '#0f172a',
    '--text-secondary': '#64748b',
    '--accent-blue': '#2563eb',
    '--accent-cyan': '#0ea5e9',
    '--status-success': '#16a34a',
    '--status-warning': '#eab308',
    '--status-error': '#dc2626',
    '--border-color': '#cbd5e1',
  }
};

export function applyTheme(theme) {
  const themeVars = themes[theme];
  if (!themeVars) return;
  Object.entries(themeVars).forEach(([key, value]) => {
    document.documentElement.style.setProperty(key, value);
  });
}
