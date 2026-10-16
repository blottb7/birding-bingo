#!/usr/bin/env python3
"""Generate a printable starter bingo card from the local eBird Basic Dataset."""

from __future__ import annotations

import argparse
import csv
import html
import random
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "outputs"
LOCATION_ID = "L161180"
LOCATION_NAME = "Montrose Point, Lincoln Park, Chicago"
TARGET_DATE = date(2026, 10, 10)
WINDOW_START = (10, 3)
WINDOW_END = (10, 17)
CARD_BIRD_COUNT = 24
EBIRD_COLUMNS = (
    "GLOBAL UNIQUE IDENTIFIER",
    "LAST EDITED DATE",
    "TAXONOMIC ORDER",
    "CATEGORY",
    "TAXON CONCEPT ID",
    "COMMON NAME",
    "SCIENTIFIC NAME",
    "SUBSPECIES COMMON NAME",
    "SUBSPECIES SCIENTIFIC NAME",
    "EXOTIC CODE",
    "OBSERVATION COUNT",
    "BREEDING CODE",
    "BREEDING CATEGORY",
    "BEHAVIOR CODE",
    "AGE/SEX",
    "COUNTRY",
    "COUNTRY CODE",
    "STATE",
    "STATE CODE",
    "COUNTY",
    "COUNTY CODE",
    "IBA CODE",
    "BCR CODE",
    "USFWS CODE",
    "ATLAS BLOCK",
    "LOCALITY",
    "LOCALITY ID",
    "LOCALITY TYPE",
    "LATITUDE",
    "LONGITUDE",
    "OBSERVATION DATE",
    "TIME OBSERVATIONS STARTED",
    "OBSERVER ID",
    "SAMPLING EVENT IDENTIFIER",
    "PROTOCOL TYPE",
    "PROTOCOL CODE",
    "PROJECT CODE",
    "DURATION MINUTES",
    "EFFORT DISTANCE KM",
    "EFFORT AREA HA",
    "NUMBER OBSERVERS",
    "ALL SPECIES REPORTED",
    "GROUP IDENTIFIER",
    "HAS MEDIA",
    "APPROVED",
    "REVIEWED",
    "REASON",
    "TRIP COMMENTS",
    "SPECIES COMMENTS",
)
SYNTHETIC_SPECIES = {
    "American Robin": "Turdus migratorius",
    "White-throated Sparrow": "Zonotrichia albicollis",
    "House Sparrow": "Passer domesticus",
    "Song Sparrow": "Melospiza melodia",
    "Canada Goose": "Branta canadensis",
    "Black-capped Chickadee": "Poecile atricapillus",
    "American Goldfinch": "Spinus tristis",
    "Mallard": "Anas platyrhynchos",
    "Ring-billed Gull": "Larus delawarensis",
    "Northern Cardinal": "Cardinalis cardinalis",
    "Downy Woodpecker": "Dryobates pubescens",
    "House Finch": "Haemorhous mexicanus",
    "Cooper's Hawk": "Accipiter cooperii",
    "Golden-crowned Kinglet": "Regulus satrapa",
    "White-crowned Sparrow": "Zonotrichia leucophrys",
    "European Starling": "Sturnus vulgaris",
    "Palm Warbler": "Setophaga palmarum",
    "Herring Gull": "Larus argentatus",
    "Winter Wren": "Troglodytes hiemalis",
    "Yellow-rumped Warbler": "Setophaga coronata",
}
SYNTHETIC_EVENTS = (
    ("2025-10-10", ("American Robin", "White-throated Sparrow", "House Sparrow")),
    ("2025-10-10", ("American Robin", "Song Sparrow", "Canada Goose")),
    ("2025-10-11", ("Black-capped Chickadee", "American Goldfinch", "Mallard")),
    ("2025-10-11", ("White-throated Sparrow", "Ring-billed Gull", "Northern Cardinal")),
    ("2025-10-12", ("Downy Woodpecker", "Song Sparrow", "House Finch")),
    ("2025-10-12", ("American Robin", "Cooper's Hawk", "Canada Goose")),
    ("2025-10-13", ("Golden-crowned Kinglet", "White-crowned Sparrow", "European Starling")),
    ("2025-10-13", ("Black-capped Chickadee", "Palm Warbler", "Mallard")),
    ("2025-10-14", ("Yellow-rumped Warbler", "House Sparrow", "Herring Gull")),
    ("2025-10-14", ("Winter Wren", "American Goldfinch", "Northern Cardinal")),
)


