# Raw event logs — BPIC12 and BPIC17

This folder is intentionally empty in the public repository. The raw BPIC12 and BPIC17 event logs are not redistributed because the 4TU.ResearchData licence governs their distribution; they should be fetched directly from the source.

## How to obtain the raw data

### Option 1 — automated download

```bash
python data/raw/download_bpic_data.py
```

The helper script fetches both XES files from their persistent DOIs at 4TU.ResearchData and saves them under `data/raw/`. Total download size is approximately 250 MB; allow several minutes on a typical home connection.

### Option 2 — manual download

1. Visit https://doi.org/10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f for **BPIC12**.
2. Visit https://doi.org/10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b for **BPIC17**.
3. Download the `.xes.gz` file from each page.
4. Place both files into this `data/raw/` folder. The notebooks accept either gzipped or uncompressed XES.

## After download

Run notebook `01_data_cleaning.ipynb`. It will detect the raw files automatically and re-derive the case-level and stage-month CSVs in `data/processed/`. Notebooks 02-06 will then operate on the real data without further modification.

## Citations

- van Dongen, B. F. (2012). *BPI Challenge 2012* [Data set]. 4TU.ResearchData. https://doi.org/10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f
- van Dongen, B. F. (2017). *BPI Challenge 2017* [Data set]. 4TU.ResearchData. https://doi.org/10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b
