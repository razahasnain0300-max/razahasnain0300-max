# RehabConnect — Authentic Website Page Previews

**Matching private project repository**: `razahasnain0300-max/rehabconnects`  
**Public website**: `https://rehabconnect.pk/`  
**GitHub profile**: `razahasnain0300-max/razahasnain0300-max`

This workflow uses Playwright Chromium to capture **real screenshots** from carefully selected public RehabConnect pages, rather than fake generated dashboard designs. It may publish up to ten valid screens, including the homepage, care finder, rehabilitation directory, professional listings, research, resources, facilities, comparison and family-support sections.

The screenshot selection is **quality-gated**: every page must be HTTP-successful, stay on the approved domain, have sufficient public content and produce a nonblank screenshot. Inaccessible pages are skipped rather than represented with invented art. At least four pages, including the homepage, must succeed for a new preview set to be published.

### Public profile presentation

- Main project gallery: one wide RehabConnect website preview built from the real homepage and a few other actual screenshots, with no external website link.
- Full `PORTFOLIO.md`: a large project hero and a two-column gallery of selected real public pages, clearly labeled.
- All image files are committed as `assets/previews/rehabconnect-*.webp`.
- `portfolio/curated_projects.json` marks the project as `real_website_screenshot`, so the hourly gallery generator keeps the live captures instead of the older illustrative SVG.

### Privacy safeguards

Capture visits only fixed public, unauthenticated pages. No patient account, admission details, staff/admin dashboard, provider login, booking workflow or private source code is involved. Screenshot images are intentionally **not wrapped in hyperlinks**; clicking does not redirect to the live RehabConnect site.

### Maintenance

The screenshot workflow runs weekly and can be launched manually in GitHub Actions. GitHub's hourly repository-discovery workflow remains independent; the production website and the private project repository are not modified. If the homepage fails to load or fewer than four quality screenshots are captured, the workflow fails without replacing the previous good screenshot assets.
