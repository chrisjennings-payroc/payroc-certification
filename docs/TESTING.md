# Testing

```bash
cd payroc-certification/skills/create-certification-script
python3 -m unittest discover -s tests -v    # catalogue validity, tailoring, build output, Python/JS tailoring parity (needs node)
python3 scripts/build-cert.py tests/fixtures/sd-hpp-recurring.md --out /tmp/cert
python3 scripts/review-cert.py /tmp/cert/Acme-Coffee-Software-Certification-Script.html
```

Manual browser checks (Chrome/Edge): open the built `.html`; change a scenario to Blocked (reason required) and confirm it appears in
Blockers & follow-ups; paste a sample response and confirm fields extract and card numbers are masked; switch to Payroc reviewer view (View selector, top right) and use Import Solution Design with a different fixture
and confirm the scope changes while recorded results stay; enable Autosave .html/.md/.pdf and confirm all three files update; switch to Payroc reviewer view and use the log lookup panel.

## Testing against real Solution Designs
Real SDs contain partner data and are not committed. Export each SD's `.md` twin into a local folder and run:
```bash
CERT_REAL_SD_DIR=/path/to/sd-md-folder python3 -m unittest discover -s payroc-certification/skills/create-certification-script/tests -v
python3 payroc-certification/skills/create-certification-script/scripts/parse-sd.py /path/to/Partner-Solution-Design.md
```
SDs created before template 0.2 have no `.md` twin; open the SD in the 0.2 template (or ask for a converter) to produce one. The old section id `gochip` is treated as the Worldnet SDK/plugin section.
