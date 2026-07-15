"""
Table schemas as raw SQL. Kept as plain strings (not an ORM) to stay
lightweight and transparent — every query is visible and debuggable
directly in sqlite3 CLI.
"""

FILES_TABLE = """
CREATE TABLE IF NOT EXISTS files (
    hash          TEXT PRIMARY KEY,
    path          TEXT NOT NULL,
    filename      TEXT NOT NULL,
    extension     TEXT,
    size_bytes    INTEGER NOT NULL,
    modified_at   TEXT NOT NULL,
    registered_at TEXT NOT NULL
);
"""

GROUPS_TABLE = """
CREATE TABLE IF NOT EXISTS groups (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT UNIQUE NOT NULL,
    created_at    TEXT NOT NULL
);
"""

GROUP_MEMBERS_TABLE = """
CREATE TABLE IF NOT EXISTS group_members (
    group_id      INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    file_hash     TEXT    NOT NULL REFERENCES files(hash) ON DELETE CASCADE,
    added_at      TEXT NOT NULL,
    PRIMARY KEY (group_id, file_hash)
);
"""

PROVENANCE_TABLE = """
CREATE TABLE IF NOT EXISTS provenance (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    input_hash    TEXT NOT NULL REFERENCES files(hash),
    output_hash   TEXT NOT NULL REFERENCES files(hash),
    process       TEXT NOT NULL,
    notes         TEXT,
    recorded_at   TEXT NOT NULL
);
"""

SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version       INTEGER PRIMARY KEY,
    applied_at    TEXT NOT NULL
);
"""

ALL_TABLES = [
    SCHEMA_VERSION_TABLE,
    FILES_TABLE,
    GROUPS_TABLE,
    GROUP_MEMBERS_TABLE,
    PROVENANCE_TABLE,
]
