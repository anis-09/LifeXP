/**
 * static/js/auth.js
 * Client-side form validation for Register and Login pages.
 * Enhances user experience before server-side validation runs.
 *
 * Features:
 *  - Real-time field validation with visual feedback
 *  - Password strength meter (register only)
 *  - Password visibility toggle
 *  - Form submit loading state
 *  - Matches server-side password rules
 */

(function () {
  'use strict';

  /* ------------------------------------------------------------------ */
  /* Utility Helpers                                                      */
  /* ------------------------------------------------------------------ */

  /**
   * Set input validation state and hint text.
   * @param {HTMLInputElement} input
   * @param {'valid'|'invalid'|''} state
   * @param {string} message
   * @param {string} hintId
   */
  function setFieldState(input, state, message, hintId) {
    input.classList.remove('is-valid', 'is-invalid');
    var hint = document.getElementById(hintId);

    if (state === 'valid') {
      input.classList.add('is-valid');
      if (hint) {
        hint.textContent = message;
        hint.className = 'form-hint success';
      }
    } else if (state === 'invalid') {
      input.classList.add('is-invalid');
      if (hint) {
        hint.textContent = message;
        hint.className = 'form-hint error';
      }
    } else {
      if (hint) {
        hint.textContent = message;
        hint.className = 'form-hint';
      }
    }
  }

  /**
   * Validate email format.
   * @param {string} email
   * @returns {boolean}
   */
  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.trim());
  }

  /**
   * Evaluate password strength.
   * Returns { score: 0-4, label: string }
   */
  function getPasswordStrength(password) {
    var score = 0;
    if (password.length >= 8)                         score++;
    if (/[A-Z]/.test(password))                       score++;
    if (/[a-z]/.test(password) && /\d/.test(password)) score++;
    if (/[!@#$%^&*(),.?":{}|<>_\-]/.test(password))   score++;

    var labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
    return { score: score, label: labels[score] || '' };
  }

  /* ------------------------------------------------------------------ */
  /* Password Visibility Toggle                                           */
  /* ------------------------------------------------------------------ */

  function initPasswordToggle(toggleId, inputId) {
    var toggle = document.getElementById(toggleId);
    var input  = document.getElementById(inputId);
    if (!toggle || !input) return;

    toggle.addEventListener('click', function () {
      var isShowing = input.type === 'text';
      input.type = isShowing ? 'password' : 'text';
      toggle.textContent = isShowing ? '👁️' : '🙈';
      toggle.setAttribute('aria-pressed', (!isShowing).toString());
    });
  }

  initPasswordToggle('toggle-password', 'password');
  initPasswordToggle('toggle-confirm',  'confirm_password');


  /* ------------------------------------------------------------------ */
  /* Password Strength Meter (Register Page Only)                         */
  /* ------------------------------------------------------------------ */

  var passwordInput = document.getElementById('password');
  var strengthContainer = document.getElementById('password-strength');
  var strengthLabel = document.getElementById('strength-label');
  var ariaStrength  = document.getElementById('password_strength_label');

  if (passwordInput && strengthContainer) {
    var bars = [
      document.getElementById('bar-1'),
      document.getElementById('bar-2'),
      document.getElementById('bar-3'),
      document.getElementById('bar-4'),
    ];

    var classMap = { 1: 'weak', 2: 'fair', 3: 'good', 4: 'strong' };

    function updateStrengthMeter(password) {
      var result = getPasswordStrength(password);
      var score  = result.score;

      bars.forEach(function (bar, idx) {
        bar.className = 'strength-bar';
        if (idx < score && classMap[score]) {
          bar.classList.add(classMap[score]);
        }
      });

      if (strengthLabel) strengthLabel.textContent = result.label;
      if (ariaStrength)  ariaStrength.textContent  = 'Password strength: ' + result.label;
    }

    passwordInput.addEventListener('input', function () {
      updateStrengthMeter(this.value);
    });
  }


  /* ------------------------------------------------------------------ */
  /* Register Form Validation                                             */
  /* ------------------------------------------------------------------ */

  var registerForm = document.getElementById('register-form');

  if (registerForm) {
    var nameInput    = document.getElementById('full_name');
    var emailInput   = document.getElementById('email');
    var confirmInput = document.getElementById('confirm_password');

    // Live: Full name
    if (nameInput) {
      nameInput.addEventListener('blur', function () {
        var val = this.value.trim();
        if (!val) {
          setFieldState(this, 'invalid', 'Full name is required.', 'full_name_hint');
        } else if (val.length < 2) {
          setFieldState(this, 'invalid', 'Name must be at least 2 characters.', 'full_name_hint');
        } else {
          setFieldState(this, 'valid', '✓ Looks good!', 'full_name_hint');
        }
      });
    }

    // Live: Email
    if (emailInput) {
      emailInput.addEventListener('blur', function () {
        var val = this.value.trim();
        if (!val) {
          setFieldState(this, 'invalid', 'Email address is required.', 'email_hint');
        } else if (!isValidEmail(val)) {
          setFieldState(this, 'invalid', 'Please enter a valid email address.', 'email_hint');
        } else {
          setFieldState(this, 'valid', '✓ Valid email', 'email_hint');
        }
      });
    }

    // Live: Password
    if (passwordInput) {
      passwordInput.addEventListener('blur', function () {
        var val = this.value;
        if (!val) {
          setFieldState(this, 'invalid', 'Password is required.', 'password_hint');
        } else if (val.length < 8) {
          setFieldState(this, 'invalid', 'At least 8 characters required.', 'password_hint');
        } else if (!/[A-Z]/.test(val)) {
          setFieldState(this, 'invalid', 'Add at least one uppercase letter.', 'password_hint');
        } else if (!/[a-z]/.test(val)) {
          setFieldState(this, 'invalid', 'Add at least one lowercase letter.', 'password_hint');
        } else if (!/\d/.test(val)) {
          setFieldState(this, 'invalid', 'Add at least one number.', 'password_hint');
        } else if (!/[!@#$%^&*(),.?":{}|<>_\-]/.test(val)) {
          setFieldState(this, 'invalid', 'Add at least one special character.', 'password_hint');
        } else {
          setFieldState(this, 'valid', '✓ Strong password!', 'password_hint');
        }
      });
    }

    // Live: Confirm password
    if (confirmInput) {
      confirmInput.addEventListener('blur', function () {
        var password = passwordInput ? passwordInput.value : '';
        if (!this.value) {
          setFieldState(this, 'invalid', 'Please confirm your password.', 'confirm_hint');
        } else if (this.value !== password) {
          setFieldState(this, 'invalid', 'Passwords do not match.', 'confirm_hint');
        } else {
          setFieldState(this, 'valid', '✓ Passwords match!', 'confirm_hint');
        }
      });
    }

    // Submit validation
    registerForm.addEventListener('submit', function (e) {
      var valid = true;

      if (!nameInput.value.trim() || nameInput.value.trim().length < 2) {
        setFieldState(nameInput, 'invalid', 'Full name is required (min 2 chars).', 'full_name_hint');
        valid = false;
      }

      if (!isValidEmail(emailInput.value)) {
        setFieldState(emailInput, 'invalid', 'Enter a valid email address.', 'email_hint');
        valid = false;
      }

      var pwd = passwordInput.value;
      if (!pwd || pwd.length < 8 ||
          !/[A-Z]/.test(pwd) || !/[a-z]/.test(pwd) ||
          !/\d/.test(pwd) || !/[!@#$%^&*(),.?":{}|<>_\-]/.test(pwd)) {
        setFieldState(passwordInput, 'invalid', 'Password does not meet requirements.', 'password_hint');
        valid = false;
      }

      if (confirmInput.value !== pwd) {
        setFieldState(confirmInput, 'invalid', 'Passwords do not match.', 'confirm_hint');
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
        return;
      }

      // Show loading state
      var btn = document.getElementById('register-submit');
      if (btn) {
        btn.classList.add('loading');
        btn.disabled = true;
      }
    });
  }


  /* ------------------------------------------------------------------ */
  /* Login Form Validation                                                */
  /* ------------------------------------------------------------------ */

  var loginForm = document.getElementById('login-form');

  if (loginForm) {
    var loginEmail    = document.getElementById('email');
    var loginPassword = document.getElementById('password');

    // Live: email
    if (loginEmail) {
      loginEmail.addEventListener('blur', function () {
        if (!this.value.trim()) {
          setFieldState(this, 'invalid', 'Email is required.', 'email_hint');
        } else if (!isValidEmail(this.value)) {
          setFieldState(this, 'invalid', 'Enter a valid email address.', 'email_hint');
        } else {
          setFieldState(this, 'valid', '', 'email_hint');
        }
      });
    }

    // Submit
    loginForm.addEventListener('submit', function (e) {
      var valid = true;

      if (!loginEmail.value.trim() || !isValidEmail(loginEmail.value)) {
        setFieldState(loginEmail, 'invalid', 'Enter a valid email address.', 'email_hint');
        valid = false;
      }

      if (!loginPassword.value) {
        loginPassword.classList.add('is-invalid');
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
        return;
      }

      // Show loading state
      var btn = document.getElementById('login-submit');
      if (btn) {
        btn.classList.add('loading');
        btn.disabled = true;
      }
    });
  }

})();