def month_day_in_window(observation_date: date) -> bool:
    month_day = (observation_date.month, observation_date.day)
    return WINDOW_START <= month_day <= WINDOW_END


def find_dataset(archive_path: Path | None) -> Path:
    if archive_path is not None:
        if not archive_path.is_file():
            raise FileNotFoundError(f"Dataset archive not found: {archive_path}")
        return archive_path

    archives = sorted(RAW_DIR.glob("*.zip"))
    if len(archives) != 1:
        raise RuntimeError(
            f"Expected exactly one ZIP archive in {RAW_DIR}, found {len(archives)}. "
            "Pass the intended archive with --archive."
        )
    return archives[0]


def analyze_dataset(archive_path: Path) -> tuple[int, Counter[str]]:
    with zipfile.ZipFile(archive_path) as archive:
        data_files = [
            name
            for name in archive.namelist()
            if name.startswith("ebd_") and name.endswith(".txt")
        ]
        if len(data_files) != 1:
            raise RuntimeError(
                f"Expected one eBird data file in {archive_path.name}, "
                f"found {len(data_files)}."
            )

        checklist_species: dict[str, set[str]] = defaultdict(set)
        with archive.open(data_files[0]) as data_file:
            rows = csv.DictReader(
                (line.decode("utf-8") for line in data_file),
                delimiter="\t",
            )
            required_columns = {
                "LOCALITY ID",
                "OBSERVATION DATE",
                "SAMPLING EVENT IDENTIFIER",
                "ALL SPECIES REPORTED",
                "CATEGORY",
                "COMMON NAME",
            }
            if rows.fieldnames is None or not required_columns.issubset(rows.fieldnames):
                raise RuntimeError("The eBird data file is missing required columns.")

            for row in rows:
                if row["LOCALITY ID"] != LOCATION_ID:
                    continue
                if row["ALL SPECIES REPORTED"] != "1":
                    continue

                try:
                    observation_date = date.fromisoformat(row["OBSERVATION DATE"])
                except ValueError as error:
                    raise RuntimeError(
                        f"Invalid observation date: {row['OBSERVATION DATE']!r}"
                    ) from error

                if not month_day_in_window(observation_date):
                    continue

                event_id = row["SAMPLING EVENT IDENTIFIER"]
                if not event_id:
                    raise RuntimeError("A matching row has no sampling event identifier.")

                # Every species row belonging to a complete checklist shares its event ID.
                checklist_species[event_id]
                if row["CATEGORY"] == "species" and row["COMMON NAME"]:
                    checklist_species[event_id].add(row["COMMON NAME"])

        if not checklist_species:
            raise RuntimeError(
                f"No complete checklists found for {LOCATION_NAME} "
                f"between October {WINDOW_START[1]} and {WINDOW_END[1]}."
            )

        frequency: Counter[str] = Counter()
        for species in checklist_species.values():
            frequency.update(species)
        return len(checklist_species), frequency


