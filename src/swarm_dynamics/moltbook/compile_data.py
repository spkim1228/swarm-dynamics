import duckdb
from pathlib import Path

from swarm_dynamics import ROOT_PATH

RAW_DB = ROOT_PATH / "datastore" / "raw" / "moltbook" / "moltbook_observatory.db"
COOKED_DIR = ROOT_PATH / "datastore" / "cooked" / "moltbook"

TS = "TIMESTAMPTZ"
# Kept columns and their types. Dropped: follows (empty), lost_and_found* (recovery
# duplicates), avatar/banner URLs (~all empty), agent_name (joins via agents),
# fetched_at and snapshot ids (scraper metadata).
SCHEMA = {
    "agents": {
        "id": "VARCHAR", "name": "VARCHAR", "description": "VARCHAR", "karma": "BIGINT",
        "follower_count": "BIGINT", "following_count": "BIGINT", "is_claimed": "BOOLEAN",
        "owner_x_handle": "VARCHAR", "created_at": TS, "first_seen_at": TS, "last_seen_at": TS,
    },
    "posts": {
        "id": "VARCHAR", "agent_id": "VARCHAR", "submolt": "VARCHAR", "title": "VARCHAR",
        "content": "VARCHAR", "url": "VARCHAR", "score": "BIGINT", "comment_count": "BIGINT",
        "is_pinned": "BOOLEAN", "created_at": TS,
    },
    "comments": {
        "id": "VARCHAR", "post_id": "VARCHAR", "agent_id": "VARCHAR", "parent_id": "VARCHAR",
        "content": "VARCHAR", "score": "BIGINT", "created_at": TS,
    },
    "submolts": {
        "name": "VARCHAR", "display_name": "VARCHAR", "description": "VARCHAR",
        "subscriber_count": "BIGINT", "post_count": "BIGINT", "created_at": TS, "first_seen_at": TS,
    },
    "snapshots": {
        "timestamp": TS, "total_agents": "BIGINT", "total_posts": "BIGINT", "total_comments": "BIGINT",
        "active_agents_24h": "BIGINT", "avg_sentiment": "DOUBLE", "top_words": "VARCHAR[]",
    },
    "word_frequency": {"word": "VARCHAR", "hour": TS, "count": "BIGINT"},
}
# Comments with no parseable created_at are malformed (agent profiles written into
# the comments table) or have no author.
ROW_FILTERS = {"comments": "TRY_CAST(NULLIF(created_at, '') AS TIMESTAMPTZ) IS NOT NULL"}


def compile_data(db_path: Path = RAW_DB, out_dir: Path = COOKED_DIR) -> Path:
    """Write each kept table to Parquet with typed columns; empty strings become NULL
    and mixed-format timestamps are normalised to UTC (naive values read as UTC)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite; SET sqlite_all_varchar=true; SET TimeZone='UTC'")
    con.execute(f"ATTACH '{db_path}' AS m (TYPE sqlite, READ_ONLY)")
    for table, cols in SCHEMA.items():
        select = ", ".join(
            f"CAST(CAST(NULLIF(\"{c}\", '') AS JSON) AS {t}) AS \"{c}\"" if t.endswith("[]")
            else f"TRY_CAST(NULLIF(\"{c}\", '') AS {t}) AS \"{c}\""
            for c, t in cols.items()
        )
        where = f"WHERE {ROW_FILTERS[table]}" if table in ROW_FILTERS else ""
        con.execute(
            f"COPY (SELECT {select} FROM m.{table} {where}) TO '{out_dir / table}.parquet' (FORMAT parquet, COMPRESSION zstd)"
        )
    return out_dir


if __name__ == "__main__":
    print(f"Wrote {compile_data()}")
