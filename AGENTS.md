# Birding Bingo project guidance

Birding Bingo is a birding game and data-science portfolio project. Its current playable MVP is a mobile-friendly, static site for Montrose Point, Chicago. The longer-term goal is to support more places, hotspots, and times of year. Read `README.md` for the current implementation and data method before changing behavior.

## How to work here

- Let the user choose the scope and sequence of work. Treat the roadmap below as ideas to develop, not permission to implement them all at once.
- Answer direct questions directly and keep explanations concise.
- Preserve the current MVP's 5×5 card, 24 distinct birds, free center, toggleable marks, row/column/diagonal bingo, local progress, reset, new-card control, and selected date window unless a requested change supersedes them.
- The current site needs no account, backend, or live API. Revisit that architecture when a specific future feature calls for it.
- Check the result in a browser at mobile width when changing the page or game behavior.

## Current data and publishing

- `generate_card.py` reads a local eBird Basic Dataset archive from `data/raw/`. The `EBD_relAug-2022` archive is a Cook County extract (`US-IL-031`); Montrose's complete checklists in it span January 2012 through August 2022. `analysis/` contains a year-round aggregate preview and its reproducible builder.
- Year-round Montrose cards draw from **all eligible species** on complete checklists for hotspot `L161180` in the chosen one-of-48 date window, weighted by checklist reporting frequency and sampled without replacement. The original October 3–17 card data remains for previously saved cards. The top-30 CSV is a summary, not a draw limit.
- Do not commit or publish the original eBird archive. Keep the eBird citation and terms with published derivatives, and preserve attribution on the page.
- `outputs/` contains the static site and generated derivatives. `.github/workflows/pages.yml` publishes the playable site to GitHub Pages; review generated files and the deployment workflow before changing what is published.

## Project roadmap

- Make `README.md` a clean, easy-to-read portfolio presentation with at least one visual, potentially the playable game itself.
- Review and update `.gitignore` for files currently left visible or untracked that should not be committed.
- Expand card generation by place or hotspot and by time of year, working toward use of the full eBird dataset rather than only the current extract.
- Simulate games to estimate the percentage of cards that achieve bingo; state the observation, time-window, and player assumptions behind each estimate.
- Design Beginner, Intermediate, and Expert cards for a selected area and time, then extend those levels across supported areas and times.
- Build time-specific forecasts that show how a bird's chance of being reported changes across weeks or seasons, rather than using one frequency for a broad period.
- Model rarities, vagrants, and other outliers explicitly: distinguish isolated records from meaningful recent sightings, and allow unusual observations to change a rare bird's forecast when warranted.
- Much later, consider a process for incorporating newly available observations and refreshing cards and forecasts regularly.
