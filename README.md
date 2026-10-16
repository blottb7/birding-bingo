# Birding Bingo

An interactive, mobile-friendly Birding Bingo card for Montrose Point, Chicago. Cards use historical bird frequencies for the selected time of year.

## Play or publish

Play at [blottb7.github.io/birding-bingo](https://blottb7.github.io/birding-bingo/) or open `outputs/index.html` locally. On a first visit, the card uses today's date in Chicago. Choose another date and press **Use this date** to start a card for its seasonal window. The current card stays in place across refreshes and midnight until you choose a new one. Tap birds to mark or unmark them; completed rows, columns, and diagonals are highlighted. **Reset marks** clears progress on the current card; **New card** draws another card for the current window. The card and marks are saved in this browser's local storage. No account, backend, or live API is needed.

To publish, serve the contents of `outputs/` as a static site, with
`outputs/index.html` as the entry point. Keep `birds.js`, `seasonal-data.js`, `app.js`,
`terms_of_use.txt`, and `recommended_citation.txt` in the same directory as
the page. Do not include `data/raw/` in the published site. Review the eBird
terms before publishing, particularly the noncommercial-use restriction.

For this public GitHub repository, `.github/workflows/pages.yml` publishes
only those six site files to GitHub Pages after a push to `main`. In the
repository's **Settings → Pages**, set **Build and deployment → Source** to
**GitHub Actions**. The public app URL will be
`https://blottb7.github.io/birding-bingo/`.

## Build year-round data

Keep the original Cook County eBird ZIP in `data/raw/`, then run:

```sh
ruby --disable-gems analysis/build_montrose_seasonality.rb
```

The script streams the ZIP, writes 48 date-window summaries and species frequencies to `analysis/`, and writes the static site's `outputs/seasonal-data.js`. Each month is split into days 1–7, 8–14, 15–21, and 22–month end. A bird's weight is the number of complete checklists in that window that report it; cards draw 24 distinct birds without replacement. See [`analysis/README.md`](analysis/README.md) for the data preview, coverage, and caveats.

## Generate the original October sample card

Keep the original eBird ZIP in `data/raw/`, then run:

```sh
python3 generate_card.py
```

This separate script streams the ZIP without extracting it and writes the original
October card data in `outputs/birds.js`, a printable `outputs/card.html`,
and a 30-species aggregated frequency sample at
`outputs/montrose-october-species-summary.csv`. Open the HTML in a browser to
print the card. It also copies the dataset's terms of use and recommended
citation into `outputs/`.

## Original October sample-card method

The original card and weighted sample card draw 24 distinct species from all species reported on complete
checklists for eBird hotspot `L161180`, October 3–17 across the available
years. Each species' draw weight is its number of reports in those checklists,
which is proportional to its historical reporting percentage. Thus a species
reported on 63% of checklists has about 37 times the weight of one reported
on 1.7% of checklists. This creates a general card that favors common birds
without limiting the draw to only the most common species. The displayed
percentages are historical checklist reporting frequencies—not guarantees
of seeing a species on October 10, 2026.

The draw is weighted sampling without replacement: a species can appear only
once on a card, even if its weight is high. This is a simple probability-based draw, not a Markov chain. Generate the
original baseline card of the 24 most frequently reported species with
`python3 generate_card.py --method common`; it writes
`outputs/card-most-common.html` without replacing the weighted card. The
30-species CSV is only a summary; the original draw uses every eligible
species in `birds.js`. Existing saved original cards remain playable after the year-round update.

The dataset is version EBD_relAug-2022. Montrose's complete checklists in the local archive span January 2012 through August 2022.

The original dataset is excluded from version control. Do not publicly
redistribute it. Any shared card or other derived output must be accompanied
by the included eBird terms of use and citation, and used consistently with
those terms.
