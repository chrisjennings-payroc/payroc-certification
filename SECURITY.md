# Security policy

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Use GitHub's private reporting: the **Security** tab → **Report a vulnerability**. We aim to acknowledge reports within 5 business days.

In scope: script or command injection in the plugin's Python scripts, secrets or card data leaking into generated certification files, tampering with the vendored `jspdf.umd.min.js`, or weaknesses in the plugin marketplace manifest.

## Supported versions

Only the latest release on `main` is supported.

## What the plugin does

See [docs/SECURITY_payroc.md](docs/SECURITY_payroc.md) for the plugin's runtime behaviour (local stdlib-only Python, no network calls, redaction of pasted secrets).

## Contributing safely

- All changes land through pull requests with code-owner review; `main` is protected.
- Never commit credentials, API keys, merchant data, cardholder data or real partner information.
