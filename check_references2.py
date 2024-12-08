#!/usr/bin/env python
"""
Paper cross reference checker
"""
import sys, os, pathlib
from os import listdir
from os.path import isfile, join
from glob import glob
import re
import csv
import pymupdf


def title_filter(title: str):
    return title.strip() != ""


CANON_REMOVECHARS = re.compile("[^a-zA-Z0-9]")


def canonizalize(s: str):
    return CANON_REMOVECHARS.sub("", s).lower()


def main():
    paper_txt_dir = "./papers_as_text"
    output = "./cross_references2.csv"
    titles = []

    with open("titles.txt", "r") as file:
        titles = list(
            sorted(filter(title_filter, file.read().split("\n")), key=str.lower)
        )

    docs = dict()
    for filename, title in zip(
        sorted(glob("papers_as_text/*"), key=str.lower), sorted(titles, key=str.lower)
    ):
        with open(filename) as file:
            text = file.read()
            docs[title] = canonizalize(text)

    rows = []

    for title, doc in docs.items():
        row = []
        row.append(title)
        for check_title in docs.keys():
            if check_title != title and canonizalize(check_title) in doc:
                row.append("TRUE")
            else:
                row.append("FALSE")
        rows.append(row)

    with open(output, "w") as csvf:
        writer = csv.writer(csvf, dialect="excel-tab")
        writer.writerow([""] + list(docs.keys()))  # Columns
        writer.writerows(rows)


if __name__ == "__main__":
    main()
