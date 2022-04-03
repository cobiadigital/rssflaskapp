DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    description TEXT,
    imagefilename TEXT,
    audiofilename TEXT,
    audio_file_length TEXT,
    guid TEXT UNIQUE NOT NULL
)