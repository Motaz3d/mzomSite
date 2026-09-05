# PLAN.md — Work status

## Done
- Project folder created, AGENTS.md session protocol established, repo pushed to GitHub.
- Placeholder homepage (index.html, Arabic RTL) created and pushed.
- GitHub Pages enabled on branch `main` (path `/`) — live at https://motaz3d.github.io/mzomSite/

## In progress
- Custom domain setup: waiting for the domain name from the user to create the CNAME file and set it in Pages settings.

## Next
- Add DNS records at **Virtono** (the domain uses Virtono NS, so Regery DNS is ignored):
  - 4 × A records: `@` → 185.199.108.153 / .109.153 / .110.153 / .111.153
  - CNAME: `www` → Motaz3d.github.io
  - Keep existing Zoho MX/TXT/DKIM records untouched.
- Create `CNAME` file with the domain and set custom domain in Pages, then enforce HTTPS.
- Build the real site content.
