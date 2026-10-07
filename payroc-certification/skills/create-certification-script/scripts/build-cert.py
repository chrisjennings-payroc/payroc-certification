#!/usr/bin/env python3
"""Build a tailored Payroc Certification Script (.html + .md twin) from a Solution Design .md.

Usage:
  build-cert.py <solution-design.md> [--out DIR] [--name BASENAME] [--project-number N] [--no-pdf-lib]
  build-cert.py --template-only [--out DIR]      # full catalogue, no SD (blank template)

Writes {Partner}-Certification-Script.html and .md (the .html embeds scenarios, state and the jsPDF library
so it is fully self-contained and works offline). Stdlib only.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import certlib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sd", nargs="?")
    ap.add_argument("--out", default=".")
    ap.add_argument("--name")
    ap.add_argument("--template-only", action="store_true")
    ap.add_argument("--project-number", default="", help="Integration Project Number (used in every Test Tag; max ~12 chars)")
    ap.add_argument("--no-pdf-lib", action="store_true")
    a = ap.parse_args()
    if not a.sd and not a.template_only:
        ap.error("provide a Solution Design .md or --template-only")
    catalog = certlib.load_catalog()
    sd = None
    sd_name = ""
    if a.sd:
        with open(a.sd, encoding="utf-8") as fh:
            sd = certlib.parse_sd(fh.read())
        if not sd["sections"]:
            print("ERROR: no <!-- sd:section=... --> markers found; is this a Solution Design .md?", file=sys.stderr)
            return 1
        sd_name = os.path.basename(a.sd)
    state = certlib.build_state(catalog, sd, sd_name, {"projectNumber": a.project_number} if a.project_number else None)
    partner = state["meta"]["partner"]
    base = a.name or ((re.sub(r"[^A-Za-z0-9]+", "-", partner).strip("-") + "-Certification-Script") if partner else "Payroc-Certification-Script" + ("-Template" if a.template_only else ""))
    os.makedirs(a.out, exist_ok=True)
    html_path = os.path.join(a.out, base + ".html")
    md_path = os.path.join(a.out, base + ".md")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(certlib.render_html(catalog, state, with_pdf=not a.no_pdf_lib))
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(certlib.render_md(catalog, state))
    t = state["tailor"]
    print("Wrote %s\nWrote %s" % (html_path, md_path))
    print("Scenarios in script: %d (excluded %d). Integration Project Number: %s" % (len(t["included"]), len(t["excluded"]), state["meta"]["projectNumber"] or "(not set - enter it in the header)"))
    for f in t["followUps"]:
        print("FOLLOW-UP: " + f["text"])
    for n in t["notes"]:
        print("NOTE: " + n)
    print("Next: open the .html in Chrome/Edge, click 'Autosave .html' and '.md', then share the files with the partner.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
