(() => {
  const tabs = document.querySelectorAll('.mobile-tabs button');
  const sections = ['chat-view', 'analytics-view', 'batch-view'].map(id => document.getElementById(id));

  function show(id) {
    if (window.innerWidth > 1024) return;
    sections.forEach(s => s.classList.toggle('hidden', s.id !== id));
  }

  tabs.forEach(btn => btn.addEventListener('click', () => show(btn.dataset.target)));
  show('chat-view');

  let touchStartY = 0;
  document.addEventListener('touchstart', e => { touchStartY = e.touches[0].clientY; }, { passive: true });
  document.addEventListener('touchend', e => {
    if (window.scrollY === 0 && e.changedTouches[0].clientY - touchStartY > 80) {
      location.reload();
    }
  }, { passive: true });

  function applySwipeNavigation(direction) {
    const visible = sections.findIndex(s => !s.classList.contains('hidden'));
    const next = direction === 'left' ? Math.min(visible + 1, sections.length - 1) : Math.max(visible - 1, 0);
    show(sections[next].id);
  }

  if (window.Hammer) {
    const hammer = new Hammer(document.body);
    hammer.get('swipe').set({ direction: Hammer.DIRECTION_HORIZONTAL, threshold: 25, velocity: 0.2 });
    hammer.on('swipeleft', () => { if (window.innerWidth <= 1024) applySwipeNavigation('left'); });
    hammer.on('swiperight', () => { if (window.innerWidth <= 1024) applySwipeNavigation('right'); });
  } else {
    let startX = 0;
    document.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
    document.addEventListener('touchend', e => {
      if (window.innerWidth > 1024) return;
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) < 70) return;
      applySwipeNavigation(dx < 0 ? 'left' : 'right');
    }, { passive: true });
  }
})();
