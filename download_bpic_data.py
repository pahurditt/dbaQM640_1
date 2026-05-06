"""
download_bpic_data.py

Fetches the BPIC12 and BPIC17 event logs from 4TU.ResearchData and stores
them under data/raw/. The persistent DOIs resolve to download URLs that
serve the underlying XES files; the helper follows redirects and writes
the files with their canonical names.

Usage:
    python data/raw/download_bpic_data.py
    python data/raw/download_bpic_data.py --skip-bpic12   # only BPIC17
    python data/raw/download_bpic_data.py --force         # re-download

The script is idempotent: if files already exist with non-zero size and
--force is not passed, the existing files are kept.
"""

import argparse
import sys
import urllib.request
from pathlib import Path

# 4TU.ResearchData direct download endpoints
# (these resolve from the DOIs cited in the report bibliography)
BPIC12_URL = (
    "https://data.4tu.nl/file/533f66a4-8911-4ac7-8612-1235d65d1f37/"
    "3276db7f-8bee-4f2b-88ee-92dbffb5a893"
)
BPIC17_URL = (
    "https://data.4tu.nl/file/34c3f44b-3101-4ea9-8281-e38905c68b8d/"
    "f3aec4f7-d52c-4217-82f4-57d719a8298c"
)

TARGETS = [
    ("BPIC12.xes.gz", BPIC12_URL),
    ("BPIC17.xes.gz", BPIC17_URL),
]


def download(url: str, dest: Path) -> None:
    print(f"Downloading {dest.name} ...")
    print(f"  source: {url}")
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            done = 0
            chunk = 1 << 20  # 1 MB
            with dest.open("wb") as fh:
                while True:
                    buf = resp.read(chunk)
                    if not buf:
                        break
                    fh.write(buf)
                    done += len(buf)
                    if total:
                        pct = 100 * done / total
                        print(f"\r  progress: {done/1e6:8.1f} / "
                              f"{total/1e6:8.1f} MB  ({pct:5.1f}%)",
                              end="", flush=True)
        print(f"\n  saved to {dest}")
    except Exception as e:
        print(f"\n  ERROR: {e}", file=sys.stderr)
        print("  Manual download fallback:")
        print("    BPIC12: https://doi.org/10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f")
        print("    BPIC17: https://doi.org/10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-bpic12", action="store_true")
    parser.add_argument("--skip-bpic17", action="store_true")
    parser.add_argument("--force", action="store_true",
                        help="re-download even if files exist")
    args = parser.parse_args()

    raw_dir = Path(__file__).resolve().parent
    for fname, url in TARGETS:
        if args.skip_bpic12 and "BPIC12" in fname:
            continue
        if args.skip_bpic17 and "BPIC17" in fname:
            continue
        dest = raw_dir / fname
        if dest.exists() and dest.stat().st_size > 0 and not args.force:
            print(f"Already present: {dest.name} "
                  f"({dest.stat().st_size/1e6:.1f} MB) — skipping")
            continue
        download(url, dest)

    print("\nDone. Run notebook 01_data_cleaning.ipynb to process the raw logs.")


if __name__ == "__main__":
    main()
