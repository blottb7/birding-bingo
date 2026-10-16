# Birding Bingo

First milestone: one printable, general-difficulty card for Montrose Point,
Chicago, for October 10, 2026.

## Generate the card

Keep the original eBird ZIP in `data/raw/`, then run:

```sh
python3 generate_card.py
```

The script streams the ZIP without extracting it and writes `outputs/card.html`
plus a 30-species aggregated frequency sample at
`outputs/montrose-october-species-summary.csv`. Open the HTML in a browser to
print the card. It also copies the dataset's terms of use and recommended
citation into `outputs/`.

## Sample-card method

The weighted sample card draws 24 distinct species from all species reported on complete
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
`outputs/card-most-common.html` without replacing the weighted card.

The dataset is version EBD_relAug-2022, with observations from 2012 through
September 2022.

The original dataset is excluded from version control. Do not publicly
redistribute it. Any shared card or other derived output must be accompanied
by the included eBird terms of use and citation, and used consistently with
those terms.
