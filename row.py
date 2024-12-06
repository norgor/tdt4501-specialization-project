from __future__ import annotations
import json
from scholarly import scholarly, MaxTriesExceededException
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
        if (
            self.type is None
            or self.value is None
            or other.type is None
            or other.value is None
        ):
            return False
        return self.type == other.type and self.value == other.value


@dataclass
class RowInfo:
    num_citations: int | None


class Row:
    CSV_FIELDNAMES = ("QueryID", "Index", "ID", "Title", "URL", "Year", "Citations")
    CANONTITLE_REMOVECHARS = re.compile("[^a-zA-Z0-9]")

    def __init__(
        self,
        query_id: str,
        index: int,
        title: str,
        ident: RowIdent,
        url: str,
        year: int,
    ):
        self.query_id = query_id
        self.query_index = index
        self.title = BeautifulSoup(title, features="lxml").get_text()
        self.ident = ident
        self.url = url
        self.year = year
        self.__canontitle = Row.CANONTITLE_REMOVECHARS.sub("", self.title).lower()

    @property
    def info(self) -> RowInfo:
        l = scholar_lookup(self)
        return RowInfo(l["num_citations"]) if l else RowInfo(None)

    def to_csv_dict(self):
        return dict(
            zip(
                Row.CSV_FIELDNAMES,
                (
                    self.query_id,
                    self.query_index + 1,
                    self.ident,
                    self.title,
                    self.url,
                    self.year,
                    self.info.num_citations or 0,
                ),
            )
        )

    def __hash__(self) -> int:
        return hash(self.__canontitle)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Row)
            and self.ident == other.ident
            or self.__canontitle == other.__canontitle
        )

    def __str__(self):
        return f"[{self.ident}] {self.title} ({self.__canontitle})"


def scholar_lookup(row: Row):
    if not hasattr(scholar_lookup, "cache"):
        print("Loading scholar cache")
        try:
            with open(".cache.scholar", "r") as cachefile:
                scholar_lookup.cache = json.load(cachefile)
            print(f"Scholar cache loaded ({len(scholar_lookup.cache)} entries)")
        except FileNotFoundError:
            print("Scholar cache not found")
            scholar_lookup.cache = dict()

    if row.ident.type == "DOI" and str(row.ident) not in scholar_lookup.cache:
        v = None
        while True:
            try:
                print(row.ident.value)
                v = scholarly.search_single_pub(row.ident.value)
                break
            except MaxTriesExceededException as e:
                print(e)
            except IndexError:
                print("IndexError within search - assuming does not exist")
                break

        scholar_lookup.cache[str(row.ident)] = v
        print(f"Saving scholar cache ({len(scholar_lookup.cache)} entries)")
        with open(".cache.scholar", "w") as cachefile:
            json.dump(scholar_lookup.cache, cachefile, indent="\t")

    return scholar_lookup.cache.get(str(row.ident))


def row_filter(row: Row):
    return row.year >= 2010
