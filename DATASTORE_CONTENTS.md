# Datastore contents

What is inside every file under `datastore/`, as inspected on 2026-10-13.
For the folder layout and sizes, see the tree in `README.md`.

## How this was produced

- **Every `.jsonl.gz`, `.json.gz` and `.csv` file was read in full**, including the two multi-GB files. Record counts, field lists, value counts and date ranges below come from those full passes, not from samples.
- **Zip archives were extracted and their members inspected.** Tabular members were read in full; free-text members were sampled.
- **Long free-text fields were only sampled** (chat content, memories, wiki bodies, payload text). Descriptions of what the text "is about" are limited to what a file's own documentation says or what a few sampled rows show.
- **Statements about meaning are sourced.** Where a file ships its own documentation (a README, manifest, changelog or `source` note), I quote or paraphrase that and say so. Where nothing documents a field, I say "undocumented" instead of guessing.
- **Not inspected:** the two image files in the government archive (see that section), and most of the 50 small `responses/*.txt` files there (5 were opened).

Conventions used below: "n" is the number of records in which a field is present; "null" means JSON `null`; counts written as `value × count`.

---

## `cooked/`

Empty. No files.

---

## `raw/ai-village/`

Eleven files: one Markdown changelog and ten gzipped JSON-lines tables. Every table row is a JSON object. All tables carry a single `village_id` value where that column exists (`00ebc425-074c-466f-ab2d-5aa2efa445aa`).

Timestamps are strings like `2026-07-10 21:09:27.837523` with no timezone marker; no file states the timezone of these columns.

Relationships I verified by joining the files:

| Relationship | Result |
|---|---|
| `computer_use_sessions.agent_id` → `agents.id` | all match |
| `computer_use_turns.session_id` → `computer_use_sessions.id` | all 2,689,904 turns match; 83,813 of 84,073 sessions have at least one turn |
| `chat_messages.agent_speaker_id` → `agents.id` | all 52 distinct speakers match |
| `events.data.messageId` → `chat_messages.id` | every chat message id appears in events; events has 57 extra message ids not in `chat_messages` |
| `events.data.computerUseSessionId` → `computer_use_sessions.id` | all match |
| `agent_goals.agent_id` → `agents.id` | all match |
| `claude_code_messages.sdk_session_id` → `claude_code_sessions.sdk_session_id` | **not** a full match: messages have 53 distinct values, sessions have 42 |

### `CHANGELOG.md`

**Overview.** A prose changelog titled "AI Village scaffolding changelog". By its own description it documents changes to the scaffolding around the agents (prompts, tools, memory system, computer-use and human-use mechanics) so researchers can tell agent behaviour apart from environment changes. It states the scaffolding code is not open source and that the list is "LLM-written based on our private git history".

**Contents.**
- **Agent roster table:** agent name, model string, joined date, left date (or "active"). 52 rows, from the 2025-04-02 launch to 2026-09-29.
- **Dated scaffolding changes:** entries from 2025-04-02 to 2026-07-03, each tagged `[Prompt]`, `[Tools]`, `[Memory]`, `[Computer-use]`, `[Human-use]`, `[Chat]`, `[Goals]` or `[Other]`.
- **Regime change it flags:** the 2026-03-24 "perma-computer-use rollout", which it calls "the single biggest structural change in the dataset" and says to treat data before and after late March 2026 as different regimes.
- **Pointers to other files:** it says the "Opus 4.5 (Claude Code)" agent's data is in `claude_code_messages`, and that per-agent goals are in `agent_goals.jsonl.gz`.

The roster table has 52 rows, the same number as the records in `agents.jsonl.gz`; I did not compare them name by name.

### `agents.jsonl.gz`

**Overview.** One row per agent: 52 records. A registry of agents with their model string, token counters and current state.

| Field | Type | What the data shows |
|---|---|---|
| `id` | string (UUID) | 52 distinct |
| `name` | string | 52 distinct display names, e.g. `Claude 3.7 Sonnet`, `GPT-5.1`, `Opus 4.5 (Claude Code)` |
| `emoji` | string | `🤖` in all 52 |
| `status_message` | null | null in all 52 |
| `model_string` | string | e.g. `claude-3-5-sonnet-20241022`, `z-ai/glm-5.3-flash`; 7–91 chars |
| `is_pending` | bool | `false` × 52 |
| `is_updating_memory` | bool | `false` × 51, `true` × 1 |
| `input_tokens_used` | int | 0 to 728,178,931 |
| `output_tokens_used` | int | 0 to 10,164,741 |
| `last_seen_event_index` | int | 14,714 to 479,140 |
| `money` | **string** holding a number | e.g. `-591`, `0`, `763`; mostly negative. Meaning undocumented |
| `paused_until` | string or null | null × 40; otherwise a timestamp |
| `paused_until_task_id` | string or null | null × 51; the one value is a timestamp-like string |
| `current_computer_use_session_id` | UUID or null | null × 7 |
| `village_id` | UUID | single value |
| `created_at`, `updated_at` | string | created 2025-04-02 to 2026-09-29; updated 2026-02-25 to 2026-10-07 |
| `goal` | null | null in all 52 |
| `is_participating` | bool | `true` × 38, `false` × 14 |
| `current_human_use_session_request_id` | null | null in all 52 |
| `is_paused_for_google_sign_in` | bool | `false` × 52 |
| `current_room_id` | UUID | 3 distinct; one room holds 49 agents |

### `agent_goals.jsonl.gz`

**Overview.** 39 records, one per individual goal assigned to an agent. The changelog says per-agent goals were added on 2026-07-03 and are shown to each agent below the village goal.

| Field | Type | What the data shows |
|---|---|---|
| `id` | UUID | 39 distinct |
| `agent_id` | UUID | 38 distinct (one agent has 2 goals) |
| `name` | string | goal text, 21–193 chars, e.g. "Maximize viewers of an animated series you create" |
| `short_name` | string | 30 distinct labels, e.g. `Game dev`, `YouTuber`, `Reporter`, `Prankster` |
| `description` | string or null | null × 31; 8 have text (25–1,991 chars) |
| `start_time` | string | 2026-07-06 to 2026-09-30; 21 share `2026-07-06 15:59:00` |
| `end_time` | string or null | null × 38 |
| `created_at`, `updated_at` | string | 2026-07-03 to 2026-09-30 |

### `village_goals.jsonl.gz`

**Overview.** 51 records, one per village-wide goal period.

| Field | Type | What the data shows |
|---|---|---|
| `id` | UUID | 51 distinct |
| `village_id` | UUID | single value |
| `goal` | string | goal text, 18–105 chars, e.g. "Adopt a park and get it cleaned!" |
| `start_time` | string | 2025-04-02 to 2026-07-06 |
| `end_time` | string or null | null × 1; otherwise 2025-05-10 to 2026-07-06 |
| `created_at`, `updated_at` | string | 2025-04-02 to 2026-07-06 |

### `chat_messages.jsonl.gz`

**Overview.** 192,167 chat messages posted in the village's chat rooms, by agents and by human users, from 2025-04-02 to 2026-10-07.

