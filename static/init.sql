CREATE TABLE IF NOT EXISTS Events (
    id              SERIAL PRIMARY KEY,
    event_type      VARCHAR(16) NOT NULL,
    event_data      TEXT NOT NULL,
    channel_id      BIGINT DEFAULT NULL,
    category_id     BIGINT DEFAULT NULL,
    user_id         BIGINT DEFAULT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
