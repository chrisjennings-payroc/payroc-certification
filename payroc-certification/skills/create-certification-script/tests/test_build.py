import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
import certlib  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
REQUIRED_KEYS = ["id", "title", "tier", "kind", "platform", "appliesWhen", "steps", "expected"]


def read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return fh.read()


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = certlib.load_catalog()

    def test_scenarios_valid(self):
        ids = set()
        for sec in self.catalog["sections"]:
            for sc in sec["scenarios"]:
                for k in REQUIRED_KEYS:
                    self.assertIn(k, sc, "%s missing %s" % (sc.get("id"), k))
                self.assertIn(sc["tier"], ("required", "conditional", "recommended"), sc["id"])
                self.assertIn(sc["platform"], ("payroc", "worldnet", "both"), sc["id"])
                self.assertTrue(sc["steps"], sc["id"])
                if sc["tier"] == "conditional":
                    self.assertTrue(sc["appliesWhen"], "%s conditional without appliesWhen" % sc["id"])
                self.assertNotIn(sc["id"], ids)
                ids.add(sc["id"])
                self.assertFalse(re.search(r"gochip|ecomm|woocommerce|magento", sc["title"], re.I), sc["id"])

    def test_tag_length_budget(self):
        longest = max(len(sc["id"]) for s in self.catalog["sections"] for sc in s["scenarios"])
        tag = certlib.run_id("Abcdefghijkl") + "-" + "X" * longest + "-99"
        self.assertLessEqual(len(tag), 24, tag)


class TailorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = certlib.load_catalog()

    def test_hpp_recurring(self):
        sd = certlib.parse_sd(read("sd-hpp-recurring.md"))
        t = certlib.tailor(self.catalog, sd)
        inc = set(t["included"])
        self.assertFalse(any(i.startswith("CP-") for i in inc), "cloud is out of scope")
        self.assertTrue(any(i.startswith("HPP-") for i in inc))
        self.assertTrue(any(i.startswith("AUTH-") for i in inc))
        self.assertEqual(len(t["followUps"]), 1)
        self.assertFalse(t["sections"]["cloud"]["inScope"])

    def test_worldnet_only(self):
        sd = certlib.parse_sd(read("sd-worldnet-only.md"))
        t = certlib.tailor(self.catalog, sd)
        by_id = {sc["id"]: sc for s in self.catalog["sections"] for sc in s["scenarios"]}
        for i in t["included"]:
            self.assertIn(by_id[i]["platform"], ("worldnet", "both"), i)
        self.assertTrue(t["notes"])

    def test_no_sd_includes_everything(self):
        t = certlib.tailor(self.catalog, None)
        self.assertEqual(len(t["excluded"]), 0)


class BuildTests(unittest.TestCase):
    def test_build_outputs(self):
        out = tempfile.mkdtemp()
        try:
            r = subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), "scripts", "build-cert.py"),
                                os.path.join(FIX, "sd-hpp-recurring.md"), "--out", out], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            files = os.listdir(out)
            html = open(os.path.join(out, [f for f in files if f.endswith(".html")][0]), encoding="utf-8").read()
            md = open(os.path.join(out, [f for f in files if f.endswith(".md")][0]), encoding="utf-8").read()
            self.assertNotIn("__CERT_CATALOG__", html)
            self.assertNotIn("__VENDOR_JSPDF__", html)
            state = re.search(r'id="cert-state">(.*?)</script>', html, re.S).group(1)
            st = json.loads(state)
            md_ids = re.findall(r"<!-- cert:scenario=([A-Za-z0-9-]+) -->", md)
            self.assertEqual(sorted(md_ids), sorted(st["tailor"]["included"]))
            self.assertIn("document: payroc-certification-script", md)
            self.assertIn("ACMECO", st["meta"]["certRunId"])
        finally:
            shutil.rmtree(out)


class ReviewTests(unittest.TestCase):
    def test_review_flags_problems(self):
        out = tempfile.mkdtemp()
        try:
            subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), "scripts", "build-cert.py"),
                            os.path.join(FIX, "sd-hpp-recurring.md"), "--out", out], check=True, capture_output=True)
            html_path = [os.path.join(out, f) for f in os.listdir(out) if f.endswith(".html")][0]
            review = os.path.join(os.path.dirname(HERE), "scripts", "review-cert.py")
            self.assertEqual(subprocess.run([sys.executable, review, html_path], capture_output=True).returncode, 0)
            with open(html_path, encoding="utf-8") as fh:
                html = fh.read()
            bad = html.replace('"results":{}', '"results":{"HPP-01":{"status":"blocked","attempt":1}}')
            with open(html_path, "w", encoding="utf-8") as fh:
                fh.write(bad)
            r = subprocess.run([sys.executable, review, html_path], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("no reason", r.stdout)
        finally:
            shutil.rmtree(out)


@unittest.skipUnless(shutil.which("node"), "node not installed")
class ParityTests(unittest.TestCase):
    """The in-browser tailor() must give the same answer as certlib.tailor()."""

    def run_js(self, fixture):
        with open(certlib.TEMPLATE, encoding="utf-8") as fh:
            tpl = fh.read()
        block = re.search(r"// <tailor>(.*?)// </tailor>", tpl, re.S).group(1)
        js = ("var ALWAYS=%s;\n%s\nvar fs=require('fs');var catalog=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));var md=fs.readFileSync(process.argv[2],'utf8');"
              "console.log(JSON.stringify(tailor(catalog,parseSD(md))));") % (json.dumps(certlib.ALWAYS), block)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
            json.dump(certlib.load_catalog(), tf)
        try:
            out = subprocess.run(["node", "-e", js, tf.name, os.path.join(FIX, fixture)], capture_output=True, text=True)
        finally:
            os.unlink(tf.name)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)

    def test_parity(self):
        catalog = certlib.load_catalog()
        for fx in ("sd-hpp-recurring.md", "sd-worldnet-only.md"):
            py = certlib.tailor(catalog, certlib.parse_sd(read(fx)))
            js = self.run_js(fx)
            self.assertEqual(py["included"], js["included"], fx)
            self.assertEqual(py["tierOverride"], js["tierOverride"], fx)
            self.assertEqual(py["followUps"], js["followUps"], fx)
            self.assertEqual(py["sections"], js["sections"], fx)


@unittest.skipUnless(os.environ.get("CERT_REAL_SD_DIR"), "set CERT_REAL_SD_DIR to a folder of real SD .md files (not committed: partner data)")
class RealSDTests(unittest.TestCase):
    def test_real_sds_tailor_sensibly(self):
        catalog = certlib.load_catalog()
        d = os.environ["CERT_REAL_SD_DIR"]
        files = [f for f in os.listdir(d) if f.endswith(".md")]
        self.assertTrue(files)
        for f in files:
            with open(os.path.join(d, f), encoding="utf-8") as fh:
                sd = certlib.parse_sd(fh.read())
            self.assertTrue(sd["sections"], f)
            t = certlib.tailor(catalog, sd)
            self.assertGreater(len(t["included"]), 10, f)
            self.assertLess(len(t["included"]), 186, f)


if __name__ == "__main__":
    unittest.main()
