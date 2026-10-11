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

## Private case studies with explicit approval

New public GitHub repositories appear automatically on a four-hour schedule. New private repositories **do not** appear without explicit approval.

To publish a public-safe private-project description, edit `portfolio/approved_private_projects.json` in this public repository. Provide an approved title, short summary, category, technologies and set `approved_for_public_profile` to `true`. A `public_demo_url` is optional and must be a real, public HTTPS URL.

Example format (fictional demonstration, not a claim about actual client work):

    {
      "projects": [
        {
          "approved_for_public_profile": true,
          "public_title": "Example Reporting Portal",
          "public_summary": "A custom reporting dashboard",
          "category": "Web Application",
          "technologies": "React, Node.js"
        }
      ]
    }

Never include private GitHub URLs, real client secrets, private credentials, private repository slugs or internal demo links. The sync will build a purple/cyan approved-project card **without** revealing source code. Deleting an entry and re-running the sync removes it.

Your 13 existing showcase concepts, organization-style branding, portrait animation and other README content remain outside the managed sections. GitHub account settings for private contribution visibility must still be enabled by the account owner.
