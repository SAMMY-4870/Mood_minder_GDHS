// home.js

document.addEventListener('DOMContentLoaded', function () {
  console.log("Home page loaded");

  // Animate cards on scroll
  const cards = document.querySelectorAll('.card');
  const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
          if (entry.isIntersecting) {
              entry.target.classList.add('show');
          }
      });
  }, { threshold: 0.5 });

  cards.forEach(card => {
      observer.observe(card);
  });

  // Add click animation on buttons
  const buttons = document.querySelectorAll('.btn');
  buttons.forEach(btn => {
      btn.addEventListener('click', () => {
          btn.classList.add('clicked');
          setTimeout(() => btn.classList.remove('clicked'), 300);
      });
  });
});
