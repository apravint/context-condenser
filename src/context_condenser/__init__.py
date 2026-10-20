"""
context-condenser: Ultra-fast local BM25 context compression for AI coding agents.
"""

__version__ = "0.1.0"

from .engine import condense, create_in_memory_fts

__all__ = ["condense", "create_in_memory_fts"]
