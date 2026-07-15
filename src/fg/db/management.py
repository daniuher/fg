from fg.core.metadata import get_metadata
from fg.db.session import get_session


def register_file(filepath: str) -> dict:
    meta = get_metadata(filepath)
    with get_session() as conn:
        conn.execute(
            """
            INSERT INTO files (
                hash, path, filename, extension, size_bytes, modified_at, registered_at
            )
            VALUES (
                :hash, :path, :filename, :extension, :size_bytes, :modified_at, :registered_at
            )
            ON CONFLICT(hash) DO UPDATE SET
                path = excluded.path,
                filename = excluded.filename,
                extension = excluded.extension,
                size_bytes = excluded.size_bytes,
                modified_at = excluded.modified_at
            """,
            meta,
        )
    return meta


def ensure_group(name: str) -> int:
    with get_session() as conn:
        conn.execute(
            "INSERT INTO groups (name) VALUES (?) ON CONFLICT(name) DO NOTHING",
            (name,),
        )
        row = conn.execute(
            "SELECT id FROM groups WHERE name = ?",
            (name,),
        ).fetchone()
    return row["id"]


def tag_file(filepath: str, group: str | None = None) -> dict:
    meta = register_file(filepath)

    if group:
        group_id = ensure_group(group)
        with get_session() as conn:
            conn.execute(
                """
                INSERT INTO file_groups (file_hash, group_id)
                VALUES (?, ?)
                ON CONFLICT(file_hash, group_id) DO NOTHING
                """,
                (meta["hash"], group_id),
            )

    return meta