| Field | Type | What the data shows |
|---|---|---|
| `id` | UUID | unique |
| `speaker_type` | string | `agent` × 182,159; `user` × 10,008 |
| `agent_speaker_id` | UUID or null | set on the 182,159 agent messages; 52 distinct agents |
| `user_speaker_id` | UUID or null | set on the 10,008 user messages; 602 distinct users |
| `content` | string | message text; 0–32,921 chars, mean 503 |
| `room_id` | UUID | 16 distinct rooms |
| `created_at`, `updated_at` | string | 2025-04-02 17:47 to 2026-10-07 00:00 |
| `has_been_approved` | bool or null | `true` × 9,809; null × 182,358 |

Room names are not in this file. Mapping `room_id` through the `ENTER_ROOM` events in `events.jsonl.gz` gives: `general` 157,977 messages; `rest` 20,078; `best` 8,388; `focus` 3,503; `universe-coordination` 1,742; `voted-out` 253; `showcase-live` 173; and nine rooms with 22 or fewer.

### `events.jsonl.gz`

**Overview.** 404,823 records. The village's event log: every agent action and chat event, with the raw model output that produced it. The discriminator is `data.actionType`. Runs from 2025-04-02 to 2026-10-07.

Top-level fields:

| Field | Type | What the data shows |
|---|---|---|
| `id` | UUID | unique |
| `event_index` | int | unique; 5,839 to 479,152, so there are gaps. The file is **not** sorted by it |
| `village_id` | UUID | single value |
| `created_at`, `updated_at` | string | 2025-04-02 to 2026-10-07 |
| `data` | object | the event payload; keys depend on `actionType` |

Event types, with counts, date range, and the `data` keys seen on that type (a key listed is not necessarily present on every row of the type):

| `actionType` | Count | Dates | Keys in `data` besides `actionType` |
|---|---|---|---|
| `AGENT_TALK` | 182,159 | 2025-04-02 → 2026-10-07 | `chatMessageId`, `content`, `cost`, `inputTokens`, `messageId`, `output`, `outputTokens`, `roomId`, `speakerId`, `speakerType` |
| `CONSOLIDATE` | 58,030 | 2026-03-24 → 2026-10-07 | `agentId`, `computerUseSessionId`, `cost`, `inputTokens`, `nextSessionGoal`, `nextShortDisplayedSessionGoal`, `output`, `outputTokens`, `roomId` |
| `PAUSE` | 48,719 | 2025-04-02 → 2026-10-07 | `agentId`, `cost`, `inputTokens`, `output`, `outputTokens`, `roomId`, `seconds` |
| `WAIT` | 36,022 | 2025-04-02 → 2026-03-23 | `agentId`, `cost`, `inputTokens`, `output`, `outputTokens`, `roomId` |
| `START_USING_COMPUTER` | 25,975 | 2025-04-02 → 2026-05-29 | `agentId`, `computerUseSessionId`, `cost`, `inputTokens`, `output`, `outputTokens`, `roomId`, `sessionGoal`, `shortDisplayedSessionGoal` |
| `STOP_USING_COMPUTER` | 25,939 | 2025-04-02 → 2026-03-27 | `agentId`, `cost`, `inputTokens`, `output`, `outputTokens`, `roomId`, `summary` |
| `SEARCH_HISTORY` | 11,246 | 2025-09-19 → 2026-10-06 | `agentId`, `answerToQuery`, `cost`, `endDate`, `endDay`, `inputTokens`, `output`, `outputTokens`, `query`, `roomId`, `startDate`, `startDay` |
| `USER_TALK` | 10,065 | 2025-04-02 → 2026-10-05 | `chatMessageId`, `content`, `hasBeenApproved`, `messageId`, `roomId`, `speakerId`, `speakerName`, `speakerType` |
| `USER_NAME_CHANGE` | 3,711 | 2025-04-02 → 2026-08-28 | `newName`, `oldName`, `userId` |
| `REQUEST_GOOGLE_SIGN_IN` | 636 | 2025-10-06 → 2026-10-06 | `agentId`, `cost`, `inputTokens`, `output`, `outputTokens`, `roomId` |
| `RESTARTING_AFTER_GOOGLE_SIGN_IN` | 628 | 2025-10-06 → 2026-10-06 | `agentId`, `cost`, `inputTokens`, `outputTokens`, `roomId` |
| `ENTER_ROOM` | 459 | 2026-03-05 → 2026-09-29 | `agentId`, `cost`, `currentRooms`, `inputTokens`, `output`, `outputTokens`, `previousRoomId`, `previousRoomName`, `roomId`, `roomName` |
| `OUTREACH_APPROVAL_REQUEST` | 400 | 2026-04-14 → 2026-10-06 | `agentId`, `cost`, `inputTokens`, `medium`, `messageContent`, `output`, `outputTokens`, `outreachApprovalRequestId`, `rationale`, `recipient`, `roomId` |
| `OUTREACH_APPROVAL_RESPONSE` | 391 | 2026-04-16 → 2026-10-06 | `adminComment`, `agentId`, `approval`, `cost`, `inputTokens`, `medium`, `messageContent`, `outputTokens`, `outreachApprovalRequestId`, `rationale`, `recipient`, `roomId` |
| `REQUEST_HUMAN_HELPER` | 265 | 2025-08-15 → 2026-09-01 | `agentId`, `cost`, `estimatedDuration`, `humanConstraints`, `humanUseSessionRequestId`, `inputTokens`, `output`, `outputTokens`, `roomId`, `sessionGoal`, `shortDisplayedSessionGoal` |
| `CANCEL_REQUEST_FOR_HUMAN_HELPER` | 141 | 2025-08-15 → 2026-08-24 | `agentId`, `cost`, `inputTokens`, `output`, `outputTokens`, `roomId` |
| `STOP_HUMAN_USE_SESSION` | 37 | 2025-08-15 → 2026-08-24 | `agentId`, `cost`, `endComment`, `endReason`, `inputTokens`, `output`, `outputTokens`, `roomId`, `summary` |

Notes on selected `data` fields:

- **`cost`:** integer, `1` × 385,058 and `0` × 5,989. Unit undocumented.
- **`inputTokens` / `outputTokens`:** integers, up to 662,318 and 20,060.
- **`seconds`** (on `PAUSE`): 1 to 259,200.
- **`startDay` / `endDay`** (on `SEARCH_HISTORY`): integers 1 to 484. **`startDate` / `endDate`:** date strings, 2025-10-01 to 2026-10-06.
- **`approval`** (on `OUTREACH_APPROVAL_RESPONSE`): `true` × 290, `false` × 101.
- **`endReason`** (on `STOP_HUMAN_USE_SESSION`): `agent_ended` × 26, `user_timeout` × 10, `user_ended` × 1.
- **`speakerType`:** `agent` × 179,536, `HUMAN` × 10,065.
- **`output`:** present on 283,482 events. It is the model's raw response and its shape varies: a JSON object in 173,691 rows and a list in 109,791. The full profile found 252 distinct field paths across the file. Shapes seen include objects with `content` / `stop_reason` / `usage` / `model`; objects with `candidates` / `usageMetadata` / `modelVersion` (values such as `gemini-2.5-pro`); objects with `tool_calls` / `reasoning_content`; and lists of items typed `function_call`, `reasoning`, `message`, `thinking`, `text`, `tool_use`.
- **`output.stop_reason`** where present: `tool_use` × 62,785, `end_turn` × 4,152, `refusal` × 192, `max_tokens` × 2.

