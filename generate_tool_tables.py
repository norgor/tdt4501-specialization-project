#!/usr/bin/env python
import sys
import json

ALIASES = {
	"Disassembly": {
		"Disassembly",
		'Instruction Boundaries',
		'Function Signatures',
		'Binary Pointer Analysis',
	},
	"Decompilation": {
		"Decompilation",
		'High level view',
	},
	"Structural Analysis": {
		'Function Boundaries',
		'Function recognition',
		'Overlapping Functions and Basic Blocks',
		'Basic Block Identification',
		'Function recognition with and without obfuscation of code',
		'Pattern Matching to Find Function Addresses',
	},
	"Anti-Anti-RE": {
		"Code packing",
		"Obfuscated Constants",
		"Embedded Virtual Machines",
		'Virtualization based obfuscation',
		'Call stack tampering',
		'Non-returning calls',
		'Ambiguous Code and Data',
		'Stolen Bytes',
		'Obfuscated Calls and Returns',
		'Disassembler Fuzz Testing',
		'Exception-Based Control Transfers',
		'Self-Checksumming',
		'Calling-Convention Violations',
	},
	"Binary Rewriting": {
		'Binary Rewriting',
		'Instrumentation of Executable',
		'Runtime Binary Patching',
		'Memory Leak Observation',
		'Low Level Binary Analysis and Rewriting',
		'All tools mentionedin table for Binary rewriting',
	},
	'Binary Lifting': {
		'Binary Lifting',
		'Binary Lifting to LLVM IR',
	},
	"Semantic Analysis": {
		'Semantic Extraction',
		'Static Value Set Analysis (VSA)',
		'Extracting Semantics',
	},
 
	None: {
		"Emulation",
		'Specification Adherance Monitoring',
		'Data Mining',
	},
}

VARMAP = {
	"ATOM": "Atom",
    "Angr": "Angr",
	"BAP": "BAP",
    "BIRD": "Bird",
	"BinJuice": "BinJuice",
	"Binary Ninja": "BinaryNinja",
	"BitBlaze": "BitBlaze",
	"BitShred": "BitShred",
	"ByteWeight": "ByteWeight",
	"DREAM": "DREAM",
	"Diablo": "Diablo",
	"DynamoRIO": "DynamoRIO",
	"Dyninst": "DynInst",
	"Ghidra": "Ghidra",
	"IDA Pro": "IDAPro",
	"Jakstab": "JakStab",
	"PEBIL": "Pebil",
	"Phoenix": "Phoenix",
	"Pin": "Pin",
	"QEMU": "QEMU",
	"Radare2": "RadareTwo",
	"Rev.ng": "RevNg",
	"Rotalumé": "Rotalume",
	"SecondWrite": "SecondWrite",
	"UQBT": "UQBT",
	"Uroboros": "Uroboros",
	"VMAttack": "VMAttack",
	"Valgrind": "Valgrind",
	"Vulcan": "Vulcan",
	"objdump": "Objdump",
	"ptrace": "Ptrace",
}

def find_feature_from_circumstance(s):
	for (name, aliases) in ALIASES.items():
		if s in aliases:
			return name
	return None

def generate_table(i, o):
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
		tools[name] = {"features": set()}
		for circumstance in tool["circumstances"]:
			feature = find_feature_from_circumstance(circumstance)
			if feature is not None:
				features.add(feature)
				tools[name]["features"].add(feature)

	features = list(sorted(features))

	pn(f"\\begin{{tabular}}{{{"l" * (len(features) + 1)}}}")
	pn("\\toprule")
	pn("\\thead{Tool}")
	for feature in features:
		p(f" & \\theadr{{{feature}}}")
	p("\\hspace{4em}")
	pn("\\\\")
	pn("\\midrule")

	for (name, props) in sorted(tools.items(), key=lambda x: x[0]):
		p(f"\\varTool{VARMAP[name]}{{}}")
		for feature in features:
			if feature in props["features"]:
				p(" & \\cross")
			else:
				p(" & ")
		pn("\\\\")
	pn("\\bottomrule")
	pn("\\end{tabular}")




def main():
	generate_table(sys.stdin, sys.stdout)

if __name__ == "__main__":
	main()
