# Security notes

- The plugin runs local Python (stdlib only) scripts under `payroc-certification/skills/create-certification-script/scripts/`: `parse-sd.py`, `build-cert.py`, `review-cert.py`. Commands declare `Bash(python3:*)`; narrow it per your organisation's policy.
- The plugin makes **no network calls** and stores no credentials. Generated scripts load the Geist web font from Google Fonts when online; otherwise they fall back to system fonts.
- The generated HTML embeds a vendored copy of [jsPDF](https://github.com/parallax/jsPDF) 4.2.1 (MIT) for PDF autosave. Re-vendor with `npm pack jspdf` and copy `dist/jspdf.umd.min.js`.
- Partners paste responses into the script: the paste-to-capture box masks Luhn-valid card numbers, bearer tokens and common secret fields before storing, and `review-cert.py` scans the HTML and .md for JWTs, private keys, long hex strings, key/secret assignments and card numbers. It is a safety net, not a guarantee: tell partners never to paste secrets.
- Autosave uses the browser File System Access API (Chrome/Edge); the user picks each file. Other browsers cache in `localStorage` and offer downloads.