### `computer_use_sessions.jsonl.gz`

**Overview.** 84,073 records, one per computer-use session an agent ran, with the goal the agent set for it. 2025-04-02 to 2026-10-07.

| Field | Type | What the data shows |
|---|---|---|
| `id` | UUID | unique |
| `agent_id` | UUID | 52 distinct; the busiest agent has 7,725 sessions |
| `village_id` | UUID | single value |
| `created_at`, `updated_at` | string | 2025-04-02 18:00 to 2026-10-07 00:06 |
| `has_been_asked_to_stop` | bool | `false` × 84,072, `true` × 1 |
| `session_goal` | string or null | null × 3; free text, 4–45,515 chars, mean 966 |
| `short_displayed_session_goal` | string or null | null × 449; 4–175 chars, mean 41 |

### `computer_use_turns.jsonl.gz`

**Overview.** 2,689,904 records, one per turn inside a computer-use session: the model's raw response, the action it took, and the tool's text output or error. This is the largest file. 2025-04-02 to 2026-10-07. Sessions have a median of 41 turns and a maximum of 326.

There is **no screenshot image field** in this file; only flags about screenshot redaction.

| Field | Type | What the data shows |
|---|---|---|
| `id` | UUID | unique |
| `session_id` | UUID | joins to `computer_use_sessions.id` |
| `agent_action` | object or null | null × 87,727; the parsed action (see below) |
| `agent_messages` | object or list | object × 2,039,654, list × 650,250; the raw model response (see below) |
| `output` | string or null | null × 1,456,524; tool output text, up to 398,993 chars, mean 1,376 |
| `error` | string or null | set on 164,709 rows; up to 130,952 chars |
| `system` | string or null | set on 577 rows; e.g. "tool has been restarted." |
| `screenshot_is_redacted` | bool | `false` × 2,675,532, `true` × 14,372 |
| `has_redaction_been_overruled` | bool or null | null × 1,550,320, `false` × 1,139,453, `true` × 131 |
| `created_at`, `updated_at` | string | 2025-04-02 to 2026-10-07 |

`agent_action` keys seen:

- **`action`** (n = 1,524,914): `left_click` × 382,135; `key` × 246,199; `scroll` × 182,558; `type` × 167,095; `get_pixel_coords_of_element` × 157,561; `send_message_back_to_chat` × 109,020; `mouse_move` × 80,070; `screenshot` × 60,936; `wait` × 51,295; `pause` × 48,085; `search_history` × 10,599; plus 15 rarer values including `triple_click`, `double_click`, `left_click_drag`, `right_click`, `view_clipboard`, `move_to_room`, `hold_key`, `request_Google_sign_in`, `request_approval_for_unsolicited_outreach`, `request_human_helper`.
- **`command`** (n = 1,074,121): shell command text, up to 71,747 chars.
- **`restart`** (n = 243,536): bool, null, or in 4 rows the string `"true"`.
- **`text`**, **`coordinate`** (a two-integer list, values 0–3,873), **`description`**, **`content`** (chat text for `send_message_back_to_chat`), **`seconds`**, **`query`**, **`startDate`/`endDate`**, **`startDay`/`endDay`**, **`roomName`**, **`medium`**, **`recipient`**, **`sessionGoal`**, **`shortDisplayedSessionGoal`**, **`duration`**, **`scrollAmount`**, **`scrollDirection`**, **`startCoordinate`**: each present only for the action types that use them.

`agent_messages` shapes seen (357 distinct field paths in total across the file):

- **Object with `model`, `content[]`, `stop_reason`, `usage`** (n = 961,835). `model` takes 18 values, all `claude-*`, led by `claude-haiku-4-5-20251001` × 173,798 and `claude-opus-4-5-20251101` × 146,733. `content[].type` is `tool_use`, `text` or `thinking`. `stop_reason`: `tool_use` × 947,498, `end_turn` × 13,694, `max_tokens` × 508, `refusal` × 135. On 117 rows `stop_details.category` is set: `cyber` × 75, `bio` × 14, `reasoning_extraction` × 6, null × 22.
- **Object with `candidates[]`, `modelVersion`, `usageMetadata`** (n = 596,332). All 9 `modelVersion` values contain `gemini`, led by `gemini-2.5-pro` × 201,473.
- **List of items** (650,250 rows) with `type` in `function_call` × 505,543, `reasoning` × 470,376, `message` × 289,394, `computer_call` × 63,186. Function names: `bash` × 232,432; `use_computer` × 197,632; `send_message_to_chat` × 26,648; `get_pixel_coords_of_element` × 23,419; `pause` × 21,808; and eight rarer ones. Some items carry `encrypted_content`.
- **Object with `tool_calls[]`, `reasoning` / `reasoning_content`** (n = 461,774 with `tool_calls`).
- **Object with `textMessage` / `thinkingMessage` / `_sdkFormat`** (n = 11,679).

### `agent_memories.jsonl.gz`

**Overview.** 251,860 records. Each is a snapshot of an agent's memory document at a point in time. The content is long free text; this is the second-largest file. 2025-04-02 to 2026-10-07.

| Field | Type | What the data shows |
|---|---|---|
| `id` | UUID | unique |
| `agent_id` | UUID | 52 distinct; the busiest agent has 34,751 snapshots |
| `content` | string | 0 to 1,640,873 chars, mean 27,835. Sampled rows are Markdown-style notes headed e.g. "Consolidated Operational Memory — GPT‑5 …" or "# Internal Memory — Claude Opus 4.7 …" |
| `created_at`, `updated_at` | string | 2025-04-02 18:00 to 2026-10-07 00:06 |

There is no session or event id on these rows; the only link to other tables is `agent_id` plus the timestamp.

### `claude_code_sessions.jsonl.gz`

**Overview.** 303 records, all for one agent (`0c5968ed-…`, named `Opus 4.5 (Claude Code)` in `agents.jsonl.gz`). 2026-01-26 to 2026-03-31. The changelog says this agent ran different scaffolding from the others and should be analysed separately.

| Field | Type | What the data shows |
|---|---|---|
| `id` | UUID | 303 distinct |
| `agent_id` | UUID | single value |
| `sdk_session_id` | UUID | 42 distinct; one value covers 260 of the 303 rows |
| `created_at`, `updated_at` | string | 2026-01-26 19:05 to 2026-03-31 17:01 |

### `claude_code_messages.jsonl.gz`

**Overview.** 244,820 records: the message-by-message transcript of that same agent, 2026-01-26 to 2026-03-31. Each row wraps one SDK message in `content`.

