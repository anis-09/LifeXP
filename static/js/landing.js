/**
 * static/js/landing.js
 * Landing page interactivity:
 *  - Navbar scroll behaviour (background on scroll)
 *  - Mobile hamburger menu toggle
 *  - Smooth scroll to anchor sections
 *  - Intersection Observer scroll-reveal animations
 *  - Particle canvas background
 */

(function () {
  'use strict';

  /* ------------------------------------------------------------------ */
  /* Navbar Scroll Behaviour                                              */
  /* ------------------------------------------------------------------ */

  var navbar = document.getElementById('navbar');

  function handleNavbarScroll() {
    if (window.scrollY > 20) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }

  window.addEventListener('scroll', handleNavbarScroll, { passive: true });
  handleNavbarScroll(); // Run once on load


  /* ------------------------------------------------------------------ */
  /* Mobile Hamburger Menu                                                */
  /* ------------------------------------------------------------------ */

  var toggleBtn = document.getElementById('navbar-toggle');
  var navLinks  = document.getElementById('navbar-links');

  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', function () {
      var isOpen = navLinks.classList.toggle('open');
      toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close menu when a link is clicked
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
        toggleBtn.setAttribute('aria-expanded', 'false');
      });
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!navbar.contains(e.target)) {
        navLinks.classList.remove('open');
        toggleBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }


  /* ------------------------------------------------------------------ */
  /* Smooth Scroll for Anchor Links                                       */
  /* ------------------------------------------------------------------ */

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var targetId = this.getAttribute('href');
      if (targetId === '#') return;

      var target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        var navbarHeight = navbar ? navbar.offsetHeight : 72;
        var targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navbarHeight;
        window.scrollTo({ top: targetPosition, behavior: 'smooth' });
      }
    });
  });


  /* ------------------------------------------------------------------ */
  /* Scroll Reveal — Intersection Observer                               */
  /* ------------------------------------------------------------------ */

  var revealSelectors = '.reveal, .reveal-left, .reveal-right';
  var revealElements  = document.querySelectorAll(revealSelectors);

  if ('IntersectionObserver' in window && revealElements.length > 0) {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            revealObserver.unobserve(entry.target); // Fire once
          }
        });
      },
      { threshold: 0.12 }
    );

    revealElements.forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    // Fallback: just show everything
    revealElements.forEach(function (el) {
      el.classList.add('visible');
    });
  }


  /* ------------------------------------------------------------------ */
  /* Particle Canvas Background                                           */
  /* ------------------------------------------------------------------ */

  var canvas = document.createElement('canvas');
  canvas.id = 'particle-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  document.body.insertBefore(canvas, document.body.firstChild);

  var ctx = canvas.getContext('2d');

  function resizeCanvas() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  resizeCanvas();
  window.addEventListener('resize', resizeCanvas, { passive: true });

  // Particle configuration
  var PARTICLE_COUNT = 60;
  var particles = [];

  var COLORS = [
    'rgba(124, 58, 237, ',   // purple
    'rgba(6, 182, 212, ',    // cyan
    'rgba(245, 158, 11, ',   // gold
  ];

  function createParticle() {
    return {
      x:       Math.random() * canvas.width,
      y:       Math.random() * canvas.height,
      radius:  Math.random() * 1.5 + 0.3,
      color:   COLORS[Math.floor(Math.random() * COLORS.length)],
      speed:   Math.random() * 0.3 + 0.1,
      opacity: Math.random() * 0.5 + 0.1,
      dx:      (Math.random() - 0.5) * 0.4,
      dy:     -(Math.random() * 0.5 + 0.2),
    };
  }

  for (var i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(createParticle());
  }

  function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(function (p) {
      // Update position
      p.x += p.dx;
      p.y += p.dy;

      // Wrap around edges
      if (p.y < -10)            p.y = canvas.height + 10;
      if (p.x < -10)            p.x = canvas.width  + 10;
      if (p.x > canvas.width  + 10) p.x = -10;

      // Draw
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color + p.opacity + ')';
      ctx.fill();
    });

    requestAnimationFrame(animateParticles);
  }

  animateParticles();

})();
