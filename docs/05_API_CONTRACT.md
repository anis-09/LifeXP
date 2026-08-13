# LifeXP API Contract

Version: 1.0

---

# Purpose

This document defines every API endpoint used by LifeXP.

Frontend and backend must strictly follow this contract.

Rules

- JSON for API responses.
- Proper HTTP status codes.
- Consistent response format.
- Never expose passwords or sensitive data.
- Validate every request.

---

# Base URL

Development

http://127.0.0.1:5000

Future

https://api.lifexp.app

---

# Response Format

Success

{
    "success": true,
    "message": "Operation successful",
    "data": {}
}

Error

{
    "success": false,
    "message": "Something went wrong",
    "errors": []
}

---

# Authentication

## Register

POST

/api/auth/register

Body

{
    "full_name": "",
    "email": "",
    "password": "",
    "confirm_password": ""
}

Success

201 Created

Errors

400 Validation Error

409 Email Already Exists

---

## Login

POST

/api/auth/login

Body

{
    "email": "",
    "password": ""
}

Success

200 OK

Response

{
    "user": {},
    "session": true
}

Errors

401 Invalid Credentials

---

## Logout

POST

/api/auth/logout

Success

200 OK

---

# User

GET

/api/user/profile

Returns

- Name
- Avatar
- Level
- XP
- Coins
- Streak

---

POST

/profile/edit

Body (Form Data)

- full_name
- avatar

Success

302 Redirect to /profile with success flash

Errors

302 Redirect to /profile with error flash (Validation)

---

# Dashboard

GET

/api/dashboard

Returns

- User Stats
- Today's Missions
- Current Streak
- Notifications

---

# Missions

GET

/api/missions

Returns

Mission List

---

POST

/api/missions

Create Mission

Body

{
    "title":"",
    "description":"",
    "category":"",
    "difficulty":""
}

---

PUT

/api/missions/{id}

Update Mission

---

DELETE

/api/missions/{id}

Delete Mission

---

POST

/api/missions/{id}/complete

Complete Mission

Backend must

- Validate mission
- Prevent duplicate completion
- Award XP
- Award Coins
- Update Stats
- Check Achievements
- Create Notification

Response

{
    "xp":100,
    "coins":20,
    "level":4
}

---

# Achievements

GET

/api/achievements

Returns

Unlocked Achievements

---

# Rewards

GET

/api/rewards

Returns

Today's reward

---

POST

/api/rewards/claim

Claim reward

Rules

One claim per day

---

# Leaderboard

GET

/api/leaderboard

Query Parameters

- period (optional): global, weekly, monthly, friends

Returns

{
    "period": "global",
    "top_players": [
        {
            "rank": 1,
            "user_id": 1,
            "full_name": "Player 1",
            "avatar": "default.png",
            "xp": 1500,
            "level": 3,
            "streak": 5
        }
    ],
    "user_rank_row": {
        "rank": 17,
        "user_id": 42,
        "full_name": "Current Player",
        "avatar": "default.png",
        "xp": 500,
        "level": 2,
        "streak": 1
    },
    "user_in_top": false
}

Note: The current implementation renders this data directly via the `/leaderboard` route (SSR).

---

# Notifications

GET

/api/notifications

Returns

Unread notifications

---

PUT

/api/notifications/read

Marks notification as read

---

# Settings

GET

/api/settings

PUT

/api/settings

---

# Status Codes

200 OK

201 Created

204 Deleted

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

500 Internal Server Error

---

# Validation Rules

Email

Valid format

Password

Minimum 8 characters

One uppercase

One lowercase

One number

Mission Title

Maximum 100 characters

Mission Description

Maximum 500 characters

---

# Security

Always hash passwords.

Never trust frontend data.

Validate everything.

Never expose database IDs unnecessarily.

---

# Development Rule

Every future endpoint must be added to this document before implementation.