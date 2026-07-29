--------------------------------------------------
-- DEFAULT USER (Development)
-- Password: dev123  (pbkdf2:sha256, for local use only)
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
    'pbkdf2:sha256:600000$QA1LHL70JEzQVS4z$95d3f7de6a5a72e0acbc85d97d17ede01e37dafa79bbf0f5ad6164f9832167b7',
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