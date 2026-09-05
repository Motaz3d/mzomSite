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

## Next
- User (in Virtono panel): add 4 × A `@` → 185.199.108/109/110/111.153 + CNAME `www` → Motaz3d.github.io.
- ⚠️ **Mail risk:** current MX is `motazomarien.com` itself (cPanel mail on 146.70.56.163). Before changing A `@`, user must: create A `mail` → 146.70.56.163 and change MX to `mail.motazomarien.com` — otherwise email breaks.
- Delete stale A/AAAA records pointing to the old server after the new ones are in place.
- After DNS propagates: verify domain, enable "Enforce HTTPS" in Pages (currently https_enforced=false).
- Build the real site content.
