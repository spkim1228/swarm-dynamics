import json
import re
import zipfile
from collections.abc import Iterable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from swarm_dynamics import ROOT_PATH

RAW_ZIP = ROOT_PATH / "datastore" / "raw" / "collusion" / "main" / "full-wiki-logs.zip"
COOKED_DIR = ROOT_PATH / "datastore" / "cooked" / "collusion" / "main"
EDITS_PATH = COOKED_DIR / "edits.jsonl"


def _edit_kind(rev: dict, base_lines: list[str]) -> str:
    """Classify a revision by the shape of its diff against the previous revision."""
    if rev["diff_base_reason"] == "page_created":
        return "created"
    if rev["diff_base_reason"] == "earlier_revisions_not_published":
        return "unknown_base"
    hunks = rev["hunks"]
    if not hunks:
        return "no_change"
    ops = {h["op"] for h in hunks}
    if ops == {"insert"}:
        if all(h["a0"] == len(base_lines) for h in hunks):
            return "append"
        if all(h["a0"] == 0 for h in hunks):
            return "prepend"
        return "insert"
    if ops == {"delete"}:
        return "delete"
    if len(hunks) == 1 and hunks[0]["a0"] == 0 and hunks[0]["a1"] == len(base_lines):
        return "overwrite"
    return "replace"


def extract_edits(zip_path: Path = RAW_ZIP, out_path: Path = EDITS_PATH) -> Path:
    """Reduce every revision in the raw wiki logs to only what that edit changed.

    Reads revisions.jsonl straight from the zip (raw data is left untouched) and
    writes one JSON line per revision to out_path, sorted by time. Each record
    keeps the revision's metadata plus the added/removed lines, recovered from
    the stored diff hunks against the previous revision of the same page.
    """
    with zipfile.ZipFile(zip_path) as zf, zf.open("revisions.jsonl") as f:
        revisions = {r["rev_id"]: r for r in map(json.loads, f)}

    edits = []
    for rev in revisions.values():
        base = revisions.get(rev["diff_base"]) if rev["diff_base"] else None
        base_lines = base["body"].split("\n") if base else []
        body_lines = rev["body"].split("\n")

        changes = [
            {
                "op": h["op"],
                "at_line": h["a0"],
                "removed": base_lines[h["a0"] : h["a1"]],
                "added": body_lines[h["b0"] : h["b1"]],
            }
            for h in rev["hunks"]
        ]
        added = [line for c in changes for line in c["added"]]
        removed = [line for c in changes for line in c["removed"]]

        edits.append(
            {
                "rev_id": rev["rev_id"],
                "page_key": rev["page_key"],
                "wiki": rev["wiki"],
                "page": rev["name"],
                "seq": rev["seq"],
                "time": rev["time"],
                "label": rev["label"],
                "ip16": rev["ip16"],
                "change_summary": rev["change_summary"],
                "edit_kind": _edit_kind(rev, base_lines),
                "prev_rev_id": rev["diff_base"],
                "prev_label": base["label"] if base else None,
                "added_text": "\n".join(added),
                "removed_text": "\n".join(removed),
                "n_lines_added": len(added),
                "n_lines_removed": len(removed),
                "changes": changes,
                "relation_type": rev["relation_type"],
                "related_event_id": rev["related_event_id"],
            }
        )

    edits.sort(key=lambda e: (e["time"], e["page_key"], e["seq"]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for e in edits:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return out_path


def _to_datetime(value: str | date | datetime, is_end: bool = False) -> datetime:
    """Parse a filter bound. A date-only end bound includes that whole day."""
    if isinstance(value, str):
        date_only = len(value) == 10
        value = datetime.fromisoformat(value)
    else:
        date_only = not isinstance(value, datetime)
        if date_only:
            value = datetime(value.year, value.month, value.day)
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    if is_end and date_only:
        value += timedelta(days=1, microseconds=-1)
    return value


def _as_set(value: str | Iterable[str] | None) -> set[str] | None:
    if value is None:
        return None
    return {value} if isinstance(value, str) else set(value)


def _ip_prefix(ip: str) -> str:
    """Reduce a full IPv4 address or /16 prefix to the dataset's ip16 form."""
    return ".".join(ip.split(".")[:2])


def filter_edits(
    start: str | date | datetime | None = None,
    end: str | date | datetime | None = None,
    labels: str | Iterable[str] | None = None,
    label_pattern: str | None = None,
    ip16: str | Iterable[str] | None = None,
    wikis: str | Iterable[str] | None = None,
    pages: str | Iterable[str] | None = None,
    edit_kinds: str | Iterable[str] | None = None,
    path: Path = EDITS_PATH,
) -> list[dict]:
    """Return the edits from extract_edits() that match every given filter.

    start/end: inclusive time window; ISO strings, dates or datetimes (naive = UTC).
    labels: exact agent label(s); label_pattern: regex searched within the label.
    ip16: IP prefix(es) such as "20.165"; full IPv4 addresses are reduced to /16,
        since the dataset only publishes /16 prefixes.
    wikis, pages, edit_kinds: exact match on wiki, page name, or edit_kind.
    """
    start_dt = _to_datetime(start) if start is not None else None
    end_dt = _to_datetime(end, is_end=True) if end is not None else None
    label_set = _as_set(labels)
    label_re = re.compile(label_pattern) if label_pattern else None
    ip_set = {_ip_prefix(ip) for ip in _as_set(ip16)} if ip16 is not None else None
    wiki_set = _as_set(wikis)
    page_set = _as_set(pages)
    kind_set = _as_set(edit_kinds)

    matches = []
    with path.open(encoding="utf-8") as f:
        for edit in map(json.loads, f):
            if start_dt or end_dt:
                t = datetime.fromisoformat(edit["time"])
                if start_dt and t < start_dt:
                    continue
                if end_dt and t > end_dt:
                    continue
            if label_set is not None and edit["label"] not in label_set:
                continue
            if label_re and not label_re.search(edit["label"]):
                continue
            if ip_set is not None and edit["ip16"] not in ip_set:
                continue
            if wiki_set is not None and edit["wiki"] not in wiki_set:
                continue
            if page_set is not None and edit["page"] not in page_set:
                continue
            if kind_set is not None and edit["edit_kind"] not in kind_set:
                continue
            matches.append(edit)
    return matches


if __name__ == "__main__":
    print(f"Wrote {extract_edits()}")
