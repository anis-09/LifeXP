# LifeXP Security Guidelines

Version: 1.0

---

# Purpose

This document defines the security standards for the LifeXP application.

Every module must follow these rules to protect user data, prevent common attacks, and maintain application integrity.

Security is a core feature, not an afterthought.

---

# Security Principles

- Security by Design
- Least Privilege
- Defense in Depth
- Never Trust User Input
- Fail Securely

---

# Authentication

Passwords must never be stored in plain text.

Always hash passwords using Werkzeug's password hashing.

Example

generate_password_hash()

check_password_hash()

Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Special character recommended

---

# Session Security

- Secure server-side sessions
- Automatic session expiration
- Logout destroys session
- Regenerate session after login

Never store passwords in sessions.

---

# Authorization

Every protected page must verify authentication.

Users must only access their own data.

Never trust user_id received from the frontend.

Always use the logged-in session user.

---

# Input Validation

Validate every input.

Examples

Email

- Required
- Valid format

Mission Title

- Required
- Maximum 100 characters

Description

- Maximum 500 characters

Reject invalid requests before database operations.

---

# SQL Injection Protection

Always use parameterized queries.

Correct

cursor.execute(
"SELECT * FROM users WHERE email=?",
(email,)
)

Never build SQL using string concatenation.

---

# XSS Protection

Escape all user-generated content before rendering.

Never render raw HTML unless absolutely necessary.

Use Jinja2 auto escaping.

---

# CSRF Protection

Enable CSRF protection for all forms.

Every POST request must include a CSRF token.

---

# File Upload Security

Only allow approved file types.

Allowed

- PNG
- JPG
- JPEG
- WEBP

Maximum Size

5 MB

Rename uploaded files.

Never trust original filenames.

Store uploads outside executable directories when possible.

---

# Environment Variables

Never hardcode secrets.

Store

- SECRET_KEY
- API Keys
- Database URLs
- SMTP Credentials

Inside

.env

Never commit .env to Git.

---

# Error Handling

Show friendly messages to users.

Log technical details internally.

Bad

Database connection failed at line 245.

Good

Something went wrong. Please try again.

---

# Logging

Log

- Login attempts
- Failed logins
- Password changes
- Mission completion
- Reward claims
- Security events

Never log

- Passwords
- Session IDs
- Secret Keys

---

# Rate Limiting

Protect

- Login
- Registration
- Password Reset
- Public APIs

Future

Use Flask-Limiter.

---

# HTTPS

Production must always use HTTPS.

Never send authentication over HTTP.

---

# Cookies

Use

- Secure
- HttpOnly
- SameSite=Lax

Prevent client-side access whenever possible.

---

# API Security

Validate every request.

Return proper HTTP status codes.

Never expose internal stack traces.

Use authentication for protected endpoints.

---

# Database Security

Use parameterized queries.

Limit database permissions.

Backup database regularly.

Never expose database files publicly.

---

# Dependency Management

Install packages only from trusted sources.

Regularly update dependencies.

Remove unused packages.

---

# Backup Strategy

Daily database backup.

Weekly full project backup.

Monthly archive.

Test backup restoration regularly.

---

# Incident Response

If a vulnerability is discovered

1. Fix immediately.
2. Document the issue.
3. Test the fix.
4. Deploy update.
5. Review for similar vulnerabilities.

---

# Security Checklist

Before deployment

✔ Password hashing

✔ CSRF enabled

✔ SQL Injection protection

✔ XSS protection

✔ HTTPS enabled

✔ Environment variables configured

✔ Logging enabled

✔ Authentication verified

✔ Authorization verified

✔ Input validation complete

✔ Error handling tested

---

# Golden Rule

Assume every request is malicious until it is validated.

Security is everyone's responsibility.