| Field | Type | What the data shows |
|---|---|---|
| `id` | UUID | unique |
| `agent_id` | UUID | single value |
| `sdk_session_id` | UUID | 53 distinct |
| `message_uuid` | null | null in every row |
| `message_type` | string | `assistant` × 168,266; `user` × 73,154; `system` × 3,135; `result` × 265 |
| `message_subtype` | string or null | null × 241,419; `status` × 1,881; `compact_boundary` × 940; `init` × 314; `success` × 211; `error_during_execution` × 54; `prompt` × 1 |
| `content` | object | the message itself; 271 distinct field paths across the file |
| `created_at` | string | no `updated_at` column in this file |

Inside `content`:

- **`content.message`** (assistant and user rows): `role`, `model` (`claude-opus-4-5-20251101` × 168,245, `<synthetic>` × 21), `usage` token counters, and `content[]` blocks typed `tool_use` × 72,225, `tool_result` × 72,213, `thinking` × 65,550, `text` × 31,431.
- **Tool names called:** `mcp__village__get_events` × 33,905; `Bash` × 10,783; `mcp__village__computer_use` × 7,200; `Read` × 5,433; `mcp__village__bash` × 4,553; `mcp__village__chat_message` × 2,627; `mcp__village__edit_memory` × 2,365; plus 15 rarer ones.
- **`content.tool_use_result`** (n = 72,213): the structured tool result. Shape depends on the tool, e.g. `stdout`/`stderr` for shell, `filePath`/`structuredPatch` for edits, `file` for reads.
- **Images are removed:** all 4,641 image results have `file.base64` equal to the literal `[IMAGE_REMOVED]`.
- **`init` rows** (n = 314) record the session setup: `tools[]`, `mcp_servers[]` (one server, `village`), `claude_code_version` (`2.0.77` × 173, `2.1.38` × 141), `permissionMode` (`bypassPermissions` × 314).
- **`result` rows** (n = 265) record per-run totals: `num_turns`, `duration_ms`, `total_cost_usd` (0 to 201.07), `modelUsage` broken down by model, `is_error` (`false` × 190, `true` × 75).
- **`compact_boundary` rows** (n = 940) carry `compact_metadata.trigger` = `auto` and `pre_tokens` of 155,002 to 179,868.

---

## `raw/collusion/main/`

Six files. The five `.gz` files are byte-identical copies of five members of `full-wiki-logs.zip`: I decompressed each and its SHA-256 matches the zip's `SHA256SUMS`. So the zip and the loose `.gz` files hold the same data twice.

The manifest states the export was generated 2026-09-03 from a SQLite database (`corpus/farm_db/farm.sqlite`), cut to revisions with `write_date >= 2026-05-01`, covering four wikis named `dse`, `probier`, `fractal` and `dorfwiki`.

Throughout this dataset, IP addresses appear only as their first two octets (field `ip16`, e.g. `20.165`), and some names appear as placeholders such as `[Admin1]` or `[Person14]`.

Relationships I verified: every `revisions.page_id` is in `pages.jsonl` and vice versa; every `revisions.label` is in `labels.jsonl`; every non-null `events.revision_ref` is a `revisions.rev_id`.

### `full-wiki-logs.zip`

**Overview.** Zip of six files, 54.6 MB uncompressed: `pages.jsonl`, `revisions.jsonl`, `events.jsonl`, `labels.jsonl`, `manifest.json`, `SHA256SUMS`. All member timestamps are 1980-01-01. The first five are described under their `.gz` twins below. `SHA256SUMS` (398 bytes) lists a SHA-256 for each of the other five.

### `manifest.json.gz`

**Overview.** A single JSON object (62 KB uncompressed) describing the export: totals, definitions of each count, and the export's own self-checks. It is documentation for the other four files.

Top-level keys (17):

| Key | What it holds |
|---|---|
| `generated_at` | `2026-09-03T03:42:36Z` |
| `db_sha256` | hash of the source database |
| `cut` | the filter: `revision.write_date >= 2026-05-01` |
| `counts` | 14,591 revisions, 4,579 pages, 3,103 labels |
| `per_wiki` | revisions / pages / body bytes for each wiki. `dse`: 13,403 revisions, 3,908 pages. `probier`: 1,013 and 601. `fractal`: 169 and 68. `dorfwiki`: 6 and 2 |
| `population_counts` | `save` 14,591; `delete` 5,217; `revert` 4; `probe` 101; `first_recreation_relations` 68; plus a `never_sum` note warning that these populations overlap and the 19,913-row total of `events.jsonl` "has no incident meaning" |
| `grade_histograms` | how each event's timestamp was corroborated: `reqlog`, `rclog` or `write_date` |
| `body_bytes`, `body_encoding` | 27,186,058 body bytes; `ascii` 14,340, `utf8` 250, `latin1` 1 |
| `page_family_coverage` | 3,908 pages covered by a page-family map, 671 uncovered |
| `facts` | 58 named counts, each with `value`, `definition`, `source_refs` and a `never_add_to` list |
| `recreation_source` | how the 68 "first recreation" relations were derived |
| `resources`, `tool_versions` | export run stats; Python 3.13.5, SQLite 3.46.1, exporter `explorer-schema-2` |
| `source_scan` | row counts scanned from each upstream log file |
| `request_source_note` | a note on which request logs were needed |
| `checks` | 122 self-checks, each with `name`, `expected`, `actual`, `ok` |

Definitions from `facts` that explain terms used in the other files: `dse_admin_deletion_events` is "Successful DSE administrator deletion events in the declared window" (5,217, dated 2026-06-04 to 2026-07-14); `dse_script_probe_requests` is "DSE requests in the narrow executable script-injection family" (101); `first_recreation_relations` is "First-recreation relation edges from eligible deletions to their first later successful mutation" (68).

### `pages.jsonl.gz`

**Overview.** 4,579 records, one per wiki page in the cut, with per-page aggregates.

| Field | Type | What the data shows |
|---|---|---|
| `page_id` | string | `wiki/name`, e.g. `dorfwiki/AgentDataUSAProbeFebX2` |
| `page_key` | string | same with `~` separator and escaped characters, e.g. `probier~~5bPerson14~5d` |
| `wiki` | string | `dse` × 3,908; `probier` × 601; `fractal` × 68; `dorfwiki` × 2 |
| `name` | string | page name, 1–55 chars |
| `bucket` | string | 26 values, mostly a single letter (`A` × 2,183, `O` × 497 …) plus `other` |
| `page_family` | string | 49 values. Top: `source-cache-url-list` × 1,231; `relay-coordination` × 709; `source-or-unclassified` × 677; `off_store_unclassified` × 671; `loop-chain-infrastructure` × 339; `probe-test` × 236 |
| `page_family_cohort` | string or null | null × 3,334; otherwise labels like `Nov18`, `Mar07` |
| `page_family_confidence` | float or null | 0.35 to 0.98; null × 671 |
| `page_family_method`, `page_family_source` | string / null | how the family was assigned |
| `n_revs` | int | 1 to 2,327; 3,126 pages have exactly 1 |
| `n_revs_before` | int | revisions before the cut; 0 × 4,562 |
| `first_write`, `last_write` | ISO UTC string | 2026-05-24 to 2026-07-02 |
| `body_bytes` | int | 0 to 7,218,730 |
| `deleted_live` | bool | `false` × 4,579 |
| `live_body_variant` | string | `txt` × 3,900; `dw` × 679 |
| `head_differs_from_live` | bool | `false` × 3,903; `true` × 676 |
| `n_deletions` | int | 0 to 8; `1` × 3,845 |
| `n_recreations` | int | 0 to 7; `0` × 4,531 |
| `labels` | list of strings | editor labels seen on the page; 1 to 342 entries |
| `n_labels`, `n_ips`, `n_ip16` | int | distinct labels, IPs and /16 blocks per page |

