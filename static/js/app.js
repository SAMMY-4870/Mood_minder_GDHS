// Small client-side helpers
document.addEventListener('DOMContentLoaded', () => {
  // Smooth scroll for internal anchors
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id.length > 1 && document.querySelector(id)) {
        e.preventDefault();
        document.querySelector(id).scrollIntoView({behavior: 'smooth'});
      }
    });
  });

  // Reveal on scroll
  const onScroll = () => {
    document.querySelectorAll('.reveal').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight - 80) {
        el.classList.add('visible');
      }
    });
  };
  window.addEventListener('scroll', onScroll);
  onScroll();

  // Button ripple
  document.querySelectorAll('button, .btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      const circle = document.createElement('span');
      circle.className = 'ripple';
      const size = Math.max(this.clientWidth, this.clientHeight);
      circle.style.width = circle.style.height = size + 'px';
      const rect = this.getBoundingClientRect();
      circle.style.left = (e.clientX - rect.left - size / 2) + 'px';
      circle.style.top = (e.clientY - rect.top - size / 2) + 'px';
      this.appendChild(circle);
      setTimeout(() => circle.remove(), 600);
    });
  });
});


