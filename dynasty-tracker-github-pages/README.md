# Dynasty Tracker — GitHub Pages edition

A static, public GitHub Pages dashboard for Cabal Dynasty character `lXlGhostlXl`.

## Deploy to GitHub Pages

1. Create a new GitHub repository, e.g. `dynasty-tracker` (public is easiest for GitHub Pages).
2. Upload **the contents of this folder** to the repository root, including the hidden `.github/workflows/sync.yml` file. You can use `git add -A` to ensure hidden files are included.
3. In **Settings → Pages → Build and deployment**, select **Deploy from a branch**, `main`, `/ (root)`, then Save.
4. Open `https://YOUR-USERNAME.github.io/dynasty-tracker/` after deployment.
5. In **Actions**, enable workflows if prompted; open **Sync Armory character → Run workflow** to test an immediate sync.
6. Under **Settings → Actions → General → Workflow permissions**, ensure the workflow can write repository contents (or configure appropriate permissions). The workflow declares `contents: write`, but organizational policies can restrict this.

## Scheduled syncing

`.github/workflows/sync.yml` runs every **6 hours** at minute 17 UTC, plus manual `workflow_dispatch` runs. `scripts/sync.py` fetches the same 14 public Armory endpoints used by the browser extractor, validates critical results, normalizes them, and commits `data/snapshots/YYYY-MM-DD.json` and `data/index.json`.

- **One snapshot per UTC day**: later successful syncs that day replace the day's snapshot; 120 days are retained.
- **Failed syncs do not commit** partial data. Check the Actions logs for HTTP, DNS, bot-protection, or API failures.
- **No API keys or secrets** are used or required for the public endpoints.
- **Important:** GitHub-hosted runners may be blocked by the Armory, and external access has **not been verified**. If blocked, manual JSON import continues to work, but automatic sync requires an authorized alternative (such as a locally scheduled extractor).
- GitHub Actions scheduled jobs may be delayed or disabled after extended inactivity on public repositories. Check the Actions tab and last-sync label.

## Current dashboard

Overview, equipment, Force Wing, Stellar Link, Collections, Pet/Runes/Merit/Achievements, and Snapshot History. Dungeon time tracking has been intentionally postponed.

The dashboard fetches `data/index.json` and referenced snapshots on every page load. The original Oct 20 seed is a fallback. You can still import Armory JSON manually; manual imports are saved in browser storage. Published snapshot data is visible to anyone who can access the public repository/site.

## Extend for new endpoints

1. Add the route to `ROUTES` in `scripts/sync.py`.
2. Add desired normalized fields to `normalize()` in **both** `scripts/sync.py` and `app.js`.
3. Add the UI rendering to `app.js`.
4. Keep optional endpoints optional; do not let a newly discovered 404 stop all syncing.

## Security and operational notes

Only query publicly accessible read-only API routes. Do not store credentials or session tokens in the repository. Never commit raw responses containing private data. Confirm that automated requests are allowed by the site operator; reduce frequency if needed. This repository stores historical character data publicly, so review it before publishing.

### Test locally

Serve the folder over HTTP to test hosted snapshot loading: `python -m http.server 8000`, then visit `http://localhost:8000/`. Direct `file://` opening may block `fetch()`; the bundled fallback snapshot still renders.