### `revisions.jsonl.gz`

**Overview.** 14,591 records, one per saved page revision, **including the full page text** and a line diff against the previous revision. 2026-05-24 to 2026-07-02.

| Field | Type | What the data shows |
|---|---|---|
| `rev_id` | string | `page_key@seq`, e.g. `dorfwiki~AgentDataUSAProbeFebX2@1` |
| `page_id`, `page_key`, `wiki`, `name` | string | as in `pages.jsonl`. `dse` × 13,403; `probier` × 1,013; `fractal` × 169; `dorfwiki` × 6 |
| `seq` | int | revision number within the page, 1 to 2,335 |
| `rcs_rev`, `rcs_path` | string | e.g. `1.1`; `dse_page/A/A2DataProbe173920.txt_r` |
| `body` | string | full revision text, 0–38,832 chars, mean 1,863 |
| `body_len`, `lines` | int | lengths; up to 248 lines |
| `body_sha256` | string | hash of the body |
| `body_encoding` | string | `ascii` × 14,340; `utf8` × 250; `latin1` × 1 |
| `diff_base` | string or null | the `rev_id` diffed against; null × 4,579 |
| `diff_base_reason` | string or null | `page_created` × 4,562; `earlier_revisions_not_published` × 17 |
| `hunks` | list of objects | diff hunks: `op` (`insert` × 10,238, `replace` × 5,267, `delete` × 784) and line ranges `a0`, `a1`, `b0`, `b1` |
| `label` | string | the editor's self-chosen label, 0–39 chars, e.g. `DataResearcherAlpha`; the manifest counts 899 blank |
| `ip16` | string | first two octets of the saving address |
| `time` | ISO UTC string | the chosen timestamp |
| `time_grade` | string | `reqlog` × 14,482; `rclog` × 103; `write_date` × 6 |
| `winning_clock` | string | `revision.pref_ts` × 14,591 |
| `uncertainty_seconds` | int | `1` × 14,591 |
| `request_time`, `success_time`, `write_date`, `archived_at` | ISO string or null | alternative clocks for the same save |
| `recent_changes_time` | null | null in all rows |
| `request_action` | string or null | `form_edit` × 14,482; null × 109 |
| `change_summary` | string or null | the edit summary; null × 972 |
| `related_event_id`, `relation_type`, `round_id` | list / string / null | set on 63 rows; `relation_type` is `first_recreation_of` |

### `events.jsonl.gz`

**Overview.** 19,913 records mixing four event populations. The manifest warns these overlap and should not be summed. 2026-05-17 to 2026-07-14.

`event_type`: `save` × 14,591; `delete` × 5,217; `probe` × 101; `revert` × 4.

| Field | Type | What the data shows |
|---|---|---|
| `event_id` | string | prefixed by type, e.g. `delete:dse:rclog:131972`, `probe:attacklog_raw_dse_2605.jsonl:30` |
| `event_type` | string | as above |
| `time` | ISO UTC string | 2026-05-17T05:46:45Z to 2026-07-14T13:56:54Z |
| `time_grade` | string | `reqlog` × 19,803; `rclog` × 104; `write_date` × 6 |
| `wiki`, `page`, `page_key` | string | n = 19,812 (absent on probes) |
| `revision_ref` | string or null | n = 19,812; set on the 14,591 saves |
| `ip16` | string | n = 5,322; `2.202` × 5,217 |
| `request_action` | string | n = 5,322; `delete` × 5,217; `browse-bare` × 43; `form_editprefs` × 26; `browse` × 24; … one value is a literal script tag |
| `param_family` | string | n = 101 (probes); `search` × 29; `old_plist` × 26; `msg` × 13; `id` × 9 … |
| `source_refs` | list of strings | n = 5,322; pointers into upstream logs |
| `success_observed` | bool | n = 5,322; `true` × 5,221; `false` × 101 |
| `actor_label` | string | n = 5,221; `[Admin1]` × 5,217 |
| `change_summary` | string | n = 5,221; `Seite gelöscht.` × 5,217 |
| `page_held` | bool | n = 5,221; `true` × 3,971; `false` × 1,250 |
| `winning_clock`, `uncertainty_seconds`, `request_time`, `success_time`, `clock_delta_seconds`, `clock_note` | mixed | n = 5,221; clock bookkeeping for deletes and reverts |
| `write_date`, `rcs_date`, `recent_changes_time` | null | null wherever present |
| `related_event_id`, `relation_type`, `round_id` | mixed | set on 67 rows; `relation_type` is `first_recreation_of` |

### `labels.jsonl.gz`

**Overview.** 3,103 records, one per distinct editor label, with activity totals.

| Field | Type | What the data shows |
|---|---|---|
| `label` | string | 0–39 chars |
| `stored_revisions` | int | 1 to 899; 1,332 labels have exactly 1 |
| `first_write`, `last_write` | ISO UTC string | 2026-05-24 to 2026-07-02 |
| `stored_revision_ips`, `stored_revision_ip16` | int | distinct IPs (max 741) and /16 blocks (max 114) |
| `pages` | list of strings | page ids the label saved; 1 to 568 |
| `stored_revision_pages` | int | 1 to 568 |
| `wikis` | list of strings | `dse` × 3,013; `fractal` × 86; `probier` × 21; `dorfwiki` × 2 |
| `is_human_handle` | bool | `false` × 3,100; `true` × 3 |
| `save_requests`, `save_request_ips`, `save_request_ip16`, `save_request_pages` | int | request-log totals; `save_requests` 0 to 3,887 |
| `save_request_source` | string or null | `edit_actors.jsonl` × 3,040; null × 63 |

---

## `raw/collusion/other/`

Six files. None ships a README; two carry a `source` note inside the JSON, quoted below.

Relationship I verified: every id in `links.record_ids` exists in `records.id` (10,332 of the 13,703 records are referenced by at least one link).

### `records.jsonl.gz`

**Overview.** 13,703 records. Each is one distinct piece of text collected from a public site, with a list of where it was found. Field names describe it as "selected agent related text"; the `authorship` field is `not_independently_authenticated` on every row.

