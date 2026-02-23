(() => {
  const key = 'liberation-theme';
  const toggle = document.getElementById('theme-toggle');
  const saved = localStorage.getItem(key) || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  toggle.checked = saved === 'light';
  toggle.addEventListener('change', () => {
    const theme = toggle.checked ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(key, theme);
  });
})();
