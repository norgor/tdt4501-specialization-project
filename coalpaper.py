#!/usr/bin/env python
"""
Paper coalescing script
"""
from __future__ import annotations
import os
import sys
import glob
import csv
from tqdm import tqdm
from row import Row, row_filter
from database_parsing import DBS


def main(args: list[str]):
    rows = []
    n_duplicates = 0

    for prefix, func in DBS:
        for name in sorted(glob.glob(f"queries/{prefix}_*")):
            query_id = os.path.splitext(os.path.split(name)[1])[0]
            print(f"Processing {name}...")
            with open(name, "r") as f:
                for row in filter(row_filter, func(f, query_id)):
                    if row in rows:
                        print(f"  Dropping dupe {row}")
                        n_duplicates += 1
                        continue
                    rows.append(row)

    with open("coalpaper.csv", "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=Row.CSV_FIELDNAMES)
        writer.writeheader()
        for row in tqdm(rows):
            writer.writerow(row.to_csv_dict())

    print(f"Removed {n_duplicates} duplicates")


if __name__ == "__main__":
    main(sys.argv[1:])
