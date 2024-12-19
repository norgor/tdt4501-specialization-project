#!/usr/bin/env python
import sys
import json
from tools_tablegen import ALIASES

def find_feature_from_circumstance(s):
	for (name, aliases) in ALIASES.items():
		if s in aliases:
			return name
	return None

def show(i, o):
	def pn(*values):
		print(*values, file=o)

	def p(*values):
		print(*values, file=o, end="")

	cited_tools = json.load(i)
	tools = dict()
	features = set()
	for (name, tool) in cited_tools.items():
		if tool["citation_count"] < 2:
			continue
		tools[name] = {"features": dict()}
		for (citation, circumstances) in tool["citations"].items():
			for circumstance in circumstances:
				feature = find_feature_from_circumstance(circumstance)
				if feature is not None:
					features.add(feature)
					tools[name]["features"].setdefault(feature, dict()).setdefault(circumstance, set()).add(citation)

	features = list(sorted(features))

	for feature in features:
		pn(f"{feature}:")
		circumstance_tools = dict()
		for (name, props) in tools.items():
			if feature in props["features"].keys():
				for (circumstance, citations) in props["features"][feature].items():
					circumstance_tools.setdefault("Any", dict()).setdefault(name, set()).update(citations)
					circumstance_tools.setdefault(circumstance, dict()).setdefault(name, set()).update(citations)
		for (circumstance, tool_citations) in sorted(circumstance_tools.items(), key=lambda x: x[0]):
			pn(f"\t{circumstance}:")
			for (name, citations) in sorted(tool_citations.items(), key=lambda x: x[0]):
				citation_str = ", ".join(citations)
				if len(citation_str) > 0:
					citation_str = f"\\cite{{{citation_str}}}"
				print(f"\t\t{name} {citation_str}")

def main():
	show(sys.stdin, sys.stdout)

if __name__ == "__main__":
	main()