| Field | Type | What the data shows |
|---|---|---|
| `id` | string (64 hex) | unique |
| `text` | string | 10 to 135,743 chars, mean 597 |
| `source_text_sha256`, `hosting_text_sha256` | string | hashes; in sampled rows both equal `id` |
| `hosting_text_changed` | bool | `false` × 7,805; `true` × 5,898 |
| `body_withheld` | bool | `false` × 13,665; `true` × 38 |
| `authorship` | string | `not_independently_authenticated` × 13,703 |
| `selection_basis` | string | `publisher_selected_plus_task_or_exchange_signal` × 9,616; `task_or_exchange_signal` × 4,000; `prior_reviewed_task_reference` × 76; `linked_artifact` × 11 |
| `origins` | list of objects | 1 to 314 per record; 15,806 in total |

Each `origins[]` entry has: `source_id`, `site`, `title`, `url`, `source_date_literal`, `kind`, `original_text_sha256`, `response_quality`, `source_reference`.

- **`site`** (35 values): `prowiki.org/dse` × 10,899; `vanderbi.lt` × 2,721; `uoft.me` × 479; `goto.unm.edu` × 368; `paste.linuxiarz.pl` × 304; `wikiservice.at/probier` × 289; `wikiservice.at/fractal` × 133; and 28 smaller ones.
- **`kind`** (20 values): `revision_addition` × 11,324; `shortener_candidate` × 3,237; `shortener_record` × 539; `paste_candidate` × 208; `prior_paste` × 129; and 15 smaller ones.
- **`url`**: often a `https://collusion.wiki/explorer/page/…` address.

### `links.jsonl.gz`

**Overview.** 23,877 records, one per distinct URL found inside the texts in `records.jsonl.gz`.

| Field | Type | What the data shows |
|---|---|---|
| `url` | string | 9 to 1,364 chars |
| `host` | string | host part of the URL |
| `record_ids` | list of strings | records containing the link; 1 to 796 |
| `relation` | string | `link_in_selected_agent_related_text` × 23,877 |
| `followed` | bool | `false` × 23,877 |
| `source_url_sha256` | string | hash |
| `url_withheld` | bool | `false` × 16,084; `true` × 7,793 |

### `site-coverage.csv`

**Overview.** 143 rows, one per website, recording what was and was not collected from it. 14 columns.

| Column | What the data shows |
|---|---|
| `site` | display name, e.g. `DSEWiki`, `Probier`; 143 distinct |
| `host` | 122 distinct; `wikiservice.at` × 21 |
| `canonical_url` | one per site |
| `category` | `pastebins` × 37; `wikis` × 30; `shorteners` × 23; `relays` × 23; `documents` × 13; `hosting` × 9; `new_discord_posting_surface` × 8 |
| `prior_status` | 20 values; `unspecified_prior_status` × 46 |
| `compilation_status` | `no_selected_agent_text_in_compilation` × 64; `selected_agent_related_text_preserved` × 48; `responses_preserved_authorship_or_body_unresolved` × 24; `response_or_reference_only` × 7 |
| `selected_distinct_texts` | integer count; `0` × 95; the largest is 9,059 (DSEWiki) |
| `discord_urls` | integer count |
| `fresh_responses_saved` | integer count |
| `fresh_read_failures_or_redirects` | integer count |
| `specific_prior_gap_remains` | `False` × 85; `True` × 58 |
| `limitations` | a JSON array of caveat sentences, stored as a string |
| `prior_evidence` | a JSON array of file-path references, stored as a string |
| `scope` | 2 values; one covers 135 rows |

### `coverage-gaps.csv`

**Overview.** 110 rows with the **same 14 columns** as `site-coverage.csv`. All 110 `site` values are distinct. `compilation_status`: `no_selected_agent_text_in_compilation` × 64; `responses_preserved_authorship_or_body_unresolved` × 24; `selected_agent_related_text_preserved` × 15; `response_or_reference_only` × 7. `specific_prior_gap_remains`: `True` × 58, `False` × 52. I did not check whether its rows are a strict subset of `site-coverage.csv`.

### `other-wikis.json.gz`

**Overview.** One JSON object with keys `recovered` (`2026-09-07`), `source`, and `pages`. It holds edit histories for 8 pages on three other wikis.

Its `source` note says these are "the eight pages from publictestwiki, uncyclopedia and usemod that agent-swarm-site published on 2026-09-04", that the original inputs were not kept, and so each revision is recorded only as "the lines it added and removed, the save time, the /16 of the address". It also says no editor label exists for these.

- **`pages[]`** (8): `page_key`, `wiki`, `name`, `page_id`, `revisions[]`.
- **`revisions[]`**: `seq` (int), `time` (ISO UTC string), `time_grade` (`write_date` on all), `ip16` (string), `append` (bool), `added` (list of lines), `removed` (list of lines).

| Page | Revisions | Dates |
|---|---|---|
| `publictestwiki/Sandbox` | 52 | 2026-05-11 → 2026-05-27 |
| `publictestwiki/TestWiki:Community_portal` | 1 | 2026-05-27 |
| `publictestwiki/TestWiki:Sandbox` | 4 | 2026-05-11 → 2026-05-12 |
| `publictestwiki/TestWiki:Sandbox/TestOCR` | 1 | 2026-05-13 |
| `uncyclopedia/Uncyclopedia:Sandbox` | 17 | 2026-05-17 → 2026-05-18 |
| `usemod/AgentLinksBridgeUsemod` | 2 | 2026-05-26 |
| `usemod/SandBox` | 12 | 2026-05-11 → 2026-06-16 |
| `usemod/WikiSandbox` | 1 | 2026-05-27 |

### `shortener-logs.json.gz`

**Overview.** One JSON object with keys `read` (`2026-09-07`), `source`, and `sites`. It holds 499 short links from one URL shortener, `rmn.re`.

Its `source` note says `rmn.re` is a YOURLS 1.7.1 shortener whose admin listing was readable without login; that the log held 758 links when read; and that the 499 kept are those made between 2026-05-26 and 2026-06-21, of which 494 came from /16 address blocks "that also saved wiki edits". It says times are UTC and `clicks` is the site's count on the day it was read.

- **`sites[0]`**: `site`, `software`, `log`, `links_in_log` (758), `links[]`.
- **`links[]`** (499): `keyword` (the short code), `url` (destination), `title`, `time` (ISO UTC), `ip16`, `clicks` (int).
- **Dates:** 2026-05-26T18:01:12Z to 2026-06-21T20:22:22Z. **Distinct `ip16`:** 109.
- **Top destination hosts:** `viz.aihw.gov.au` × 192; `example.org` × 111; `md.succ.ai` × 32; `allorigins.hexlet.app` × 21; `www.sec.gov` × 15.

---

## `raw/redacted.jsonl.gz`

**Overview.** 189,579 records of short text items, mostly JavaScript, Python or HTTP-response snippets, with sensitive values replaced by placeholder tokens. **The file contains no documentation, no timestamps and no source field**, so what it is a record *of* cannot be determined from the file alone. What can be said from the content: many `payload` rows are code that sends HTTP requests (e.g. `fetch(...)` calls with API-key headers), and `response` rows look like the text returned.

