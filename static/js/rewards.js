/**
 * static/js/rewards.js
 * Daily Rewards page interactivity — Sprint 5
 *
 * Responsibilities:
 *  - Countdown timer (live, updates every second)
 *  - Claim button fetch → POST /api/rewards/claim
 *  - Reward animation (particle shower + card flash)
 *  - UI state transition: unclaimed → claimed without page reload
 *  - User-pill dropdown (shared with dashboard.js pattern)
 */

(function () {
  'use strict';

  /* ------------------------------------------------------------------ */
  /* Utilities                                                            */
  /* ------------------------------------------------------------------ */

  function formatTime(totalSeconds) {
    var s = Math.max(0, Math.floor(totalSeconds));
    var h = Math.floor(s / 3600);
    var m = Math.floor((s % 3600) / 60);
    var sec = s % 60;
    return (
      String(h).padStart(2, '0') + ':' +
      String(m).padStart(2, '0') + ':' +
      String(sec).padStart(2, '0')
    );
  }

  /* ------------------------------------------------------------------ */
  /* Countdown Timer                                                      */
  /* ------------------------------------------------------------------ */

  var countdownEl = document.getElementById('reward-countdown');
  var countdownInterval = null;

  function startCountdown(seconds) {
    if (!countdownEl) return;

    var remaining = seconds;
    countdownEl.textContent = formatTime(remaining);

    if (countdownInterval) clearInterval(countdownInterval);

    countdownInterval = setInterval(function () {
      remaining -= 1;
      if (remaining <= 0) {
        clearInterval(countdownInterval);
        countdownEl.textContent = '00:00:00';
        // Soft refresh so the claim button re-appears
        window.location.reload();
      } else {
        countdownEl.textContent = formatTime(remaining);
      }
    }, 1000);
  }

  // Start countdown if the timer element is present and visible
  if (countdownEl) {
    var initialSeconds = parseInt(countdownEl.getAttribute('data-seconds'), 10) || 0;
    startCountdown(initialSeconds);
  }


  /* ------------------------------------------------------------------ */
  /* Particle Shower Animation                                            */
  /* ------------------------------------------------------------------ */

  function launchParticles(rewardType) {
    var overlay = document.getElementById('reward-animation-overlay');
    if (!overlay) return;

    // Pick emoji based on reward type
    var emojis = {
      coins:       ['💰', '🪙', '✨', '⭐'],
      xp:          ['⚡', '✨', '💫', '⭐'],
      chest:       ['📦', '✨', '💎', '💰', '⚡'],
      xp_bonus:    ['🚀', '⚡', '✨', '💫'],
      avatar_item: ['🎁', '✨', '🌟', '💫'],
    };
    var pool = emojis[rewardType] || ['✨', '🌟', '💫'];

    var PARTICLE_COUNT = 28;

    for (var i = 0; i < PARTICLE_COUNT; i++) {
      (function (index) {
        setTimeout(function () {
          var particle = document.createElement('div');
          particle.className = 'reward-particle';
          particle.textContent = pool[Math.floor(Math.random() * pool.length)];
          particle.style.left = (5 + Math.random() * 90) + '%';
          particle.style.top = '-60px';
          particle.style.animationDuration = (0.9 + Math.random() * 0.8) + 's';
          particle.style.animationDelay = (Math.random() * 0.4) + 's';
          overlay.appendChild(particle);

          // Remove DOM node after animation finishes
          particle.addEventListener('animationend', function () {
            particle.remove();
          });
        }, index * 60);
      })(i);
    }
  }


  /* ------------------------------------------------------------------ */
  /* Claim Button                                                         */
  /* ------------------------------------------------------------------ */

  var btnClaim = document.getElementById('btn-claim');

  function transitionToClaimed(data) {
    // Flash card
    var card = document.getElementById('today-reward-card');
    if (card) {
      card.classList.add('claimed-flash');
      card.addEventListener('animationend', function () {
        card.classList.remove('claimed-flash');
      }, { once: true });
    }

    // Show particles
    launchParticles(data.reward_type);

    // Swap UI state: hide unclaimed, show claimed
    var unclaimedState = document.getElementById('reward-unclaimed-state');
    var claimedState   = document.getElementById('reward-claimed-state');
    if (unclaimedState) unclaimedState.style.display = 'none';
    if (claimedState)   claimedState.style.display = 'flex';

    // Start countdown from fresh seconds-until-midnight value
    // We calculate it client-side since we know the claim just happened.
    var now = new Date();
    var midnight = new Date(now);
    midnight.setHours(24, 0, 0, 0);
    var secondsLeft = Math.floor((midnight - now) / 1000);

    var cdEl = document.getElementById('reward-countdown');
    if (cdEl) {
      cdEl.setAttribute('data-seconds', secondsLeft);
      startCountdown(secondsLeft);
    }
  }

  if (btnClaim) {
    btnClaim.addEventListener('click', function () {
      var self = this;
      self.disabled = true;
      self.classList.add('loading');

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
            transitionToClaimed(result.data.data);
          } else {
            // Show error in a non-intrusive flash-style message
            showToast(result.data.message || 'Something went wrong.', 'error');
            self.disabled = false;
            self.classList.remove('loading');
          }
        })
        .catch(function () {
          showToast('Network error. Please try again.', 'error');
          self.disabled = false;
          self.classList.remove('loading');
        });
    });
  }


  /* ------------------------------------------------------------------ */
  /* Toast Notification Helper                                            */
  /* ------------------------------------------------------------------ */

  function showToast(message, type) {
    var container = document.getElementById('flash-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'flash-container';
      container.className = 'flash-container';
      container.setAttribute('role', 'alert');
      container.setAttribute('aria-live', 'polite');
      document.body.prepend(container);
    }

    var flash = document.createElement('div');
    flash.className = 'flash flash-' + (type || 'info');
    flash.style.display = 'flex';
    flash.style.justifyContent = 'space-between';
    flash.style.alignItems = 'center';
    flash.style.gap = '1rem';

    var icon = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
    var closeBtn = document.createElement('button');
    closeBtn.style.cssText = 'color:inherit;opacity:0.7;font-size:1.2rem;cursor:pointer;';
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', function () { flash.remove(); });

    var text = document.createElement('div');
    text.textContent = icon + ' ' + message;

    flash.appendChild(text);
    flash.appendChild(closeBtn);
    container.appendChild(flash);

    // Auto-dismiss after 8 s
    setTimeout(function () {
      flash.style.transition = 'opacity 0.4s ease';
      flash.style.opacity = '0';
      setTimeout(function () { flash.remove(); }, 400);
    }, 8000);
  }


  /* ------------------------------------------------------------------ */
  /* User Dropdown (shared pattern with dashboard.js)                    */
  /* ------------------------------------------------------------------ */

  var userPill = document.getElementById('user-pill');

  if (userPill) {
    userPill.addEventListener('click', function (e) {
      var isOpen = this.classList.toggle('open');
      this.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      e.stopPropagation();
    });

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

    document.addEventListener('click', function (e) {
      if (!userPill.contains(e.target)) {
        userPill.classList.remove('open');
        userPill.setAttribute('aria-expanded', 'false');
      }
    });
  }

})();