def render_card(
    species_frequency: Counter[str],
    checklist_count: int,
    output_path: Path,
    method: str,
) -> None:
    ranked_species = sorted(
        species_frequency.items(),
        key=lambda item: (-item[1], item[0].casefold()),
    )
    if len(ranked_species) < CARD_BIRD_COUNT:
        raise RuntimeError(
            f"Only {len(ranked_species)} species qualified; "
            f"need {CARD_BIRD_COUNT} to fill the card."
        )

    if method == "common":
        selected = ranked_species[:CARD_BIRD_COUNT]
    else:
        rng = random.Random(1010)
        remaining = ranked_species.copy()
        selected = []
        for _ in range(CARD_BIRD_COUNT):
            names, counts = zip(*remaining)
            picked = rng.choices(range(len(names)), weights=counts, k=1)[0]
            selected.append(remaining.pop(picked))

    cells = iter(selected)
    card_cells = []
    for index in range(25):
        if index == 12:
            card_cells.append('<div class="cell free">FREE<br>SPACE</div>')
            continue
        name, sightings = next(cells)
        percent = sightings / checklist_count * 100
        percent_text = f"{percent:.1f}" if percent < 10 else f"{percent:.0f}"
        card_cells.append(
            '<div class="cell"><strong>'
            f"{html.escape(name)}"
            "</strong><span>"
            f"{percent_text}% of checklists"
            "</span></div>"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Birding Bingo — {html.escape(LOCATION_NAME)}</title>
<style>
  :root {{ color-scheme: light; font-family: system-ui, sans-serif; }}
  body {{ color: #17342a; margin: 2rem auto; max-width: 900px; padding: 0 1rem; }}
  h1 {{ margin-bottom: .25rem; }}
  .meta, .method {{ color: #3f5a50; }}
  .card {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin: 1.5rem 0; }}
  .cell {{ align-items: center; aspect-ratio: 1; background: #edf4ee; border: 1px solid #9db4a4; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; padding: .4rem; text-align: center; }}
  .cell strong {{ font-size: clamp(.7rem, 2vw, 1rem); }}
  .cell span {{ font-size: clamp(.6rem, 1.5vw, .8rem); margin-top: .4rem; }}
  .free {{ background: #d8e9db; font-weight: 700; }}
  .notice {{ border-left: 4px solid #668b71; padding-left: 1rem; }}
  @media print {{ body {{ margin: 0; max-width: none; }} .no-print {{ display: none; }} }}
</style>
</head>
<body>
<h1>Birding Bingo</h1>
<p class="meta">{html.escape(LOCATION_NAME)} · Target date: {TARGET_DATE:%B %-d, %Y}</p>
<div class="card">
{''.join(card_cells)}
</div>
<p class="method">{'Baseline card: the 24 most frequently reported species' if method == 'common' else 'Sample general card: 24 distinct species drawn with probability proportional to how often each was reported'} on complete eBird checklists at this hotspot from October 3–17 across the dataset's available years. {'Percentages' if method == 'common' else 'Every eligible species can be drawn; more frequently reported birds have more weight and less frequent birds have less. Percentages'} show the share of those checklists reporting each bird ({checklist_count:,} complete checklists), not a guarantee of seeing it.</p>
<p class="notice">Source: eBird Basic Dataset, version EBD_relAug-2022, covering 2012–September 2022.
This card is a derived educational product. Keep it with the included eBird terms of use if shared;
do not share the original dataset.</p>
<p class="no-print">Print this page for the card.</p>
</body>
</html>
"""
    output_path.write_text(document, encoding="utf-8")


def write_species_summary(
    species_frequency: Counter[str],
    checklist_count: int,
    output_path: Path,
    limit: int = 30,
) -> None:
    ranked_species = sorted(
        species_frequency.items(),
        key=lambda item: (-item[1], item[0].casefold()),
    )[:limit]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as summary_file:
        writer = csv.writer(summary_file)
        writer.writerow(
            (
                "common_name",
                "complete_checklists_reporting_species",
                "complete_checklists_in_sample",
                "percent_of_complete_checklists",
            )
        )
        for common_name, count in ranked_species:
            writer.writerow(
                (
                    common_name,
                    count,
                    checklist_count,
                    round(count / checklist_count * 100, 2),
                )
            )


def write_synthetic_observations(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as sample_file:
        writer = csv.DictWriter(sample_file, fieldnames=EBIRD_COLUMNS)
        writer.writeheader()
        record_number = 0
        for event_number, (observation_date, species_names) in enumerate(
            SYNTHETIC_EVENTS, start=1
        ):
            for species_name in species_names:
                record_number += 1
                writer.writerow(
                    {
                        "GLOBAL UNIQUE IDENTIFIER": f"SYNTHETIC-OBS-{record_number:04d}",
                        "CATEGORY": "species",
                        "TAXON CONCEPT ID": f"SYNTHETIC-TAXON-{species_name.upper().replace(' ', '-')}",
                        "COMMON NAME": species_name,
                        "SCIENTIFIC NAME": SYNTHETIC_SPECIES[species_name],
                        "OBSERVATION COUNT": (record_number % 5) + 1,
                        "COUNTRY": "United States",
                        "COUNTRY CODE": "US",
                        "STATE": "Illinois",
                        "STATE CODE": "US-IL",
                        "COUNTY": "Cook",
                        "COUNTY CODE": "US-IL-031",
                        "LOCALITY": "Montrose Point (synthetic example)",
                        "LOCALITY ID": "SYNTH-L161180",
                        "LOCALITY TYPE": "H",
                        "OBSERVATION DATE": observation_date,
                        "TIME OBSERVATIONS STARTED": f"08:{(event_number * 7) % 60:02d}:00",
                        "OBSERVER ID": f"SYNTH-OBSERVER-{event_number:03d}",
                        "SAMPLING EVENT IDENTIFIER": f"SYNTH-EVENT-{event_number:03d}",
                        "PROTOCOL TYPE": "Traveling",
                        "PROTOCOL CODE": "SYNTH-PROTOCOL",
                        "PROJECT CODE": "SYNTHETIC-DEMO",
                        "DURATION MINUTES": 30 + (event_number % 4) * 5,
                        "EFFORT DISTANCE KM": f"{0.5 + (event_number % 3) * 0.2:.1f}",
                        "NUMBER OBSERVERS": 1,
                        "ALL SPECIES REPORTED": 1,
                        "HAS MEDIA": 0,
                        "APPROVED": 0,
                        "REVIEWED": 0,
                        "TRIP COMMENTS": "Entirely synthetic example; not an eBird record.",
                        "SPECIES COMMENTS": "Invented example value.",
                    }
                )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive",
        type=Path,
        help="eBird ZIP file (defaults to the only ZIP in data/raw/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="directory for the generated card and eBird attribution files",
    )
    parser.add_argument(
        "--method",
        choices=("weighted", "common"),
        default="weighted",
        help="weighted draw for the sample general card, or the original most-common baseline",
    )
    args = parser.parse_args()

    archive_path = find_dataset(args.archive)
    checklist_count, species_frequency = analyze_dataset(archive_path)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "montrose-october-species-summary.csv"
    write_species_summary(species_frequency, checklist_count, summary_path)
    write_synthetic_observations(
        args.output_dir / "synthetic-observation-sample.csv"
    )
    filename = "card.html" if args.method == "weighted" else "card-most-common.html"
    card_path = args.output_dir / filename
    render_card(species_frequency, checklist_count, card_path, args.method)

    with zipfile.ZipFile(archive_path) as archive:
        for source_name, output_name in (
            ("terms_of_use.txt", "terms_of_use.txt"),
            ("recommended_citation.txt", "recommended_citation.txt"),
        ):
            if source_name not in archive.namelist():
                raise RuntimeError(f"Dataset archive is missing {source_name}.")
            (args.output_dir / output_name).write_bytes(archive.read(source_name))

    print(f"Complete checklists: {checklist_count:,}")
    print(f"Eligible species: {len(species_frequency):,}")
    print(f"30-species aggregate sample created: {summary_path}")
    print(f"Card created: {card_path}")
    print(f"Keep the card with {args.output_dir / 'terms_of_use.txt'} if shared.")


if __name__ == "__main__":
    main()
