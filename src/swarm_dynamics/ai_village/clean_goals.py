import gzip
import json
from datetime import datetime
from pathlib import Path

from swarm_dynamics import ROOT_PATH

RAW_DIR = ROOT_PATH / "datastore" / "raw" / "ai_village"
COOKED_DIR = ROOT_PATH / "datastore" / "cooked" / "ai_village"
AGENT_GOALS_PATH = COOKED_DIR / "agent_goals.jsonl"
VILLAGE_GOALS_PATH = COOKED_DIR / "village_goals.jsonl"


def _read(name: str) -> list[dict]:
    with gzip.open(RAW_DIR / name, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def _write(rows: list[dict], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return path


def _iso(ts: str | None) -> str | None:
    """Normalise the raw 'YYYY-MM-DD HH:MM:SS[.f]' timestamps to ISO 8601 (timezone as in source)."""
    return datetime.fromisoformat(ts).isoformat() if ts else None


def clean_agent_goals(out_path: Path = AGENT_GOALS_PATH) -> Path:
    """Agent goals with agent name and model attached, sorted by start time."""
    agents = {a["id"]: a for a in _read("agents.jsonl.gz")}
    rows = [
        {
            "goal_id": g["id"],
            "agent_id": g["agent_id"],
            "agent_name": agents[g["agent_id"]]["name"],
            "model": agents[g["agent_id"]]["model_string"],
            "role": g["short_name"],
            "goal": g["name"],
            "description": g["description"],
            "start_time": _iso(g["start_time"]),
            "end_time": _iso(g["end_time"]),
        }
        for g in _read("agent_goals.jsonl.gz")
    ]
    rows.sort(key=lambda r: (r["start_time"], r["agent_name"]))
    return _write(rows, out_path)


def clean_village_goals(out_path: Path = VILLAGE_GOALS_PATH) -> Path:
    """Village-wide goals in chronological order; end_time is null for the current goal."""
    rows = [
        {
            "goal_id": g["id"],
            "goal": g["goal"],
            "start_time": _iso(g["start_time"]),
            "end_time": _iso(g["end_time"]),
        }
        for g in _read("village_goals.jsonl.gz")
    ]
    rows.sort(key=lambda r: r["start_time"])
    return _write(rows, out_path)


if __name__ == "__main__":
    print(f"Wrote {clean_agent_goals()}")
    print(f"Wrote {clean_village_goals()}")