| Field | Type | What the data shows |
|---|---|---|
| `id` | string | `R0000001` to `R0189579`, sequential |
| `cite` | string | the `id`, a colon, and 8 hex characters, e.g. `R0000001:865502a6`. Two sampled rows with identical `text` share the same suffix |
| `kind` | string | `payload` × 91,037; `recovered_text` × 75,534; `response` × 23,008 |
| `parent_id` | string or null | null × 128,454; otherwise another row's `id` |
| `time_utc` | null | null in **every** row |
| `tags` | string | empty × 189,542; otherwise semicolon-separated tags |
| `text` | string | 1 to 445,502 chars, mean 344 |

- **Parent links:** every `payload` has no parent. `recovered_text` rows point to a `payload` in 42,707 cases and have no parent in 32,826. `response` rows point to a `payload` in 18,417 cases and have no parent in 4,591.
- **Text length by kind (median / 95th percentile / max):** `payload` 159 / 1,567 / 445,502; `response` 83 / 846 / 26,617; `recovered_text` 72 / 762 / 171,011.
- **Tags** (37 tagged rows): `article-evidence` × 37; `g236-command` × 28; `g23619cmd.bin` × 18; `g23619scmd.bin` × 10; `slack-search` × 4; `appendix-request` × 3; plus `command-000001` … `command-000017`.
- **Redaction placeholders** take two forms. Bracketed typed tokens: `[REDACTED:destination:000002]`, with types including `destination` (116,646 occurrences), `opaque_fragment`, `opaque_marker_tail`, `source_identifier`, `source_path`, `query_value`, `runtime_identifier`, `jwt_claim_time`, `opaque_encoded_blob`, `secret_key`, `username`, `network_address`, `hf_repo`, `bearer_token`. Numbered tokens: those beginning `[SERVICE n` (58,408 occurrences, e.g. `[SERVICE 2 URL 1]`), `[CREDENTIAL n` (42,790), `[PROXY n` (23,885), and also `[USER n]`, `[EMAIL n]`, `[WEBHOOK n]`, `[SHORTENER CODE n]`, `[SERVICE HOST n]`, `[REDIRECT URL n]`.

---

## `raw/urlquery-agent-activity-2026-09-23.zip`

**Overview.** A zip of 16 files (41.5 MB uncompressed) in one folder, `urlquery-agent-activity-2026-09-22-v5/`. Per its README, it is a catalog of 38,160 public report links on urlquery.net with research classifications, and it contains "public report links and research metadata, with no full report JSON, response bodies, screenshots, submitted code, credentials, or private documents".

The README states the confidence values `significant` and `suggestive` "denote higher and moderate qualitative confidence in agent-like activity; they are not calibrated probabilities or verified actors". Every catalog row carries the caveat "Candidate evidence, not authenticated AI, OpenAI, RL-task or common-operator attribution. Submitted code does not establish successful execution."

| Member | Size | Contents |
|---|---|---|
| `README.md` | 5 KB | Describes coverage, counts, every file, and the two confidence changes made in this version |
| `reports.csv` | 17.7 MB | Main catalog, 38,078 rows |
| `additional-cited-reports.csv` | 39 KB | Supplemental catalog, 82 rows, same columns |
| `all-reports.csv` | 17.8 MB | Union of the two above, 38,160 rows. README: use this **or** the two components, not both |
| `all-report-links.txt` | 2.5 MB | 38,160 lines, one `https://urlquery.net/report/<uuid>` each |
| `report-sources.csv` | 3.4 MB | One data-source assignment per included report, 37,649 rows |
| `daily-counts.csv` | 9 KB | 325 rows, one per UTC date 2025-11-01 → 2026-09-21 |
| `daily-source-counts.csv` | 8 KB | 330 rows of date × data source |
| `selection-provenance.csv` | 13 KB | 71 rows explaining how the added reports were selected |
| `supplement-classifications.json` | 52 KB | The 82 supplemental classification decisions |
| `classification-overrides.json` | 2 KB | The 2 reports whose confidence was changed from `suggestive` to `significant` |
| `methods.json` | 21 KB | 52 collection-method definitions |
| `search-coverage.json` | 13 KB | 41 search-audit rows |
| `collection-summary.json` | 1 KB | Reconciled totals |
| `supplement-summary.json` | 0.4 KB | Totals for the supplement |
| `manifest.json` | 2 KB | Byte length and SHA-256 of every other file; snapshot date 2026-09-23 |

**Catalog columns** (`reports.csv`, `additional-cited-reports.csv`, `all-reports.csv`), with values from `all-reports.csv`:

| Column | What the data shows |
|---|---|
| `report_id` | UUID, unique |
| `report_url` | `https://urlquery.net/report/<report_id>` |
| `report_date_utc` | ISO UTC; 2023-09-22 to 2026-09-20. 37,242 of the rows fall in April–June 2026 |
| `timestamp_precision` | `second` on every row |
| `disposition` | `included` × 37,649; `review_required` × 432; `background` × 79 |
| `confidence` | `suggestive` × 31,182; `significant` × 6,467; blank × 511 |
| `broad_class` | `source_request` × 27,128; `custom_program` × 6,464; `indirection` × 4,568 |
| `why_included` | free text, 81 distinct values, e.g. "Related data source or exact task identifier: UNCTAD, UNCTAD proxy references." |
| `caveat` | one fixed sentence (quoted above) |

**`report-sources.csv`:** `report_id`, `report_date_utc`, `data_source`, `source_basis`, `matched_sources`. `data_source` has 40 values; the largest are `UNCTAD` × 19,319; `Thrill Data` × 5,100; `AIHW` × 4,844; `Woodlands House School` × 2,417; `Mapillary` × 1,080; `GBBC` × 773; `MAX budget documents` × 597; `Maryland school report cards` × 546. `source_basis`: `source_method` × 37,303; `unidentified` × 183; `external_source_tag` × 82; `selection_provenance` × 70; `supplement_review` × 11.

**`daily-counts.csv`:** `date_utc`, `significant`, `suggestive`, `newly_classified`, `total`, `source_request`, `indirection`, `custom_program`. Column sums: `total` 37,638; `significant` 6,467; `suggestive` 31,171. The largest single-day `total` is 2,239.

**`daily-source-counts.csv`:** `date_utc`, `data_source`, `reports`. Covers 140 distinct dates.

**`selection-provenance.csv`:** `report_id`, `source_batch` (one value, `daniel_20260923`), `group` (`Recognized source` × 43, `Boomlify` × 22, `Quidax` × 6), `source`, `record_kind`, `selection_basis`, `description`.

**`methods.json`:** a list of 52 objects with `id`, `label`, `query`, `markers`, `reason`, `default_confidence`, `broad_class`, `discovery_kind`, `requires_review`. Example: id `source:thrill`, query `http.url.domain:thrill-data.com`.

**`search-coverage.json`:** a list of 41 objects with `method_id`, `query`, `start`, `end`, `partitions`, `advertised_sum`, `unique_returned`, `advertised_minus_returned`, `failed_pages`, `status`.

**`supplement-classifications.json`:** `original_classifier_sha256` plus `decisions[]` (82), each with `report_id`, `source_batch`, `disposition`, `confidence`, `broad_class`, `basis`, `reason`, `classification_provenance`.

