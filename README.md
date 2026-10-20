# ⚡ context-condenser

> **Ultra-fast, local-first context compressor for AI coding agents.**  
> Shrinks terminal logs, git diffs, test outputs, and large files by up to **98%** with **0 LLM calls, 0 token costs, and 0 network latency**.

[![PyPI version](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org/project/context-condenser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](https://python.org)

---

## 🎯 The Problem

AI coding agents (Claude Code, Cursor, Aider, Copilot, Antigravity) easily blow their context windows when running command-line tools:
* Dumping a 500-line `journalctl` or test runner output wastes **20,000+ tokens**.
* Pushing massive `git diff` outputs degrades model reasoning and triggers premature session compaction.
* Calling expensive LLM summarizers adds latency, token costs, and rate-limit bottlenecks.

## 💡 The Solution

`context-condenser` indexes raw text instantly into an in-memory **SQLite FTS5 full-text database with BM25 relevance ranking and Porter stemming**. It extracts the exact lines matching your intent, attaches surrounding context windows, and snips out irrelevant repetitive noise.

```text
⚡ [Context Condenser: Compressed 500 lines (54,200 bytes) -> 24 lines (1,840 bytes) | 96.6% reduction]:
Query: 'error OR failed OR crash'
------------------------------------------------------------------------
   42 | 2026-10-20 12:04:12 [DEBUG] Connecting to redis cluster node 0...
   43 | 2026-10-20 12:04:13 [ERROR] RedisConnectionTimeout: Failed to acquire lock on session_id:9901
   44 | 2026-10-20 12:04:13 [DEBUG] Retrying connection attempt 1/3...
... [148 lines compressed] ...
  192 | 2026-10-20 12:04:19 [FATAL] WorkerThread: Panic: Unhandled exception in dispatch pipeline
  193 |    at engine.rs:341 in process_event()
```

---

## 🚀 Installation

```bash
pip install context-condenser
```
Or run directly with `pipx` or as a standalone CLI:
```bash
pipx run context-condenser
```

---

## 💻 CLI Usage

### Pipe Any Terminal Output
```bash
# Condense massive systemd logs
journalctl -n 500 --no-pager | context-condenser -q "fail OR error"

# Condense huge git diffs to focus on authentication logic
git diff HEAD~5 | context-condenser -q "auth OR token OR permission"

# Condense test runner traces
pytest | context-condenser -q "FAILED OR Error"
```

### Compress Local Files
```bash
context-condenser /var/log/syslog -q "OOM" -m 30 -w 3
```

### CLI Flags
| Flag | Default | Description |
|---|---|---|
| `-q`, `--query` | `error OR fail OR crash` | Search terms or keyword focus |
| `-m`, `--max-lines` | `60` | Maximum matching lines to preserve |
| `-w`, `--window` | `2` | Context lines preserved above & below each match |

---

## 🐍 Python SDK Usage

```python
from context_condenser import condense

raw_logs = open("heavy_test_output.log").read()

# Condense by 90%+ with custom relevance query
compressed = condense(raw_logs, query="TypeError OR AssertionError", max_lines=20, window=2)
print(compressed)
```

---

## 🧪 Testing

```bash
python3 -m unittest discover tests
```

---

## 📄 License

MIT © [Ayyappa Pravin](https://github.com/apravint)
