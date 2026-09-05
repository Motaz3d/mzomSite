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

## Done (additions)
- DNS migration complete: NS switched from Virtono to **Regery NS** (ns-cloud-e*.googledomains.com). Virtono fully detached from the domain.
- Stale records (old server A/AAAA, all Zoho records) deleted from Regery zone by the user; only GitHub records remain.
- Domain verified live: apex → 4 GitHub IPs, www → motaz3d.github.io; http://motazomarien.com serves the site (200).

## Done (additions)
- Literary site built: `build.py` (stdlib) renders `content/*.md` → `index.html` + `pieces/*.html`, paper-style Arabic RTL design.
- First piece published: خ-031 «رسائل إلى مارينا — 1: اللسان» — **then unpublished the same evening at the author's request** (not satisfied with it). Site currently shows an empty state ("قريبًا"); build.py handles zero pieces.

## Next
- Enable "Enforce HTTPS" — GitHub is still issuing the Let's Encrypt certificate (404 "certificate does not exist yet"). One-shot cron scheduled at 21:50 to retry automatically (cron id 01M1SF720QN3Y6C5QK1DCJPHRJ).
- User: cancel all active services in the Virtono client area (hosting/cPanel/VPS) — safe now that DNS is off Virtono; back up anything needed first.
- Build the real site content.
