#!/usr/bin/env python
"""
Paper year filter count script
"""
from __future__ import annotations
import os
import sys
import glob
from row import row_filter
from database_parsing import DBS


def main(args: list[str]):
    for prefix, func in DBS:
        database_hit_count = 0
        for name in sorted(glob.glob(f"queries/{prefix}_*")):
            query_id = os.path.splitext(os.path.split(name)[1])[0]
            with open(name, "r") as f:
                query_hit_count = 0
                for _ in filter(row_filter, func(f, query_id)):
                    query_hit_count += 1
        
                print(f"{query_hit_count}")
                database_hit_count += query_hit_count

        print("---")


if __name__ == "__main__":
    main(sys.argv[1:])
