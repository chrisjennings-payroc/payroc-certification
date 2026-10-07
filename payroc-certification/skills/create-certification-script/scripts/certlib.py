#!/usr/bin/env python3
"""Shared helpers for the Payroc certification script builder (stdlib only, Python 3.8+).

The tailoring rules here MUST stay in sync with the `// <tailor>` block in template.html
(tests/test_build.py runs both against the same fixtures and compares results).
"""
import datetime
import hashlib
import json
import os
import re

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIO_DIR = os.path.join(SKILL_DIR, "scenarios")
TEMPLATE = os.path.join(SKILL_DIR, "template.html")
VENDOR_JSPDF = os.path.join(SKILL_DIR, "vendor", "jspdf.umd.min.js")
VERSION = "0.1.0"

# Order sections appear in the script.
ORDER = ["auth", "errors", "boarding", "equipment", "direct-api", "hosted-fields", "hpp",
         "payment-links", "cloud", "wallets", "recurring", "verification", "funding", "reporting",
         "security"]
# Display groups (script reads top to bottom: foundation -> setup -> take payments -> stored methods -> money -> close-out)
GROUPS = {
    "auth": "Foundation", "errors": "Foundation",
    "boarding": "Onboarding & setup", "equipment": "Onboarding & setup",
    "direct-api": "Accepting payments", "hosted-fields": "Accepting payments", "hpp": "Accepting payments",
    "payment-links": "Accepting payments", "cloud": "Accepting payments", "wallets": "Accepting payments",
    "recurring": "Stored payment methods & checks", "verification": "Stored payment methods & checks",
    "funding": "Funding & reporting", "reporting": "Funding & reporting",
    "security": "Security",
}
ALWAYS = ["auth", "errors", "security"]
STATUSES = ["not_run", "pass", "fail", "blocked", "follow_up", "na"]


def _skill_map_labels():
    try:
        with open(os.path.join(SKILL_DIR, "skill-map.json"), encoding="utf-8") as fh:
            # SD labels carry the SD's own numbering ("8.2e Direct API Payments"); the script numbers sections itself.
            return {k: re.sub(r"^\d+(\.\d+)?[a-z]?\s+", "", v["label"]) for k, v in json.load(fh)["sections"].items()}
    except (OSError, KeyError, ValueError):
        return {}


SKILL_MAP_LABELS = _skill_map_labels()


# Request fields where a partner can put a free-text Test Tag. The Idempotency-Key is a UUID v4, so it can never carry the tag:
# scenarios without one of these fields are identified by the Idempotency-Key value itself.
TAGGABLE_RX = re.compile(r"^(order\.orderId|orderId|ORDERID|merchantReference|MERCHANTREF|uniqueReference|UNIQUEREF|customerReference|description|secureTokenId|paymentPlanId|subscriptionId)$")

TBC_RX = re.compile(r"confirm with payroc|documented at|not documented|not fully documented|undocumented|uat trigger", re.I)

# Items still to be confirmed with Payroc owners. Shown in every generated script and listed in the .md front matter.
FLAGS = [
    {"id": "splunk-tag-field", "text": "Splunk Test Tag field not yet confirmed: the request field named under each endpoint is a placeholder until the platform team confirms which field is indexed in Splunk."},
    {"id": "response-ids-splunk", "text": "Searchable identifiers not yet confirmed: the Test Tag (or, where a call has no free-text field, the Idempotency-Key UUID) is the primary lookup. Whether response IDs such as paymentId are also searchable in Splunk is still to be confirmed; they are captured as secondary evidence."},
    {"id": "uat-triggers", "text": "UAT triggers are limited: scenarios marked 'Trigger TBC' have no documented UAT decline / AVS / CVV / partial-approval / 3DS / device trigger yet. Agree an alternative with Payroc before running them."},
]


