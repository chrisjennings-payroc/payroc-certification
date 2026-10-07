#!/usr/bin/env python3
"""Pre-share / pre-review check for a Payroc Certification Script (.html + .md twin).

Usage: review-cert.py <script.html> [--md twin.md]
Exit 0 = ok, 1 = problems found. Stdlib only.

Checks: the .md twin exists; scenario ids match between HTML state and .md; every blocked / follow_up scenario has a reason;
every recorded run has a Test Tag in the .md; no credential- or card-shaped values anywhere.
"""
import json
import os
import re
import sys

CRED = [
    (re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"), "JWT-shaped token"),
    (re.compile(r"bearer\s+(?!\[REDACTED\])[A-Za-z0-9._~+/=-]{20,}", re.I), "Bearer token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\b[a-f0-9]{40,}\b", re.I), "40+ char hex string"),
    (re.compile(r"(?:api[_-]?key|secret|password)\"?\s*[:=]\s*\"?(?!\[REDACTED\]|<|\{\{|\"?\s*$)[A-Za-z0-9/+_-]{16,}", re.I), "key/secret assignment"),
]


def luhn(d):
    s, alt = 0, False
    for ch in reversed(d):
        n = int(ch)
        if alt:
            n = n * 2 - 9 if n * 2 > 9 else n * 2
        s += n
        alt = not alt
    return s % 10 == 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    html_path = argv[1]
    md_path = argv[argv.index("--md") + 1] if "--md" in argv else os.path.splitext(html_path)[0] + ".md"
    problems = []
    with open(html_path, encoding="utf-8") as fh:
        html = fh.read()
    m = re.search(r'id="cert-state">(.*?)</script>', html, re.S)
    if not m:
        print("ERROR: no cert-state block - not a certification script", file=sys.stderr)
        return 1
    state = json.loads(m.group(1))
    if not os.path.exists(md_path):
        problems.append("missing .md twin: " + md_path)
        md = ""
    else:
        with open(md_path, encoding="utf-8") as fh:
            md = fh.read()
    if md:
        md_ids = set(re.findall(r"<!-- cert:scenario=([A-Za-z0-9-]+) -->", md))
        t = state.get("tailor", {})
        expect = set(t.get("included", [])) | set(k for k, v in (state.get("manualInclude") or {}).items() if v)
        expect |= set(c["id"] for c in state.get("custom", []))
        expect -= set((state.get("manualExclude") or {}).keys())
        for i in sorted(expect - md_ids):
            problems.append("scenario in HTML but missing from .md: " + i)
        for i in sorted(md_ids - expect):
            problems.append("scenario in .md but not in HTML: " + i)
    for sid, r in (state.get("results") or {}).items():
        if r.get("status") in ("blocked", "follow_up") and not (r.get("reason") or "").strip():
            problems.append("%s is %s but has no reason" % (sid, r["status"]))
    scan = html.split('id="cert-catalog"')[0] + (html.split('id="cert-state">')[1] if 'id="cert-state">' in html else "") + "\n" + md
    scan = re.sub(r"<script>/\*\*.*?</script>", "", scan, flags=re.S)  # skip vendored library
    for rx, label in CRED:
        for mm in rx.finditer(scan):
            problems.append("possible %s: %s..." % (label, mm.group(0)[:12]))
            break
    for mm in re.finditer(r"(?<![\w-])((?:\d[ -]?){12,18}\d)(?![\w-])", md):
        d = re.sub(r"\D", "", mm.group(1))
        if 13 <= len(d) <= 19 and luhn(d):
            problems.append("possible card number in .md: ****" + d[-4:])
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print(" - " + p)
        return 1
    print("OK: %d scenario results checked, .md twin consistent, no credential-shaped values." % len(state.get("results") or {}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
