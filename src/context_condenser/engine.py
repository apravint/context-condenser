import sqlite3
import re
from typing import List, Tuple, Set

def create_in_memory_fts(lines: List[str]) -> sqlite3.Connection:
    """Creates an in-memory SQLite database indexed with FTS5 and Porter stemming."""
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("CREATE VIRTUAL TABLE logs_fts USING fts5(line_no UNINDEXED, content, tokenize='porter unicode61');")
    
    for idx, line in enumerate(lines, 1):
        cur.execute("INSERT INTO logs_fts(line_no, content) VALUES (?, ?);", (idx, line))
    conn.commit()
    return conn

def condense(raw_text: str, query: str = "", max_lines: int = 50, window: int = 2) -> str:
    """
    Compresses text by ranking lines using BM25 relevance against search terms,
    preserving local context windows while stripping redundant noise.
    """
    lines = raw_text.splitlines()
    if not lines:
        return ""
    
    # If text is already small, return untouched
    if len(lines) <= max_lines and len(raw_text) < 4000:
        return raw_text

    search_query = query.strip()
    if not search_query:
        search_query = "error OR fail OR failed OR warning OR fatal OR exception OR critical OR crash"

    # Clean query for FTS5 syntax
    safe_terms = re.findall(r'[a-zA-Z0-9_\-\.]+', search_query)
    if not safe_terms:
        safe_terms = ["error", "fail", "warning"]
    
    fts_expression = " OR ".join(safe_terms)

    conn = create_in_memory_fts(lines)
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT line_no, bm25(logs_fts) as score FROM logs_fts WHERE logs_fts MATCH ? ORDER BY score LIMIT ?;",
            (fts_expression, max_lines)
        )
        matched_rows = cur.fetchall()
    except Exception:
        # Fallback to simple matching if syntax error in query
        matched_rows = []
        for idx, line in enumerate(lines, 1):
            if any(term.lower() in line.lower() for term in safe_terms):
                matched_rows.append((idx, 0.0))
                if len(matched_rows) >= max_lines:
                    break

    if not matched_rows:
        head = lines[:20]
        tail = lines[-20:]
        return f"[Context Condenser: {len(lines)} lines ({len(raw_text)} bytes) -> No critical errors found. Showing head & tail]:\n" + \
               "\n".join(head) + "\n\n... [snip] ...\n\n" + "\n".join(tail)

    selected_indices: Set[int] = set()
    for row in matched_rows:
        target_idx = row[0] - 1
        for offset in range(-window, window + 1):
            idx = target_idx + offset
            if 0 <= idx < len(lines):
                selected_indices.add(idx)

    sorted_indices = sorted(selected_indices)
    output_chunks = []
    prev_idx = None
    original_size = len(raw_text.encode('utf-8'))
    
    for idx in sorted_indices:
        if prev_idx is not None and idx > prev_idx + 1:
            output_chunks.append(f"... [{idx - prev_idx - 1} lines compressed] ...")
        output_chunks.append(f"{idx + 1:5d} | {lines[idx]}")
        prev_idx = idx

    condensed_text = "\n".join(output_chunks)
    condensed_size = len(condensed_text.encode('utf-8'))
    reduction = (1 - (condensed_size / max(original_size, 1))) * 100

    header = (
        f"⚡ [Context Condenser: Compressed {len(lines)} lines ({original_size} bytes) "
        f"-> {len(sorted_indices)} lines ({condensed_size} bytes) | {reduction:.1f}% reduction]:\n"
        f"Query: '{search_query}'\n"
        f"{'-'*72}\n"
    )
    return header + condensed_text
