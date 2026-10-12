# Automatic Project Gallery

This repository has a **managed main-page gallery** and **managed full portfolio**. The gallery puts newly discoverable projects first, shows the latest six previews on the profile, and counts every showcased project automatically. The full `PORTFOLIO.md` displays all approved entries.

### How it works

- Every hour (GitHub Actions schedules are approximate), the profile sync retrieves public GitHub repositories via the public endpoint.
- New public repositories get a matching purple/cyan concept card, verified creation date, and a link to the actual public repository.
- Curated private-source projects are listed in `portfolio/curated_projects.json`. Only approved high-level titles and illustrative artwork are published — no private repo URLs, source, secret metadata or credentials.
- The cards are presented **newest-discovered first**, then existing private-source showcases in the curated order. Creation timestamps for private curated projects are not assumed.
- The counter is **showcased projects**, not an unverified total of all private repositories. It updates with additions/removals visible to the sync.
- A separate GitHub-native contribution snake workflow stays unchanged.

### Optional opt-in for newly created private repositories

GitHub's built-in `GITHUB_TOKEN` is restricted to this profile repository and cannot list all of your other private repositories. To automatically discover approved new *private* repos, configure **an additional read-only metadata credential** in this repository's GitHub Actions secret named `GALLERY_PRIVATE_READ_TOKEN`. Only select trusted, least-privilege access appropriate to your account. Never post the token in a conversation or commit it to source code.

Then, inside each private repository you authorize for public portfolio display, add the exact GitHub topic `portfolio-approved`, and fill out a **public-safe** description (do not include confidential client details). Only these explicitly marked repositories are eligible for the gallery. Their *source remains private*, and the public card intentionally omits links to private repositories. The workflow does not publish any other private repo metadata.

**Important:** For future newly created private repositories to be discoverable, the credential must be authorized for them. A fine-grained token restricted to a fixed selection of existing repositories will not automatically cover new repositories. Broader credentials have privacy implications; authorize only what you are comfortable exposing. You may instead add a vetted, public-safe manual entry in the curated manifest without any token.

### Running manually

GitHub → your profile repository → Actions → **Auto-update public portfolio** → **Run workflow**. Scheduled runs may be delayed by GitHub; profile READMEs cannot fetch data at page-view time.

### Technical details

- Generator: `scripts/build_project_gallery.py`
- Approved list: `portfolio/curated_projects.json`
- Public-only discovery: `scripts/sync_public_repos.py`
- README markers: `AUTO-PROJECT-GALLERY`
- Portfolio markers: `AUTO-FULL-GALLERY`
- Card art: `assets/previews/` (curated) and `assets/project-cards/` (generated)
- Tests: `tests/test_project_gallery.py`
- No fabricated client metrics, screenshots, dates, source access, or GitHub contributions.
