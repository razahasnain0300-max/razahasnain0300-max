# Hadia Collection — Real Public Fashion Storefront Preview

Matched private code repository `razahasnain0300-max/hadia-collection` with publicly accessible `https://hadia-collection.online/`.

This workflow uses headless Chromium for real screenshots from approved anonymous storefront pages (Homepage, New Arrivals, Collections, Upcoming, About, Contact, Delivery Information). It refuses private, customer, admin, cart, checkout and order pages. The screenshots have no hyperlink to the live website.

The profile displays a large public homepage capture, selected mini-previews and a rich e-commerce case study. User-facing headings and SEO meta descriptions extracted from the website are reported in workflow logs; technical features derive from the repository's own documented implementation, without disclosing source code.

Type: Fashion E-Commerce Website / Online Store.
Stack: Node.js, Express, EJS, MySQL, Socket.IO.
Features: collections, new arrivals, catalog filtering, sizes/colors, cart, COD checkout, tracking, accounts, ratings/reviews, inventory, returns, realtime update notifications and support.

The workflow runs weekly and can be launched manually. The hourly general gallery picks up the same real screenshot from the curated manifest. If screenshot capture fails its quality threshold, the previous gallery is retained.