def load_catalog():
    sections = []
    seen = set()
    files = {f[:-5]: os.path.join(SCENARIO_DIR, f) for f in os.listdir(SCENARIO_DIR) if f.endswith(".json")}
    for sid in ORDER + sorted(set(files) - set(ORDER)):
        if sid not in files:
            continue
        with open(files[sid], encoding="utf-8") as fh:
            data = json.load(fh)
        data["section"] = sid
        if sid in SKILL_MAP_LABELS:
            data["label"] = SKILL_MAP_LABELS[sid]
        data["label"] = re.sub(r"^\d+(\.\d+)?[a-z]?\s+", "", data.get("label", sid))
        data["group"] = GROUPS.get(sid, "Other")
        for sc in data.get("scenarios", []):
            if sc["id"] in seen:
                raise ValueError("duplicate scenario id across catalogue: " + sc["id"])
            seen.add(sc["id"])
            sc["section"] = sid
            sc["triggerTbc"] = bool(TBC_RX.search(sc.get("testData") or ""))
            eps = sc.get("endpoints") or []
            tf = (eps[0].get("tagField") if eps else None) or ""
            sc["identifyBy"] = "test_tag" if TAGGABLE_RX.match(tf.strip()) else "idempotency_key"
        sections.append(data)
    return {"version": VERSION, "sections": sections, "flags": FLAGS}


# ---------------------------------------------------------------- SD parsing
def parse_sd(md):
    out = {"front": {}, "sections": {}}
    fm = re.match(r"^---\s*\n([\s\S]*?)\n---\s*(\n|$)", md)
    if fm:
        for line in fm.group(1).split("\n"):
            m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
            if not m:
                continue
            v = m.group(2).strip()
            try:
                v = json.loads(v)
            except ValueError:
                v = re.sub(r'^"|"$', "", v)
            out["front"][m.group(1)] = v
    marks = [(m.group(1), m.start(), m.end()) for m in re.finditer(r"<!--\s*sd:section=([a-z0-9-]+)\s*-->", md)]
    for i, (sid, start, end) in enumerate(marks):
        text = md[end: marks[i + 1][1] if i + 1 < len(marks) else len(md)]
        sc = re.search(r"^- in_scope:\s*(yes|no)", text, re.I | re.M)
        pf = re.search(r"^- platform:\s*(payroc|worldnet|both)", text, re.I | re.M)
        out["sections"][sid] = {
            "text": text,
            "inScope": (sc.group(1).lower() == "yes") if sc else None,
            "platform": pf.group(1).lower() if pf else None,
        }
    return out


def match_lines(text):
    keep = [l for l in text.split("\n") if not re.match(r"^\s*- \[ \]", l) and "[TODO:" not in l]
    return "\n".join(keep).lower()


def path_regex(path):
    p = re.sub(r"^/v1", "", str(path or ""))
    parts = [re.escape(s) for s in re.split(r"\{[^}]*\}", p)]
    return re.compile("[^\\s|`]*".join(parts), re.I)


def optional_endpoint(sd_text, path):
    if not path:
        return False
    rx = path_regex(path)
    seen_opt = seen_req = False
    for l in sd_text.split("\n"):
        if "|" not in l or not rx.search(l):
            continue
        ll = l.lower()
        if "[optional]" in ll:
            seen_opt = True
        if "[required]" in ll:
            seen_req = True
    return seen_opt and not seen_req


def global_platform(catalog, sd):
    """Platform for cross-cutting sections: worldnet if every in-scope workflow is worldnet, payroc if none are, else both."""
    plats = []
    wf = sd["front"].get("workflows_in_scope") or []
    for sec in catalog["sections"]:
        sid = sec["section"]
        if sid in ALWAYS:
            continue
        s = sd["sections"].get(sid)
        if not s:
            continue
        in_scope = s["inScope"] if s["inScope"] is not None else sid in wf
        if in_scope:
            plats.append(s["platform"] or (sd["front"].get("platforms") or {}).get(sid) or "payroc")
    if not plats:
        return "both"
    if all(p == "worldnet" for p in plats):
        return "worldnet"
    if all(p == "payroc" for p in plats):
        return "payroc"
    return "both"


