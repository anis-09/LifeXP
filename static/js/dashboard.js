/**
 * static/js/dashboard.js
 * Dashboard page interactivity:
 *  - XP progress bar animated fill on load
 *  - User dropdown toggle
 *  - Stat card number count-up animation
 *  - Particle canvas background
 */

(function () {
  'use strict';

  /* ------------------------------------------------------------------ */
  /* XP Bar Animated Fill                                                 */
  /* ------------------------------------------------------------------ */

  function initXpBar() {
    var bar = document.getElementById('xp-bar');
    if (!bar) return;

    var targetWidth = parseInt(bar.getAttribute('data-width'), 10) || 0;

    // Delay slightly so user sees the animation
    setTimeout(function () {
      bar.style.transition = 'width 1.2s cubic-bezier(0.22, 1, 0.36, 1)';
      bar.style.width = targetWidth + '%';
    }, 400);
  }

  initXpBar();

  function initAchievementProgressBars() {
    var bars = document.querySelectorAll('.achievement-progress-fill[data-progress]');

    bars.forEach(function (bar) {
      var progress = Math.max(0, Math.min(100, parseFloat(bar.getAttribute('data-progress')) || 0));

      requestAnimationFrame(function () {
        bar.style.width = progress + '%';
      });
    });
  }

  initAchievementProgressBars();


  /* ------------------------------------------------------------------ */
  /* User Dropdown Toggle                                                 */
  /* ------------------------------------------------------------------ */

  var userPill = document.getElementById('user-pill');

  if (userPill) {
    // Click toggle
    userPill.addEventListener('click', function (e) {
      var isOpen = this.classList.toggle('open');
      this.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      e.stopPropagation();
    });

    // Keyboard accessibility
    userPill.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        var isOpen = this.classList.toggle('open');
        this.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      }
      if (e.key === 'Escape') {
        this.classList.remove('open');
        this.setAttribute('aria-expanded', 'false');
      }
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!userPill.contains(e.target)) {
        userPill.classList.remove('open');
        userPill.setAttribute('aria-expanded', 'false');
      }
    });
  }


  /* ------------------------------------------------------------------ */
  /* Stat Card Count-Up Animation                                         */
  /* ------------------------------------------------------------------ */

  function animateCountUp(element, endValue, duration) {
    var startTime = null;
    var start = 0;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var progress = Math.min((timestamp - startTime) / duration, 1);
      var current  = Math.floor(progress * endValue);
      element.textContent = current;

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        element.textContent = endValue;
      }
    }

    requestAnimationFrame(step);
  }

  // Animate all stat values with data-count attribute
  var statValues = document.querySelectorAll('.stat-card-value');
  statValues.forEach(function (el) {
    var numericValue = parseInt(el.textContent.trim(), 10);
    if (!isNaN(numericValue) && numericValue > 0) {
      el.textContent = '0';
      setTimeout(function () {
        animateCountUp(el, numericValue, 800);
      }, 300);
    }
  });


  /* ------------------------------------------------------------------ */
  /* Avatar Ring Rotation (CSS handles it, but pause on hover)            */
  /* ------------------------------------------------------------------ */

  var ring = document.querySelector('.profile-avatar-ring');
  var ringInner = document.querySelector('.profile-avatar-ring-inner');

  if (ring) {
    var wrapper = document.querySelector('.profile-avatar-wrapper');
    if (wrapper) {
      wrapper.addEventListener('mouseenter', function () {
        ring.style.animationPlayState = 'paused';
      });
      wrapper.addEventListener('mouseleave', function () {
        ring.style.animationPlayState = 'running';
      });
    }
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

  var PARTICLE_COUNT = 40;
  var particles = [];

  var COLORS = [
    'rgba(124, 58, 237, ',
    'rgba(6, 182, 212, ',
    'rgba(245, 158, 11, ',
  ];

  function createParticle() {
    return {
      x:       Math.random() * canvas.width,
      y:       Math.random() * canvas.height,
      radius:  Math.random() * 1.2 + 0.2,
      color:   COLORS[Math.floor(Math.random() * COLORS.length)],
      opacity: Math.random() * 0.4 + 0.1,
      dx:      (Math.random() - 0.5) * 0.3,
      dy:     -(Math.random() * 0.4 + 0.1),
    };
  }

  for (var i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(createParticle());
  }

  function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(function (p) {
      p.x += p.dx;
      p.y += p.dy;

      if (p.y < -10)               p.y = canvas.height + 10;
      if (p.x < -10)               p.x = canvas.width  + 10;
      if (p.x > canvas.width + 10) p.x = -10;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color + p.opacity + ')';
      ctx.fill();
    });

    requestAnimationFrame(animateParticles);
  }

  animateParticles();

  /* ------------------------------------------------------------------ */
  /* Dashboard — Daily Reward Claim Button                                */
  /* ------------------------------------------------------------------ */

  var btnDashClaim = document.getElementById('btn-dash-claim');

  if (btnDashClaim) {
    btnDashClaim.addEventListener('click', function () {
      var self = this;
      self.disabled = true;
      self.textContent = '⏳ Claiming…';

      fetch('/api/rewards/claim', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        },
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok, data: data };
          });
        })
        .then(function (result) {
          if (result.ok && result.data.success) {
            // Redirect to the full rewards page so user sees the animation
            window.location.href = '/rewards';
          } else {
            self.disabled = false;
            self.textContent = '🎁 Claim!';
            // Surface error via flash container
            var msg = result.data.message || 'Could not claim reward.';
            var fc = document.getElementById('flash-container');
            if (!fc) {
              fc = document.createElement('div');
              fc.id = 'flash-container';
              fc.className = 'flash-container';
              document.body.prepend(fc);
            }
            var flash = document.createElement('div');
            flash.className = 'flash flash-error';
            flash.style.cssText = 'display:flex;justify-content:space-between;align-items:center;gap:1rem;';
            flash.innerHTML = '<div>❌ ' + msg + '</div><button onclick="this.parentElement.remove()" style="opacity:0.7;font-size:1.2rem;cursor:pointer;">&times;</button>';
            fc.appendChild(flash);
          }
        })
        .catch(function () {
          self.disabled = false;
          self.textContent = '🎁 Claim!';
        });
    });
  }

})();
