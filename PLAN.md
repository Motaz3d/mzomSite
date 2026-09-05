# PLAN.md — Work status

## Done
- Project folder created, AGENTS.md session protocol established, repo pushed to GitHub.
- Placeholder homepage (index.html, Arabic RTL) created and pushed.
- GitHub Pages enabled on branch `main` (path `/`) — live at https://motaz3d.github.io/mzomSite/
- Repo made public (required for Pages on the free plan).
- CNAME file created with `motazomarien.com`; custom domain set in Pages (status: building).

## In progress
- DNS at **Virtono** (the active zone; Regery DNS is ignored): user must add GitHub records.
  - Current live DNS: apex A → 146.70.56.163, www CNAME → apex. GitHub records NOT yet added there.

## Next — Virtono exit plan (in order)
- Email decision: user will use personal Gmail (no MX records needed on the domain at all).
- 1. User: back up anything worth keeping from Virtono/cPanel (files, databases, old emails) — after cancellation it is gone.
- 2. User: clean **Regery** DNS (it becomes the active zone): delete stale A → 149.28.238.206 (×2), old AAAA (×2), and all Zoho MX/TXT/DKIM records. Keep the 4 GitHub A records + www CNAME already added there.
- 3. User: at Regery → Actions → Set Nameservers → switch to **Regery NS** (makes Regery DNS authoritative, replaces Virtono NS).
- 4. Agent: verify with dig that the apex resolves to GitHub IPs, then enable "Enforce HTTPS" in Pages.
- 5. User: cancel all active services in the Virtono client area (hosting/cPanel/VPS) — only after steps 1–4 work.
- Build the real site content.
