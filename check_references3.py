#!/usr/bin/env python

import crossref.restful
import json


def main():
    with open("ref_idents.txt") as f:
        dois = [line.split(":")[1].strip() for line in f.readlines()]

    works = crossref.restful.Works()

    all_works = [works.doi(doi) for doi in dois]
    refs = dict()
    for work in all_works:
        print(work)
        workrefs = set()
        for r in work["reference"]:
            if "DOI" in r:
                workrefs.add(r["DOI"])
        refs[work["DOI"]] = workrefs

    print(refs)


if __name__ == "__main__":
    main()