def tailor(catalog, sd):
    gp = global_platform(catalog, sd) if sd else "both"
    res = {"included": [], "excluded": [], "tierOverride": {}, "sections": {}, "followUps": [],
           "notes": [], "sdProvided": bool(sd)}
    for sec in catalog["sections"]:
        sid = sec["section"]
        info = {"inScope": True, "platform": "both", "text": ""}
        if sd:
            s = sd["sections"].get(sid)
            if sid in ALWAYS:
                info = {"inScope": True, "platform": (s or {}).get("platform") or gp, "text": s["text"] if s else ""}
            else:
                wf = sd["front"].get("workflows_in_scope") or []
                if s:
                    in_scope = s["inScope"] if s["inScope"] is not None else sid in wf
                else:
                    in_scope = False
                plat = (s or {}).get("platform") or (sd["front"].get("platforms") or {}).get(sid) or "payroc"
                info = {"inScope": bool(in_scope), "platform": plat, "text": s["text"] if s else ""}
                if s:
                    todos = s["text"].count("[TODO:")
                    if in_scope and todos:
                        res["followUps"].append({"section": sid, "text": 'SD section "%s" has %d unresolved field(s) - confirm with the partner before certifying.' % (sec["label"], todos)})
        match_text = match_lines(info["text"])
        res["sections"][sid] = {"inScope": info["inScope"], "platform": info["platform"]}
        for sc in sec["scenarios"]:
            reason = None
            if not info["inScope"]:
                reason = "Section not in SD scope"
            elif sd:
                sp = sc.get("platform") or "payroc"
                if sp != "both" and info["platform"] != "both" and sp != info["platform"]:
                    reason = "Platform %s selected in SD" % info["platform"]
                elif sp != "both" and info["platform"] == "both":
                    reason = None
                elif sc.get("tier") == "conditional":
                    hit = any(str(k).lower() in match_text for k in (sc.get("appliesWhen") or []))
                    if not hit:
                        reason = "SD does not indicate: " + ", ".join(sc.get("appliesWhen") or [])
            if reason:
                res["excluded"].append({"id": sc["id"], "reason": reason})
            else:
                res["included"].append(sc["id"])
                if sd and sc.get("tier") == "required" and sc.get("endpoints") and optional_endpoint(info["text"], sc["endpoints"][0].get("path")):
                    res["tierOverride"][sc["id"]] = "recommended"
    # "gochip" is the pre-0.2 SD id for the Worldnet SDKs/POS section
    if sd and any(sd["sections"].get(k, {}).get("inScope") for k in ("worldnet-sdks", "gochip")):
        res["notes"].append("SD scopes Worldnet SDKs / POS plugins / GoChip. These are outside this certification script and are not tested here.")
    return res


# ---------------------------------------------------------------- state / output
def build_state(catalog, sd=None, sd_name="", overrides=None):
    tl = tailor(catalog, sd)
    fr = sd["front"] if sd else {}
    partner = fr.get("partner") or ""
    meta = {
        "partner": partner or "", "contact": fr.get("partner_contact") or "", "se": fr.get("prepared_by") or "",
        "reviewDate": "", "sdFile": sd_name, "sdVersion": fr.get("template_version") or "", "env": "UAT",
        "projectNumber": "", "splunkTemplate": 'index=<INDEX> "{tag}"', "mode": "partner", "signoff": {},
    }
    meta.update(overrides or {})
    return {"meta": meta, "tailor": tl, "results": {}, "custom": [], "manualInclude": {}, "manualExclude": {}, "manual": [], "collapsed": {}}


