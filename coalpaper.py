#!/usr/bin/env python
"""
Paper coalescing script
"""
import os
import sys
import glob
import csv
import io
import itertools
import bibtexparser
import re
from bs4 import BeautifulSoup
from typing import Self
from dataclasses import dataclass

class RowIdent:
    def __init__(self, doi: str | None, issn: str | None, isbn: str | None):
        if doi:
            self.type = "DOI"
            self.value = doi
        elif issn:
            self.type = "ISSN"
            self.value = issn
        elif isbn:
            self.type = "ISBN"
            self.value = isbn
        else:
            self.type = None
            self.value = None

    def __str__(self) -> str:
        if self.type and self.value:
            return f"{self.type}:{self.value}"
        return ""
    
    def __hash__(self) -> int:
        return hash((self.type, self.value))

    def __eq__(self, other: Self) -> bool:
        if self.type is None or self.value is None or other.type is None or other.value is None:
            return False
        return self.type == other.type and self.value == other.value
        

        

@dataclass
class Row:
    CSV_FIELDNAMES = ("EntryID", "ID", "Title", "URL", "YEAR")
    CANONTITLE_REMOVECHARS = re.compile("[^a-zA-Z0-9]")

    query_id: str
    index: int
    title: str
    ident: RowIdent
    url: str
    year: str

    def to_csv_dict(self):
        return dict(zip(Row.CSV_FIELDNAMES, (
            f"{self.query_id}_{self.index+1}", self.ident, self.title, self.url, self.year
        )))
    
    def __canontitle(self) -> str:
        return Row.CANONTITLE_REMOVECHARS.sub('', self.title).lower()

    def __hash__(self) -> int:
        return hash(self.__canontitle())

    def __eq__(self, other) -> bool:
        return isinstance(other, Row) and self.ident == other.ident or self.__canontitle() == other.__canontitle()

    def __str__(self):
        return f"[{self.ident}] {self.title} ({self.__canontitle()})"

def scopus(data: io.TextIOWrapper, query_id: str) -> list[Row]:
    reader = csv.DictReader(data)
    return [Row(query_id, index, row["Title"], RowIdent(row.get("DOI"), row.get("ISSN"), row.get("ISBN")), row["Link"], row["Year"]) for (index, row) in zip(itertools.count(), reader)]

def ieee(data: io.TextIOWrapper, query_id: str) -> list[Row]:
    reader = csv.DictReader(data)
    return [Row(query_id, index, row["Document Title"], RowIdent(row.get("DOI"), row.get("ISSN"), row.get("ISBNs")), row["PDF Link"], row["Publication Year"]) for (index, row) in zip(itertools.count(), reader)]

def acm_dl(data: io.TextIOWrapper, query_id: str) -> list[Row]:
    reader = bibtexparser.load(data)
    return [Row(query_id, index, row["title"], RowIdent(row.get("doi"), row.get("issn"), row.get("isbn")), row.get("url"), row["year"]) for (index, row) in zip(itertools.count(), reader.entries)]

def web_of_science(data: io.TextIOWrapper, query_id: str) -> list[Row]:
    reader = csv.DictReader(data, dialect="excel-tab")
    return [Row(query_id, index, BeautifulSoup(row["TI"]).get_text(), RowIdent(row.get("DI"), row.get("SN"), row.get("BN")), f"https://www.webofscience.com/wos/woscc/full-record/{row["UT"]}", row["PY"]) for (index, row) in zip(itertools.count(), reader)]

def main(args: list[str]):
    # list of databases from most to least specific (for dedupe)
    dbs = (
        ("ACM", acm_dl),
        ("IEEE", ieee),
        ("SCP", scopus),
        ("WOS", web_of_science)
    )
    rows = []
    n_duplicates = 0
    
    for (prefix, func) in dbs:
        for name in glob.glob(f"queries/{prefix}_*"):
            query_id = os.path.splitext(os.path.split(name)[1])[0]
            print(f"Processing {name}...")
            with open(name, "r") as f:
                for row in func(f, query_id):
                    if row in rows:
                        print(f"  Dropping dupe {row}")
                        n_duplicates += 1
                        continue
                    rows.append(row)

    
    with open("coalpaper.csv", "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=Row.CSV_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_csv_dict())
    
    print(f"Removed {n_duplicates} duplicates")
        

if __name__ == "__main__":
    main(sys.argv[1:])
