#!/usr/bin/env python

import sys
import csv
from collections import OrderedDict

CELLMAP = {
	"TRUE": "\\cross{}",
	"FALSE": "",
}
CITEMAP = {
	"A Comb for Decompiled C Code": "a-comb-for-decompiled-c-code",
	"A Comprehensive Study on ARM Disassembly Tools": "a-comprehensive-study-on-arm-disassembly-tools",
	"A Qualitative Evaluation of Reverse Engineering Tool Usability": "a-qualitative-evaluation-of-reverse-engineering-tool",
	"A Survey of Binary Code Fingerprinting Approaches: Taxonomy, Methodologies, and Features": "a-survey-of-binary-code-fingerprinting-approaches",
	"An Observational Investigation of Reverse Engineers' Process and Mental Models": "an-observational-investigation-of-reverse-engineers",
	"Automatic Vulnerability Detection in Embedded Devices and Firmware: Survey and Layered Taxonomies": "automatic-vulnerability-detection-in-embedded-devices-and-firmware",
	"Binary code is not easy": "binary-code-is-not-easy",
	"Binary-code obfuscations in prevalent packer tools": "binary-code-obfuscations-in-prevalent-packer-tools",
	"BinGold: Towards robust binary analysis by extracting the semantics of binary code as semantic flow graphs (SFGs)": "bingold",
	"BinPointer: towards precise, sound, and scalable binary-level pointer analysis": "binpointer",
	"BinRec: Attack Surface Reduction Through Dynamic Binary Recovery": "binrec",
	"Defeating MBA-based Obfuscation": "defeating-mba-based-obfuscation",
	"Fast location of similar code fragments using semantic 'juice'": "juice",
	"From Hack to Elaborate Technique—A Survey on Binary Rewriting": "from-hack-to-elaborate-technique",
	"HEAPSTER: Analyzing the Security of Dynamic Allocators for Monolithic Firmware Images": "heapster",
	"Helping Johnny to Analyze Malware A Usability-Optimized Decompiler and Malware Analysis User Study": "helping-johnny-to-analyze-malware",
	"HexT5: Unified Pre-training for Stripped Binary Code Information Inference": "hext5",
	"How Professional Hackers Understand Protected Code while Performing Attack Tasks": "how-professional-hackers-understand-protected-code",
	"Labeling library functions in stripped binaries": "labeling-library-functions-in-stripped-binaries",
	"Obfuscation resilient binary code reuse through trace-oriented programming": "obfuscation-resilient-binary-code-reuse",
	"Revisiting Deep Learning for Variable Type Recovery": "revisiting-deep-learning-for-variable-type-recovery",
	"SATURN Software Deobfuscation Framework Based on LLVM": "saturn",
	"Scalable variable and data type detection in a binary rewriter": "scalable-variable-and-data-type-detection",
	"Semantics-Aware Machine Learning for Function Recognition in Binary Code": "semantics-aware-machine-learning-for-function-recognition",
	"SIGMA: A Semantic Integrated Graph Matching Approach for identifying reused functions in binary code": "sigma",
	"SoK: Automatic Deobfuscation of Virtualization-protected Applications": "sok",
	"Speculative disassembly of binary code": "speculative-disassembly-of-binary-code",
	"The Method and Software Tool for Identification of the Machine Code Architecture in Cyberphysical Devices": "the-method-and-software-tool-for-identification-of-the-machine-code-architecture",
	"The missing link: explaining ELF static linking, semantically": "the-missing-link",
	"Understanding the behaviour of hackers while performing attack tasks in a professional setting and in a public challenge": "behaviour-of-hackers",
	"UROBOROS: Instrumenting Stripped Binaries with Static Reassembling": "uroboros",
	"Using Reduced Execution Flow Graph to Identify Library Functions in Binary Code": "using-reduced-execution-flow-graph",
	"VMAttack: Deobfuscating Virtualization-Based Packed Binaries": "vmattack"
}



def mapcell(s):
	return CELLMAP[s] if s in CELLMAP else s

def mapcite(s):
	return CITEMAP[s] if s in CITEMAP else s

def generate_compressed(i, o):
	p = lambda *x: print(*x, file=o)
	r = csv.DictReader(i, dialect="excel-tab")
	themes = OrderedDict([(theme, set()) for theme in filter(lambda x: x != "", r.fieldnames[1:])])
	written_rqs = set()
	for row in r:
		citation = mapcite(row["Title"])
		for theme, theme_citations in themes.items():
			if row[theme] == "TRUE":
				theme_citations.add(citation)

	p(f"\\begin{{tabular}}{{lll}}")
	p("\\toprule")
	p("& \\thead{Theme} & \\thead{Citation(s)} \\\\")
	p("\\midrule")
	for theme, theme_citations in themes.items():
		rqtext = ""
		(rq, theme) = theme.split("|")
		if rq not in written_rqs:
			if len(written_rqs) != 0:
				print("\\midrule")
			written_rqs.add(rq)
			rqtext = f"\\thead{{{rq}}}"
		p(f"{rqtext} & {theme} & ")
		if len(theme_citations) > 0:
			p("\\cite{" + ", ".join(theme_citations) + "}")
		p("\\\\")
	p("\\bottomrule")
	p("\\end{tabular}")

def generate(i, o):
	p = lambda *x: print(*x, file=o)
	r = csv.DictReader(i, dialect="excel-tab")
	p(f"\\begin{{tabular}}{{{"l" * len(r.fieldnames)}}}")
	p("\\toprule")
	p(f"\\thead{{{r.fieldnames[0]}}} & " + " & ".join(map(lambda x: f"\\theadr{{{x}}}" if x else "", r.fieldnames[1:])) + "\\\\")
	p("\\midrule")
	for row in r.reader:
		p(" & ".join(map(mapcell, row)) + "\\\\")
	p("\\bottomrule")
	p("\\end{tabular}")
	

def main(args):
	generate_compressed(sys.stdin, sys.stdout)

if __name__ == "__main__":
	main(sys.argv[1:])
