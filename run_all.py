"""
run_all.py — execute every notebook in order.

Equivalent to:
    jupyter nbconvert --to notebook --execute --inplace notebooks/01_*.ipynb
    jupyter nbconvert --to notebook --execute --inplace notebooks/02_*.ipynb
    ... (etc) ...

Usage:
    python scripts/run_all.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "notebooks"

ORDER = [
    "01_data_cleaning.ipynb",
    "02_eda.ipynb",
    "03_lasso_rq1.ipynb",
    "04_logistic_rq2.ipynb",
    "05_its_rq3.ipynb",
    "06_mcda_rq4.ipynb",
]


def main():
    failed = []
    for nb in ORDER:
        path = NB_DIR / nb
        if not path.exists():
            print(f"SKIP   {nb} (not found)")
            continue
        print(f"RUN    {nb}")
        result = subprocess.run(
            ["jupyter", "nbconvert", "--to", "notebook",
             "--execute", "--inplace", str(path)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"FAILED {nb}")
            print(result.stderr[-1500:])
            failed.append(nb)
        else:
            print(f"OK     {nb}")
    if failed:
        print(f"\n{len(failed)} notebook(s) failed: {failed}")
        sys.exit(1)
    print("\nAll notebooks executed successfully.")


if __name__ == "__main__":
    main()
