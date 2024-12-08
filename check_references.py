#!/usr/bin/env python
"""
Paper cross reference checker
"""
import sys, os, pathlib, pymupdf
from os import listdir
from os.path import isfile, join
import csv


def title_filter(title: str):
    return title.strip() != ""


def main():
    paper_txt_dir = "./papers_as_text"
    output = "./cross_references.csv"
    titles = []

    with open("titles.txt", "r") as file:
        titles = list(
            sorted(filter(title_filter, file.read().split("\n")), key=str.lower)
        )

    rows = []
    for title in titles:
        row = [title]
        for _ in titles:
            row.append("FALSE")
        rows.append(row)

    file_names = [
        f
        for f in sorted(listdir(paper_txt_dir), key=str.lower)
        if isfile(join(paper_txt_dir, f))
    ]

    for row_idx, file_name in enumerate(file_names):
        with open(join(paper_txt_dir, file_name), "r") as file:
            data = file.read()

            for col_idx, title in enumerate(titles):
                if row_idx == col_idx:
                    continue
                if title.lower().strip() in data.lower().strip():
                    rows[row_idx][col_idx + 1] = "TRUE"

    with open(output, "w") as csvf:
        writer = csv.writer(csvf, dialect="excel-tab")
        writer.writerow([""] + titles)  # Columns
        writer.writerows(rows)


if __name__ == "__main__":
    main()
