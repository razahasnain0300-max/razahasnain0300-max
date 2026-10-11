# Automatic GitHub Profile Project Updates

The GitHub Actions workflow at [.github/workflows/sync-public-repos.yml](../.github/workflows/sync-public-repos.yml) checks for new **public** repositories owned by `razahasnain0300-max` approximately every four hours.

Every scheduled run updates three profile files only if the list changed:

- `README.md`: an automatically managed section with links to up to eight recently created public repositories.
- `AUTO_REPOSITORIES.md`: a complete list of the public projects discovered.
- `assets/auto-repos.svg`: a matching purple/cyan graphical showcase of up to six projects.

Existing custom 3D sections and [the 13-project portfolio](../PORTFOLIO.md) are preserved.

**To update immediately:** GitHub repository → **Actions** → **Auto-update public portfolio** → **Run workflow**.

**Privacy:** All application repositories currently connected to this account are private. This public-only workflow intentionally does not publish their names, descriptions, code or other metadata. To display a private project, manually approve a safe public title and preview. A broader private-repo updater would need explicit consent, a separate credential, and careful filtering.

**Limitations:** This is scheduled polling, not instant creation-event detection. GitHub may delay scheduled runs. The repository needs Actions enabled and must permit workflow `contents: write` for automatic push; if those permissions are restricted, the workflow may need an owner setting change.

This automation uses the built-in `GITHUB_TOKEN` only and does not require storing your personal GitHub token.
