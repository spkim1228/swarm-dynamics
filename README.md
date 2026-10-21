# swarm-dynamics


# Data

All data is stored in the `datastore/` folder, which is symlinked to an external hard drive. To set this up, run the following command at the root of this repository:

```
ln -s "/path/to/folder/location" "datastore"
```

Snapshot taken 2026-10-21: 24 files, 8.0 GB.

## Tree

```
datastore/
├── cooked/                                          (empty)
└── raw/
    ├── ai-village/
    │   ├── CHANGELOG.md                              23 KB
    │   ├── agent_goals.jsonl.gz                     4.7 KB
    │   ├── agent_memories.jsonl.gz                  2.4 GB
    │   ├── agents.jsonl.gz                          5.8 KB
    │   ├── chat_messages.jsonl.gz                    53 MB
    │   ├── claude_code_messages.jsonl.gz             99 MB
    │   ├── claude_code_sessions.jsonl.gz             12 KB
    │   ├── computer_use_sessions.jsonl.gz            41 MB
    │   ├── computer_use_turns.jsonl.gz              2.6 GB
    │   ├── events.jsonl.gz                          342 MB
    │   └── village_goals.jsonl.gz                   4.3 KB
    ├── collusion/
    │   ├── main/
    │   │   └── full-wiki-logs.zip                   4.0 MB
    │   └── other/
    │       ├── coverage-gaps.csv                     80 KB
    │       ├── links.jsonl.gz                       2.1 MB
    │       ├── other-wikis.json.gz                  4.8 KB
    │       ├── records.jsonl.gz                     3.7 MB
    │       ├── shortener-logs.json.gz                14 KB
    │       └── site-coverage.csv                    109 KB
    └── moltbook/
        ├── agents.parquet                            17 MB
        ├── comments.parquet                         901 MB
        ├── posts.parquet                            1.6 GB
        ├── snapshots.parquet                        253 KB
        ├── submolts.parquet                         644 KB
        └── word_frequency.csv                        31 MB
```

## `cooked/`

All data that was been modified and any analysis outputs of data are held in this folder.

## `raw/`

All raw data are held in this folder. No modifications were made to any of these file and exist as they were downloaded. All file formats are kept as the original unless noted below.

## `raw/ai-village/`

- **Source:** https://theaidigest.org/village
- **Accessibility:** Requires Hugging face account and repo author permission
- **Access Date:** 10/9/2026

### `CHANGELOG.md`

- **Size:** 23 KB

Documented dated scaffolding changes (prompt edits, tools added/removed, model upgrades, memory changes, roster changes).

### `agent_goals.jsonl.gz`

- **Size:** 4.7 KB

Per-agent individual goals (name, short name, description, optional start/end times), shown to that agent in its prompt below the village goal.

### `agent_memories.jsonl.gz`

- **Size:** 2.4 GB

The long-term memories agents wrote for themselves during memory consolidation.

### `agents.jsonl.gz`

- **Size:** 5.8 KB

Agent metadata: name, emoji, model string, goal, token usage.

### `chat_messages.jsonl.gz`

- **Size:** 53 MB

Chat messages (agent and human), with room, speaker, content, timestamp.

### `claude_code_messages.jsonl.gz`

- **Size:** 99 MB

Full message stream for agents that used the Claude Code scaffolding (a minority of agents).

### `claude_code_sessions.jsonl.gz`

- **Size:** 12 KB

Session records for the Claude Code agents.

### `computer_use_sessions.jsonl.gz`

- **Size:** 41 MB

Each computer-use session, with `session_goal` and the agent who ran it.

### `computer_use_turns.jsonl.gz`

- **Size:** 2.6 GB

Turn-by-turn computer use: the action taken (`agent_action`), the model's raw messages (`agent_messages`), tool output, and screenshot metadata. Screenshots are referenced, not inlined (see below).

### `events.jsonl.gz`

- **Size:** 342 MB

The structured activity timeline. Each row has a JSONB `data` field with an `actionType` (`AGENT_TALK`, `START_USING_COMPUTER`, `STOP_USING_COMPUTER`, `WAIT`, `PAUSE`, `USER_TALK`, `SEARCH_HISTORY`, …) and an `event_index` for ordering. The best starting point for a timeline overview.

### `village_goals.jsonl.gz`

- **Size:** 4.3 KB

The sequence of village-wide goals, with start/end times.

## `raw/collusion/`

- **Source:** https://collusion.wiki/
- **Accessibility:** Free, publicly available
- **Access Date:** 10/9/2026

## `raw/collusion/main/`

All data of edits made by AI agents on the obscure German wiki.

### `full-wiki-logs.zip`

- **Size:** 4.0 MB

## `raw/collusion/other/`

Data of edits made by AI agents on additional message boards

### `coverage-gaps.csv`

- **Size:** 80 KB

### `links.jsonl.gz`

- **Size:** 2.1 MB

### `other-wikis.json.gz`

- **Size:** 4.8 KB

### `records.jsonl.gz`

- **Size:** 3.7 MB

### `shortener-logs.json.gz`

- **Size:** 14 KB

### `site-coverage.csv`

- **Size:** 109 KB

## `raw/moltbook/`

- **Source:** https://moltbook-observatory.sushant.info.np/
- **Accessibility:** Free, publicly available
- **Access Date:** 10/21/2026

### `moltbook_observatory.db`

- **Size:** 7.7 GB

Full database dump of all collected dataset on Moltbook, including posts with metadata (ID, agent, submolt, title, content, score, timestamp), agents with stats (name, description, karma, followers, owner),and comments with metadata (ID, post_id, agent, content, score, timestamp).