DROP TABLE IF EXISTS defs;

CREATE TABLE defs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author TEXT NOT NULL,
    word TEXT NOT NULL,
    content TEXT NOT NULL
);

DROP TABLE IF EXISTS authors;

CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    words_created INTEGER NOT NULL
);