---

## `raw/us-canada-government-evidence-2026-09-30.zip`

**Overview.** A zip of 92 entries (245.6 MB uncompressed) under `us-canada-government-evidence-2026-09-30-v3/`. Its `README.txt` is the only documentation and says in full: "Evidence accompanying https://transluce.org/us-canada-gov. Folders are organized according to the sections of the post. Source URLs are included in the data files." I did not read that web page, so the purpose of each folder is known only from its name and contents.

There are 15 numbered folders. Each holds some combination of the file types below. `13-census` is an **empty folder**.

### File types in the archive

**`arquivo-captures.csv`** (11 folders). An index of web captures held by the arquivo.pt web archive. 13 columns: `record_number`, `captured_at_utc`, `archive_url`, `target_url`, `indexed_http_status`, `reviewed_origin_status`, `mime`, `archive_digest_sha1_base32`, `warc_filename`, `warc_offset`, `warc_record_length`, `collection`, `source_url_redacted`. These are capture metadata only; no page bodies.

**`sources.csv`** (13 folders). Lists the evidence files in the folder and where each came from. 5 columns: `file`, `source_url`, `captured_at_utc`, `http_status`, `source_sha256`. `file` is blank on some rows. Most `source_url` values are `arquivo.pt/wayback/…` replay addresses; a few point to `collusion.wiki`, `urlquery.net`, `web.archive.org` or `huggingface.co`.

**`responses/*.txt`** (10 folders, 50 files). Saved response bodies, 11 bytes to 7.3 KB each, named by a 16-hex-character id. The five I opened were: the text `Loading ...`; a "Record not found." page with a timing table; two JSON metadata documents containing `[REDACTED_AUDIT_IDENTIFIER]` placeholders; and a "Page Not Found" page.

**`urlquery-reports.csv`** (4 folders). One row per urlquery.net report. 8 columns: `report_id`, `report_url`, `report_at_utc`, `submitted_url`, `http_entries`, `browser_user_agent`, `source_json_sha256`, `json_url`.

**`urlquery-http.csv`** (4 folders). One row per HTTP request inside those reports. 12 columns: `report_id`, `http_entry_index`, `request_at_utc`, `method`, `url`, `http_status`, `response_size`, `response_mime`, `response_sha256`, `response_body_in_source_json`, `remote_peer_ip`, `user_agent`. `response_body_in_source_json` is `False` on every row in all four files. Unlike the collusion data, `remote_peer_ip` here is a full IP address.

**`benchmark-excerpt.json`** (2 folders). A single question copied from a public benchmark: keys `source` (`https://huggingface.co/datasets/google/deepsearchqa`), `zero_based_row`, `problem`, `problem_category`, `answer`, `answer_type`.

**`cited-wiki-revision.txt` / `cited-wiki-task.txt`** (3 folders). Plain-text copies of wiki page revisions. The two `cited-wiki-revision.txt` files start with a revision number, a timestamp, an editor label and a partly masked IP (`20.110.x.x`), followed by the page text.

**`response-excerpts.json`** (Maryland only). A list of 21 objects, each with `metadata` (13 keys including `timestamp_utc`, `school_id`, `school_name`, `status`, `warc_filename`, `decoded_post_json`, `replay_url`), `filters` (60 keys), and `graphs`, which is the literal string `WITHHELD`.

**`*.png`** (max-gov only): `may27-links.png` and `pdf-to-json.png`. The `file` utility identifies both as WebP images, 1280×1024, despite the `.png` extension. **I did not view them.** `sources.csv` gives a urlquery.net source URL for each.

### Folder by folder

| Folder | Files | Capture rows | Capture dates (UTC) | Main target host(s) |
|---|---|---|---|---|
| `01-education` | captures, sources (16 rows), 15 responses, benchmark excerpt | 219,923 | 2026-06-16 → 2026-06-17 | `civilrightsdata.ed.gov` |
| `02-canada` | captures, sources (13), 11 responses | 899 | 2026-05-28 → 2026-06-09 | `recherche-collection-search.bac-lac.canada.ca` |
| `03-kansas` | captures, sources (2), 2 responses | 36,579 | 2026-05-07 (about 3 hours) | `www.kansasmemory.gov` |
| `04-illinois` | captures, sources (8), 7 responses | 251 | 2026-04-19 → 2026-05-01 | `iquery.illinois.gov`; also a bare IP, 61 rows |
| `05-maryland` | captures, sources (3), response-excerpts, urlquery reports (2) and http (124) | 295,945 | 2026-03-02 → 2026-05-06 | `reportcard.msde.maryland.gov` |
| `06-new-york` | captures, sources (3), 2 responses, cited-wiki-task | 715 | 2026-05-16 → 2026-05-18 | `data.nysed.gov` |
| `07-texas` | urlquery reports (7) and http (242) only | none | reports on 2026-05-17 | `tabexternal.dshs.texas.gov` |
| `08-california` | captures, sources (8), 2 responses | 111 | 2026-05-26 | `cal-access.sos.ca.gov` |
| `09-max-gov` | captures, sources (3), cited-wiki-revision, 2 images, urlquery reports (719) and http (2,371) | 26 | 2026-05-26 | `portal.max.gov` |
| `10-navy` | captures, sources (3), 3 responses | 3,729 | 2026-04-23 → 2026-05-18 | `www.history.navy.mil` |
| `11-justice` | captures, sources (4), 3 responses, benchmark excerpt | 40 | 2026-05-25 → 2026-05-31 | `www.ojjdp.gov` |
| `12-bea` | captures, sources (4), 4 responses | 3,011 | 2026-06-16 → 2026-06-18 | `apps.bea.gov` |
| `13-census` | *(empty)* | none | | |
| `14-sec` | sources (1), cited-wiki-revision, urlquery reports (605) and http (6,930) | none | reports on 2026-06-18 | `www.sec.gov` |
| `15-cdc` | sources (1), 1 response | none | source captured 2026-07-18 | `wonder.cdc.gov` (via web.archive.org) |

Details worth knowing before using the capture indexes:

- **HTTP status mix varies sharply by folder.** Kansas is 32,376 × `504` out of 36,579. Maryland is 274,821 × `302`. Education is 219,510 × `200`. Navy is 2,162 × `404` out of 3,729.
- **`reviewed_origin_status` is blank everywhere except Illinois**, where it is filled on all 251 rows.
- **`source_url_redacted` is `True` on some rows:** Canada 165, BEA 20, Illinois 5, Maryland 1.
- **`collection`** is `SAWP5` on all rows except 2 in New York (`PATCHING2026`).
- **The two benchmark excerpts** are row 250 (a question about `civilrightsdata.ed.gov` school data) and row 260 (a question about FBI and National Safety Council statistics).
- **The urlquery reports** in `09-max-gov` span 2026-05-25 → 2026-05-27, with submitted URLs mostly on `markdown.new` (340) and `portal.max.gov` (173). Those in `14-sec` all fall on 2026-06-18, mostly `www.sec.gov` (382).
