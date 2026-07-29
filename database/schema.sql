PRAGMA foreign_keys = ON;

--------------------------------------------------
-- USERS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    full_name TEXT NOT NULL,

    email TEXT NOT NULL UNIQUE,

    password_hash TEXT NOT NULL,

    avatar TEXT DEFAULT 'default.png',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    last_login TIMESTAMP,

    is_active INTEGER DEFAULT 1
);

--------------------------------------------------
-- USER STATS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS user_stats (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL UNIQUE,

    current_level INTEGER DEFAULT 1,

    current_xp INTEGER DEFAULT 0,

    current_coins INTEGER DEFAULT 0,

    current_streak INTEGER DEFAULT 0,

    longest_streak INTEGER DEFAULT 0,

    missions_completed INTEGER DEFAULT 0,

    missions_failed INTEGER DEFAULT 0,

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);

--------------------------------------------------
-- MISSION CATEGORIES
--------------------------------------------------

CREATE TABLE IF NOT EXISTS mission_categories (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL UNIQUE,

    icon TEXT,

    color TEXT
);

--------------------------------------------------
-- MISSIONS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS missions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    description TEXT,

    category_id INTEGER NOT NULL,

    difficulty TEXT NOT NULL,

    xp_reward INTEGER NOT NULL,

    coin_reward INTEGER NOT NULL,

    is_daily INTEGER DEFAULT 0,

    is_system INTEGER DEFAULT 0,

    created_by INTEGER,

    is_completed INTEGER DEFAULT 0,

    completed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(created_by) REFERENCES users(id),

    FOREIGN KEY(category_id) REFERENCES mission_categories(id)
);

--------------------------------------------------
-- USER MISSIONS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS user_missions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    mission_id INTEGER NOT NULL,

    status TEXT DEFAULT 'Pending',

    progress INTEGER DEFAULT 0,

    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id),

    FOREIGN KEY(mission_id) REFERENCES missions(id)
);

--------------------------------------------------
-- XP TRANSACTIONS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS xp_transactions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    source TEXT NOT NULL,

    reference_id INTEGER,

    amount INTEGER NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);

--------------------------------------------------
-- COIN TRANSACTIONS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS coin_transactions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    source TEXT NOT NULL,

    reference_id INTEGER,

    amount INTEGER NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);

--------------------------------------------------
-- ACHIEVEMENTS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS achievements (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    description TEXT,

    icon TEXT,

    xp_reward INTEGER DEFAULT 0,

    coin_reward INTEGER DEFAULT 0
);

--------------------------------------------------
-- USER ACHIEVEMENTS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS user_achievements (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    achievement_id INTEGER NOT NULL,

    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id),

    FOREIGN KEY(achievement_id) REFERENCES achievements(id)
);

--------------------------------------------------
-- DAILY REWARDS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS daily_rewards (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    day_number INTEGER NOT NULL,

    reward_type TEXT,

    reward_value INTEGER,

    claimed INTEGER DEFAULT 0,

    claimed_at TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);

--------------------------------------------------
-- NOTIFICATIONS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS notifications (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    title TEXT NOT NULL,

    message TEXT NOT NULL,

    type TEXT,

    is_read INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);

--------------------------------------------------
-- SETTINGS
--------------------------------------------------

CREATE TABLE IF NOT EXISTS settings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL UNIQUE,

    theme TEXT DEFAULT 'dark',

    language TEXT DEFAULT 'en',

    notifications_enabled INTEGER DEFAULT 1,

    FOREIGN KEY(user_id) REFERENCES users(id)
);

--------------------------------------------------
-- INDEXES
--------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_users_email
ON users(email);

CREATE INDEX IF NOT EXISTS idx_user_missions_user
ON user_missions(user_id);

CREATE INDEX IF NOT EXISTS idx_user_missions_status
ON user_missions(status);

CREATE INDEX IF NOT EXISTS idx_notifications_user
ON notifications(user_id);

CREATE INDEX IF NOT EXISTS idx_xp_transactions_user
ON xp_transactions(user_id);

CREATE INDEX IF NOT EXISTS idx_coin_transactions_user
ON coin_transactions(user_id);