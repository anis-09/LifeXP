/**
 * static/js/celebration.js
 * -------------------------
 * Achievement Unlock Celebration System — Sprint 4.3
 *
 * Reads a JSON achievement queue from the DOM, then displays a premium
 * animated modal for each unlocked achievement in sequence.
 *
 * Features:
 *  - Modal queue (handles multiple simultaneous unlocks)
 *  - Badge pop animation (CSS keyframe)
 *  - XP / Coin count-up ticker
 *  - Canvas confetti engine
 *  - Sound hook (future-ready, no-op if <audio> absent)
 *  - Respects prefers-reduced-motion
 *
 * Zero global variables. Self-contained IIFE.
 */

(function () {
  'use strict';

  /* ------------------------------------------------------------------ */
  /* Reduced-motion detection                                             */
  /* ------------------------------------------------------------------ */

  var prefersReducedMotion = window.matchMedia
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false;

  /* ------------------------------------------------------------------ */
  /* Read achievement queue from DOM                                      */
  /* ------------------------------------------------------------------ */

  var root = document.getElementById('celebration-root');
  if (!root) return;

  var rawData = root.getAttribute('data-achievements');
  if (!rawData) return;

  var queue;
  try {
    queue = JSON.parse(rawData);
  } catch (e) {
    return;
  }

  if (!Array.isArray(queue) || queue.length === 0) return;

  /* ------------------------------------------------------------------ */
  /* DOM references (built once, reused per show)                         */
  /* ------------------------------------------------------------------ */

  var backdrop   = document.getElementById('celebration-backdrop');
  var modal      = document.getElementById('celebration-modal');
  var badgeEl    = document.getElementById('cel-badge');
  var nameEl     = document.getElementById('cel-name');
  var tierTagEl  = document.getElementById('cel-tier-tag');
  var descEl     = document.getElementById('cel-description');
  var xpEl       = document.getElementById('cel-xp');
  var coinsEl    = document.getElementById('cel-coins');
  var xpRow      = document.getElementById('cel-xp-row');
  var coinsRow   = document.getElementById('cel-coins-row');
  var counterEl  = document.getElementById('cel-queue-counter');
  var continueBtn = document.getElementById('cel-continue');

  if (!backdrop || !modal || !continueBtn) return;

  var currentIndex = 0;

  /* ------------------------------------------------------------------ */
  /* Tier label map                                                        */
  /* ------------------------------------------------------------------ */

  var TIER_LABELS = {
    bronze:    '🥉 Bronze',
    silver:    '🥈 Silver',
    gold:      '🥇 Gold',
    platinum:  '💎 Platinum',
    diamond:   '💠 Diamond',
    legendary: '👑 Legendary',
  };

  /* ------------------------------------------------------------------ */
  /* Count-up animation                                                   */
  /* ------------------------------------------------------------------ */

  function animateCountUp(element, target, duration) {
    if (prefersReducedMotion || target === 0) {
      element.textContent = target;
      return;
    }
    var start     = null;
    var startVal  = 0;

    function step(timestamp) {
      if (!start) start = timestamp;
      var progress = Math.min((timestamp - start) / duration, 1);
      element.textContent = Math.floor(progress * (target - startVal) + startVal);
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        element.textContent = target;
      }
    }
    requestAnimationFrame(step);
  }

  /* ------------------------------------------------------------------ */
  /* Show one achievement                                                  */
  /* ------------------------------------------------------------------ */

  function showAchievement(ach, index, total) {
    var tier = (ach.badge_tier || 'bronze').toLowerCase();

    // Reset animation by cloning badge (re-trigger CSS animation)
    var newBadge = badgeEl.cloneNode(true);
    newBadge.textContent = ach.icon || '🏅';
    badgeEl.parentNode.replaceChild(newBadge, badgeEl);
    badgeEl = newBadge;

    // Set modal tier
    modal.setAttribute('data-tier', tier);

    // Populate content
    nameEl.textContent     = ach.name        || 'Achievement Unlocked';
    descEl.textContent     = ach.description || '';
    tierTagEl.textContent  = TIER_LABELS[tier] || tier;
    tierTagEl.className    = 'celebration-tier-tag tier-' + tier;

    // Rewards
    if (ach.xp_reward && ach.xp_reward > 0) {
      xpRow.style.display = '';
      animateCountUp(xpEl, ach.xp_reward, 800);
    } else {
      xpRow.style.display = 'none';
    }

    if (ach.coin_reward && ach.coin_reward > 0) {
      coinsRow.style.display = '';
      animateCountUp(coinsEl, ach.coin_reward, 800);
    } else {
      coinsRow.style.display = 'none';
    }

    // Queue counter
    if (total > 1) {
      counterEl.textContent = (index + 1) + ' of ' + total;
      counterEl.style.display = '';
    } else {
      counterEl.style.display = 'none';
    }

    // Continue button label
    continueBtn.textContent = (index + 1 < total) ? 'Next ›' : 'Awesome!';

    // Show backdrop
    backdrop.classList.remove('hidden');

    // Fire confetti (after short delay so modal renders first)
    if (!prefersReducedMotion) {
      setTimeout(fireConfetti, 500);
    }

    // Sound hook (no-op until audio assets are added)
    playSound(tier);
  }

  /* ------------------------------------------------------------------ */
  /* Continue / Dismiss                                                   */
  /* ------------------------------------------------------------------ */

  function nextOrDismiss() {
    currentIndex++;
    if (currentIndex < queue.length) {
      showAchievement(queue[currentIndex], currentIndex, queue.length);
    } else {
      dismiss();
    }
  }

  function dismiss() {
    backdrop.classList.add('hidden');
  }

  continueBtn.addEventListener('click', nextOrDismiss);

  // Close on backdrop click (outside modal)
  backdrop.addEventListener('click', function (e) {
    if (e.target === backdrop) nextOrDismiss();
  });

  // Keyboard: Enter / Space = continue, Escape = dismiss
  document.addEventListener('keydown', function (e) {
    if (backdrop.classList.contains('hidden')) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      nextOrDismiss();
    }
    if (e.key === 'Escape') {
      dismiss();
    }
  });

  /* ------------------------------------------------------------------ */
  /* Confetti Engine                                                       */
  /* ------------------------------------------------------------------ */

  var confettiCanvas = document.getElementById('celebration-confetti');
  var confettiCtx    = confettiCanvas ? confettiCanvas.getContext('2d') : null;
  var confettiParticles = [];
  var confettiRaf   = null;

  var CONFETTI_COLORS = [
    '#7c3aed', '#06b6d4', '#f59e0b',
    '#ec4899', '#10b981', '#f97316',
    '#fbbf24', '#a78bfa',
  ];

  function fireConfetti() {
    if (!confettiCtx) return;

    confettiCanvas.width  = window.innerWidth;
    confettiCanvas.height = window.innerHeight;

    confettiParticles = [];
    var count = 120;

    for (var i = 0; i < count; i++) {
      confettiParticles.push({
        x:       Math.random() * confettiCanvas.width,
        y:       -20 - Math.random() * 100,
        w:       Math.random() * 10 + 5,
        h:       Math.random() * 5 + 3,
        color:   CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)],
        vx:      (Math.random() - 0.5) * 4,
        vy:      Math.random() * 4 + 3,
        rot:     Math.random() * 360,
        rotV:    (Math.random() - 0.5) * 8,
        opacity: 1,
      });
    }

    if (confettiRaf) cancelAnimationFrame(confettiRaf);

    var startTime = null;
    var DURATION  = 3000;

    function drawConfetti(timestamp) {
      if (!startTime) startTime = timestamp;
      var elapsed = timestamp - startTime;
      var progress = Math.min(elapsed / DURATION, 1);

      confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);

      confettiParticles.forEach(function (p) {
        p.x   += p.vx;
        p.y   += p.vy;
        p.rot += p.rotV;
        p.vy  += 0.1; // gravity
        p.opacity = Math.max(0, 1 - progress * 1.5);

        confettiCtx.save();
        confettiCtx.globalAlpha = p.opacity;
        confettiCtx.translate(p.x, p.y);
        confettiCtx.rotate(p.rot * Math.PI / 180);
        confettiCtx.fillStyle = p.color;
        confettiCtx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
        confettiCtx.restore();
      });

      if (elapsed < DURATION) {
        confettiRaf = requestAnimationFrame(drawConfetti);
      } else {
        confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
      }
    }

    confettiRaf = requestAnimationFrame(drawConfetti);
  }

  /* ------------------------------------------------------------------ */
  /* Sound Hook (future-ready, no-op)                                     */
  /* ------------------------------------------------------------------ */

  function playSound(tier) {
    var audioEl = document.getElementById('cel-audio-' + tier)
                  || document.getElementById('cel-audio-default');
    if (!audioEl) return;
    try {
      audioEl.currentTime = 0;
      audioEl.play();
    } catch (e) {
      // Autoplay blocked or file missing — silently ignore
    }
  }

  /* ------------------------------------------------------------------ */
  /* Kick off                                                             */
  /* ------------------------------------------------------------------ */

  showAchievement(queue[0], 0, queue.length);

})();
