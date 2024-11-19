#!/usr/bin/env python
"""
Paper coalescing script
"""
from __future__ import annotations
import os
import sys
import glob
import csv
import io
import itertools
import bibtexparser
import re
import functools
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
from scholarly import scholarly, ProxyGenerator, MaxTriesExceededException
from typing import Self
from dataclasses import dataclass

def scholar_lookup(row: Row):
	if not hasattr(scholar_lookup, "cache"):
		print("Loading scholar cache")
		try:
			with open(".cache.scholar" , "r") as cachefile:
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
		with open(".cache.scholar" , "w") as cachefile:
			json.dump(scholar_lookup.cache, cachefile, indent="\t")

	return scholar_lookup.cache.get(str(row.ident))
		
def row_filter(row: Row):
	return row.year >= 2010

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

	def __init__(self, query_id: str, index: int, title: str, ident: RowIdent, url: str, year: int):
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
					self.query_index+1,
					self.ident,
					self.title,
					self.url,
					self.year,
					self.info.num_citations
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


def main(args: list[str]):
	#pg = ProxyGenerator()
	#pg.FreeProxies(timeout=10, wait_time=1200)
	#scholarly.use_proxy(pg)

	# list of databases from most to least specific (for dedupe)
	dbs = (
		("IEEE", ieee),
		("SCP", scopus),
		("WOS", web_of_science),
		("ACM", acm_dl),
	)
	rows = []
	n_duplicates = 0

	for prefix, func in dbs:
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
