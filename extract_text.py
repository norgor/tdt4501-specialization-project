#!/usr/bin/env python
"""
Paper cross reference checker
"""
import sys, os, pathlib, pymupdf
from os import listdir
from os.path import isfile, join


def main():
    paper_dir = "./papers"
    output_dir = "./papers_as_text"
    titles: list[str] = []

    file_names = [f for f in listdir(paper_dir) if isfile(join(paper_dir, f))]

    for file_name in file_names:
        with pymupdf.open(join(paper_dir, file_name)) as doc:
            text = chr(12).join([page.get_text() for page in doc])
            title = doc.metadata["title"]
            if title.strip() == "":
                title = text.split("\n")[0]
            titles.append(title)
            # write as a binary file to support non-ASCII characters
            pathlib.Path(join(output_dir, (title + ".txt"))).write_bytes(text.encode())

    with open("titles.txt", "w") as f:
        for title in sorted(titles, key=str.lower):
            # if title.strip() != "":
            f.write(f"{title}\n")


if __name__ == "__main__":
    main()
