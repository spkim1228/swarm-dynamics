import duckdb
import shutil
from pathlib import Path

from swarm_dynamics import ROOT_PATH

RAW_DIR = ROOT_PATH / "datastore" / "raw" / "ai_village"
COOKED_DIR = ROOT_PATH / "datastore" / "cooked" / "ai_village"
FULL_DIR = COOKED_DIR / "full"
CUTOFF = "2026-07-03"
CUT_DIR = COOKED_DIR / f"since_{CUTOFF}"

TABLES = ["agents", "village_goals", "agent_goals", "chat_messages", "events", "agent_memories"]
# Lookup tables are kept whole in the cut dataset so every id still joins.
LOOKUP_TABLES = {"agents", "village_goals", "agent_goals"}


def compile_full(out_dir: Path = FULL_DIR) -> Path:
    """Convert each raw table to Parquet. Nested fields are kept as JSON columns and
    *_at / *_time columns are cast to TIMESTAMP (type inference is inconsistent on them)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    for t in TABLES:
        src = f"read_json('{RAW_DIR / t}.jsonl.gz', format='newline_delimited', maximum_depth=2, sample_size=-1)"
        cols = [c for c, *_ in con.sql(f"DESCRIBE SELECT * FROM {src}").fetchall()]
        select = ", ".join(f"CAST({c} AS TIMESTAMP) AS {c}" if c.endswith(("_at", "_time")) else c for c in cols)
        con.execute(f"COPY (SELECT {select} FROM {src}) TO '{out_dir / t}.parquet' (FORMAT parquet, COMPRESSION zstd)")
    shutil.copy(RAW_DIR / "CHANGELOG.md", out_dir)
    return out_dir


def compile_cut(src_dir: Path = FULL_DIR, out_dir: Path = CUT_DIR, cutoff: str = CUTOFF) -> Path:
    """Subset of the full dataset with created_at >= cutoff (lookup tables kept whole)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    for t in TABLES:
        where = "" if t in LOOKUP_TABLES else f"WHERE created_at >= TIMESTAMP '{cutoff}'"
        con.execute(
            f"COPY (SELECT * FROM '{src_dir / t}.parquet' {where}) TO '{out_dir / t}.parquet' (FORMAT parquet, COMPRESSION zstd)"
        )
    shutil.copy(src_dir / "CHANGELOG.md", out_dir)
    return out_dir


if __name__ == "__main__":
    print(f"Wrote {compile_full()}")
    print(f"Wrote {compile_cut()}")
