import sys
import os
import argparse
from .engine import condense

def main():
    parser = argparse.ArgumentParser(
        prog="context-condenser",
        description="Ultra-fast local BM25 context compressor for AI coding agents."
    )
    parser.add_argument("file", nargs="?", help="Input file path (or read from standard input)")
    parser.add_argument("-q", "--query", default="", help="Focus query or keyword terms (default: error/fail/crash)")
    parser.add_argument("-m", "--max-lines", type=int, default=60, help="Maximum relevant lines to extract")
    parser.add_argument("-w", "--window", type=int, default=2, help="Context lines around each match")
    args = parser.parse_args()

    if args.file and os.path.isfile(args.file):
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()
    else:
        raw_text = sys.stdin.read()

    print(condense(raw_text, query=args.query, max_lines=args.max_lines, window=args.window))

if __name__ == "__main__":
    main()
