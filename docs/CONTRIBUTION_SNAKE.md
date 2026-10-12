# Purple Contribution Snake

The snake graphics are generated from real GitHub activity with `Platane/snk/svg-only@v3` twice daily. Both a dark and light SVG are stored in the published `output` branch. The README banner is immediately present even before the first run.

The workflow also copies the interactive HTML game from `interactive-snake/index.html` to `output/index.html`. In that browser application the snake roams randomly and follows the visitor's cursor/touch, using pathfinding and a responsive Canvas. The decorative grid in the interactive game is *not a genuine contribution calendar* and makes no fabricated count claims.

**To run:** Actions → Purple Contribution Snake → Run workflow. Automatic schedule is around 03:19 and 15:19 UTC, subject to GitHub scheduling delays.

**GitHub Pages:** For a publicly playable game, the account owner can enable Settings → Pages → Deploy from a branch → `output` / root. Only promote its GitHub Pages URL once the deployment is working.

Do not insert JavaScript into README, invent contributions or share private repository data. The action only needs its scoped, built-in GITHUB_TOKEN.
