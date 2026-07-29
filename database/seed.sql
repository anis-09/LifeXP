--------------------------------------------------
-- DEFAULT USER (Development)
--------------------------------------------------

INSERT OR IGNORE INTO users
(
    id,
    full_name,
    email,
    password_hash,
    avatar
)
VALUES
(
    1,
    'Development User',
    'developer@lifexp.local',
    'development',
    'default.png'
);

--------------------------------------------------
-- DEFAULT MISSION CATEGORIES
--------------------------------------------------

INSERT OR IGNORE INTO mission_categories
(
    name,
    icon,
    color
)
VALUES

('Study', 'book', '#3B82F6'),
('Fitness', 'activity', '#10B981'),
('Coding', 'code', '#8B5CF6'),
('Reading', 'book-open', '#F59E0B'),
('Meditation', 'moon', '#06B6D4'),
('Health', 'heart', '#EF4444'),
('Work', 'briefcase', '#6366F1'),
('Personal', 'user', '#EC4899');