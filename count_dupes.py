#!/usr/bin/env python
"""
Paper duplicate count script
"""
from __future__ import annotations
import os
import sys
import glob
from row import row_filter
from database_parsing import DBS


def main(args: list[str]):
    rows = []
    n_hits = 0
    n_duplicates = 0

    for prefix, func in DBS:
        for name in sorted(glob.glob(f"queries/{prefix}_*")):
            query_id = os.path.splitext(os.path.split(name)[1])[0]
            with open(name, "r") as f:
                for row in filter(row_filter, func(f, query_id)):
                    n_hits += 1
                    if row in rows:
                        # print(f"  Dropping dupe {row}")
                        n_duplicates += 1
                        continue
                    rows.append(row)

    print(f"Total hits: {n_hits}")
    print(f"Removed {n_duplicates} duplicates")
    print(f"New total hits: {n_hits - n_duplicates}")


if __name__ == "__main__":
    main(sys.argv[1:])
