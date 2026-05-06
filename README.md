# dbaQM640 — Capstone Companion Package

**AI- and ML-Enabled Transaction Workflow Optimization for Group Operations in Banking and Finance: A Stage-One Proof of Concept for Application Intake and Validation**

Walsh College — QM640 Data Analytics Capstone — May 2026, Term 3
Author: Percival Hurditt
Mentor: Mr. Sridhar Srinivas

This repository accompanies the Capstone Interim Report. It contains the data files, Jupyter notebooks, and figures referenced in the report, structured so that the entire analytical pipeline can be reproduced end-to-end.

---

## Quick start

```bash
# 1. Clone the repository
git clone https://github.com/pahurditt/dbaQM640.git
cd dbaQM640

# 2. Create a Python environment (Python 3.11+ recommended)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate the synthetic processed datasets (one-time setup)
python scripts/generate_synthetic_data.py

# 5. Open and run the notebooks in order
jupyter notebook notebooks/
```

Run the notebooks in this order:

1. `01_data_cleaning.ipynb` — documents the cleaning pipeline; runs against raw BPIC data when available, otherwise verifies the synthetic processed CSVs.
2. `02_eda.ipynb` — produces Figures 1, 2, and 3.
3. `03_lasso_rq1.ipynb` — fits the RQ1 Lasso driver model; produces Figure 4.
4. `04_logistic_rq2.ipynb` — fits the RQ2 logistic-regression classifier; produces Figure 5.
5. `05_its_rq3.ipynb` — fits the RQ3 segmented-regression model with Newey-West HAC standard errors and robustness checks.
6. `06_mcda_rq4.ipynb` — runs the RQ4 weighted-scoring multi-criteria decision analysis.

---

## Repository layout

```
dbaQM640/
├── README.md                     this file
├── requirements.txt              Python dependencies
├── scripts/
│   ├── generate_synthetic_data.py   builds the processed CSVs
│   ├── build_notebooks.py           regenerates the six notebooks
│   └── run_all.py                   convenience: runs the full pipeline
├── data/
│   ├── raw/
│   │   ├── README.md                instructions for fetching BPIC12/BPIC17
│   │   └── download_bpic_data.py    download helper
│   └── processed/
│       ├── data_dictionary.csv      machine-readable variable definitions
│       ├── case_level_balanced_1000.csv   1,000 cases (500 per class)
│       ├── stage_month_panel.csv          76 rows: 4 stages x 19 months
│       └── activity_to_stage_mapping.csv  Stage-1 activity inclusion list
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_lasso_rq1.ipynb
│   ├── 04_logistic_rq2.ipynb
│   ├── 05_its_rq3.ipynb
│   └── 06_mcda_rq4.ipynb
└── figures/
    ├── fig1_stage1_process_map.png
    ├── fig2_processing_time_hist.png
    ├── fig3_its_panel.png
    ├── fig4_lasso_coefs.png
    ├── fig5_roc_cm.png
    └── fig6_deployment.png
```

---

## Data sources and the synthetic-vs-real distinction

The primary datasets are the **BPIC12** and **BPIC17** event logs released by van Dongen (2012, 2017) on the 4TU.ResearchData repository. Both logs cover the loan-application process of the same Dutch financial institute; between the two releases, the institute deployed a new case-management system. This is the natural-experiment basis for RQ3.

Because the raw XES files are large (hundreds of megabytes when uncompressed) and licensed for download from 4TU.ResearchData rather than redistribution, this repository ships with:

- **A download helper** (`data/raw/download_bpic_data.py`) that fetches the raw XES files from 4TU on demand.
- **Synthetic processed datasets** under `data/processed/` that match the schema of the data dictionary exactly. These are sufficient for running the entire pipeline end-to-end and for verifying that the methods work as documented.

**The numerical results produced by the notebooks on the synthetic data will not exactly match the illustrative figures cited in the Interim Report.** The synthetic data is calibrated to produce qualitatively correct findings (the classifier discriminates, the ITS shows a level shift, the MCDA selects a top intervention) but the exact magnitudes will differ. To reproduce the report's numbers exactly, run notebook 01 against the raw BPIC files; this will overwrite the synthetic processed CSVs with real BPIC-derived data, and notebooks 02-06 will then produce report-aligned outputs without further modification.

The synthetic data generator uses `numpy.random.default_rng(seed=42)`, so the synthetic outputs are themselves reproducible across machines.

---

## Method-to-research-question mapping

| RQ | Question | Method | Notebook | Primary output |
|----|----------|--------|----------|----------------|
| RQ1 | Which Stage-1 factors drive turnaround time? | Lasso regression | `03_lasso_rq1.ipynb` | `fig4_lasso_coefs.png` |
| RQ2 | Can a classifier predict downstream risk from Stage-1 features? | Logistic regression | `04_logistic_rq2.ipynb` | `fig5_roc_cm.png` |
| RQ3 | Did the system change move Stage-1 KPIs? | Segmented ITS regression | `05_its_rq3.ipynb` | (segmented-regression diagnostics) |
| RQ4 | Which Stage-1 micro-intervention should we ship first? | Weighted-scoring MCDA | `06_mcda_rq4.ipynb` | (priority-score table) |
| Diag | What does the Stage-1 workflow look like? | Process mining | `02_eda.ipynb` | `fig1_stage1_process_map.png` |

---

## Reproducibility checklist

- [x] Random seeds set in every notebook (numpy and scikit-learn).
- [x] `requirements.txt` pins major package versions.
- [x] Figures saved at 160 dpi for slide deck and report use.
- [x] All cells execute without manual intervention.
- [x] Synthetic data generator is deterministic (`seed=42`).

To regenerate everything from scratch:

```bash
python scripts/generate_synthetic_data.py
python scripts/build_notebooks.py
python scripts/run_all.py        # executes all six notebooks
```

---

## Citations

- van Dongen, B. F. (2012). *BPI Challenge 2012* [Data set]. 4TU.ResearchData. https://doi.org/10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f
- van Dongen, B. F. (2017). *BPI Challenge 2017* [Data set]. 4TU.ResearchData. https://doi.org/10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b

Full bibliography is in the Interim Report.

---

## License

The code in this repository is released under the MIT License for academic and research use. The BPIC12 and BPIC17 raw data are licensed by 4TU.ResearchData under their terms; please review and comply with their license when downloading.
