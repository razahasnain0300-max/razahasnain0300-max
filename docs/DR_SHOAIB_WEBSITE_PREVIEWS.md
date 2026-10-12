# Dr Shoaib · Genuine Website Screenshot Showcase

**Source**: private repository `razahasnain0300-max/dr.shoaib.zafar`.  
**Public website**: `https://drshoaibpsychiatrist.com/`.

The screenshot workflow captures the homepage, Why Dr. Shoaib? page and the blog using an unauthenticated Chromium browser, then replaces the portfolio's generic concept graphic with the actual homepage screenshot. Selected pages appear as additional image-only previews in `PORTFOLIO.md`.

No link from the website screenshot points to the live website or private GitHub repo; the images cannot redirect viewers to the website. Patient portals, admin pages, booking, private dashboards and authenticated routes are not captured.

The weekly workflow `.github/workflows/dr-shoaib-site-previews.yml` can also be run manually in GitHub Actions. Screenshots are publicly visible in the profile repository. If the homepage cannot be captured successfully, the workflow fails before changing the gallery and keeps the existing preview. The hourly project-gallery automation will continue using the real screenshot through `portfolio/curated_projects.json`.

This feature modifies only the GitHub profile repository, not the private source repository or manually deployed production website.
