#!/usr/bin/env python3
"""Parse a Payroc Solution Design .md and print how the certification script would be tailored.

Usage: parse-sd.py <solution-design.md> [--json]
Stdlib only. Tailoring logic lives in certlib.py (mirrored in template.html).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import certlib  # noqa: E402


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    with open(path, encoding="utf-8") as fh:
        sd = certlib.parse_sd(fh.read())
    if not sd["sections"]:
        print("ERROR: no <!-- sd:section=... --> markers found; is this a Solution Design .md?", file=sys.stderr)
        return 1
    catalog = certlib.load_catalog()
    t = certlib.tailor(catalog, sd)
    if "--json" in argv:
        print(json.dumps({"front": sd["front"], "tailor": t}, indent=2))
        return 0
    print("Partner: %s" % (sd["front"].get("partner") or "(unresolved)"))
    print("Included scenarios: %d   Excluded: %d" % (len(t["included"]), len(t["excluded"])))
    for sec in catalog["sections"]:
        info = t["sections"][sec["section"]]
        inc = [s["id"] for s in sec["scenarios"] if s["id"] in t["included"]]
        print("  %-14s %-8s %s" % (sec["section"], info["platform"] if info["inScope"] else "OUT", "%d/%d" % (len(inc), len(sec["scenarios"]))))
    for f in t["followUps"]:
        print("FOLLOW-UP: " + f["text"])
    for n in t["notes"]:
        print("NOTE: " + n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
