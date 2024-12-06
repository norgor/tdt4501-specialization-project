from __future__ import annotations
import csv
import io
import itertools
import bibtexparser
from row import Row, RowIdent


def scopus(data: io.TextIOWrapper, query_id: str) -> list[Row]:
    reader = csv.DictReader(data)
    return [
        Row(
            query_id,
            index,
            row["Title"],
            RowIdent(row.get("DOI"), row.get("ISSN"), row.get("ISBN")),
            row["Link"],
            int(row["Year"]),
        )
        for (index, row) in zip(itertools.count(), reader)
    ]


def ieee(data: io.TextIOWrapper, query_id: str) -> list[Row]:
    reader = csv.DictReader(data)
    return [
        Row(
            query_id,
            index,
            row["Document Title"],
            RowIdent(row.get("DOI"), row.get("ISSN"), row.get("ISBNs")),
            row["PDF Link"],
            int(row["Publication Year"]),
        )
        for (index, row) in zip(itertools.count(), reader)
    ]


def acm_dl(data: io.TextIOWrapper, query_id: str) -> list[Row]:
    reader = bibtexparser.load(data)
    return [
        Row(
            query_id,
            index,
            row["title"],
            RowIdent(row.get("doi"), row.get("issn"), row.get("isbn")),
            row.get("url"),
            int(row["year"]),
        )
        for (index, row) in zip(itertools.count(), reader.entries)
    ]


def web_of_science(data: io.TextIOWrapper, query_id: str) -> list[Row]:
    reader = csv.DictReader(data, dialect="excel-tab")
    return [
        Row(
            query_id,
            index,
            row["TI"],
            RowIdent(row.get("DI"), row.get("SN"), row.get("BN")),
            f"https://www.webofscience.com/wos/woscc/full-record/{row["UT"]}",
            int(row["PY"]),
        )
        for (index, row) in zip(itertools.count(), reader)
    ]


# list of databases from most to least specific (for dedupe)
dbs = (
    ("IEEE", ieee),
    ("SCP", scopus),
    ("WOS", web_of_science),
    ("ACM", acm_dl),
)