def safe_json(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def render_html(catalog, state, with_pdf=True):
    with open(TEMPLATE, encoding="utf-8") as fh:
        html = fh.read()
    vendor = ""
    if with_pdf and os.path.exists(VENDOR_JSPDF):
        with open(VENDOR_JSPDF, encoding="utf-8") as fh:
            vendor = fh.read()
        if "</script" in vendor.lower():
            raise ValueError("vendor library contains </script - cannot inline")
    html = html.replace("/*__VENDOR_JSPDF__*/", lambda_free(vendor))
    html = html.replace("__CERT_CATALOG__", lambda_free(safe_json(catalog)))
    html = html.replace('<script type="application/json" id="cert-state">{}</script>',
                        '<script type="application/json" id="cert-state">' + lambda_free(safe_json(state)) + "</script>")
    return html


def lambda_free(s):
    """Plain return; exists so str.replace never interprets the payload (kept explicit for readability)."""
    return s


def included_ids(state):
    t = state["tailor"]
    return [i for i in t["included"] if i not in state.get("manualExclude", {})]


def _q(v):
    return json.dumps(None if v in (None, "") else v, ensure_ascii=False)


NOTICE = ("> **For AI agents and tools:** this file is the machine-readable twin of the HTML Certification Script. "
          "Each `cert:scenario` marker (an HTML comment before each ### heading) starts one UAT test Payroc will verify in its logs. You may help fill in the evidence lines "
          "(`http_status`, `timestamp_utc`, `idempotency_key`, `resource_id`, `correlation_id`, `status`, `notes`) from real test runs only. "
          "Rules: keep ids and markers unchanged; where `identify_by` is `test_tag`, use the `test_tag` value exactly as written in the request field named by `tag_field`; where it is `idempotency_key`, send a fresh UUID v4 in the Idempotency-Key header and record it in `idempotency_key` (the UUID is what Payroc searches for); "
          "never invent results, ids or timestamps - leave unknown fields empty; set `status` to one of `not_run | pass | fail | blocked | "
          "follow_up | na` and give a `reason` for blocked/follow_up; never include real card numbers, API keys or secrets; never sign on anyone's behalf (signatures are captured only in the HTML file).")


def render_md(catalog, state):
    """Markdown twin for a fresh (nothing run yet) script. The browser regenerates this as results are entered."""
    m = state["meta"]
    inc = set(included_ids(state))
    override = state["tailor"].get("tierOverride", {})
    total = sum(1 for s in catalog["sections"] for sc in s["scenarios"] if sc["id"] in inc)
    L = ["---", "document: payroc-certification-script", 'template_version: "%s"' % VERSION,
         "partner: " + _q(m["partner"]), "partner_contact: " + _q(m["contact"]), "payroc_se: " + _q(m["se"]),
         "integration_project_number: " + _q(m["projectNumber"]), "environment: " + _q(m["env"]), "review_date: " + _q(m["reviewDate"]),
         "sd_source: " + _q(m["sdFile"]),
         'generated_at: "%s"' % datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
         "scenarios_total: %d" % total,
         "counts: " + json.dumps({"pass": 0, "fail": 0, "blocked": 0, "follow_up": 0, "not_run": total, "na": 0}),
         "verified_in_logs: 0",
         "pending_confirmation: " + json.dumps([f["id"] for f in catalog.get("flags", [])]), "---", "", NOTICE,
         "> **Pending confirmation:** " + " ".join(f["text"] for f in catalog.get("flags", [])), "", "# %s - Certification Script" % (m["partner"] or "Partner"), ""]
    num = 0
    for sec in catalog["sections"]:
        scs = [sc for sc in sec["scenarios"] if sc["id"] in inc]
        if not scs:
            continue
        num += 1
        L += ["<!-- cert:section=%s -->" % sec["section"], "## %d. %s" % (num, sec["label"]), ""]
        for sc in scs:
            eps = sc.get("endpoints") or []
            tag = "%s-%s-1" % (m["projectNumber"] or "PROJECT", sc["id"])
            L += ["<!-- cert:scenario=%s -->" % sc["id"], "### %s - %s" % (sc["id"], sc["title"]), "",
                  "- tier: " + override.get(sc["id"], sc["tier"]), "- platform: " + (sc.get("platform") or "payroc"),
                  "- status: not_run", "- identify_by: " + sc.get("identifyBy", "test_tag"), "- test_tag: " + tag]
            if eps:
                L += ["- endpoints: " + ", ".join("%s %s" % (e["method"], e["path"]) for e in eps),
                      "- tag_field: " + (eps[0].get("tagField") or "n/a")]
            if sc.get("triggerTbc"):
                L.append("- trigger_status: tbc")
            if sc.get("expectedStatus"):
                L.append("- expected_http_status: %s" % sc["expectedStatus"])
            if sc.get("objective"):
                L.append("- objective: " + sc["objective"])
            L += ["", "**Steps**", ""]
            L += ["%d. %s" % (i + 1, s) for i, s in enumerate(sc.get("steps") or [])]
            L += ["", "**Expected:** " + (sc.get("expected") or "")]
            if sc.get("testData"):
                L += ["", "**Test data:** " + sc["testData"]]
            L += ["", "**Evidence**", ""]
            for k in ["http_status", "timestamp_utc", "idempotency_key", "resource_id", "correlation_id", "mid_terminal", "reason", "notes", "owner", "target_date"]:
                L.append("- %s: " % k)
            L += ["- verified_in_logs: false", "- reviewer_note: ", ""]
    L += ["<!-- cert:section=blockers -->", "## Blockers & follow-ups", ""]
    fus = state["tailor"].get("followUps") or []
    L += ["- SD [Needs follow-up] " + f["text"] for f in fus] or ["None."]
    L += ["", "<!-- cert:section=signoff -->", "## Sign-off", "", "- certified_date: ", "- payroc_representative_name: ",
          "- payroc_representative_signed_at: ", "- partner_representative_name: ", "- partner_representative_signed_at: ", ""]
    return "\n".join(L)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()
