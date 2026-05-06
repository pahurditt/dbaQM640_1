"""
generate_synthetic_data.py

Produces three CSVs under data/processed/:
  - data_dictionary.csv         (machine-readable version of Table 2)
  - case_level_balanced_1000.csv  (1,000 cases, 500 per class, with realistic correlations)
  - stage_month_panel.csv         (76 rows: 4 stages x 19 months; pre/post system change)

These datasets are SYNTHETIC and intended to (a) demonstrate that the analytical
pipeline runs end-to-end and (b) give the author a structurally-correct shape into
which real BPIC-derived data can be substituted. The variable names, types, and
allowed values match the report's data dictionary exactly so that the notebooks
require no schema changes when real data is dropped in.

Author: Percival Hurditt (Walsh College, QM640, May 2026)
"""

import os
import numpy as np
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT_DIR, exist_ok=True)

RNG = np.random.default_rng(seed=42)


# ---------------------------------------------------------------------------
# 1) data dictionary
# ---------------------------------------------------------------------------
DICT_ROWS = [
    ("case_id", "Unique identifier for each loan application", "String",
     "BPIC12 / BPIC17 case attribute", "Application_652823328",
     "Primary key linking events to cases",
     "Joining events to case-level features; deduplication."),
    ("activity_name", "Name of the activity performed", "Categorical (24 levels)",
     "BPIC event field 'concept:name'", "A_Complete",
     "Identifies which step of the workflow occurred",
     "Mapped to stages via activity_to_stage_mapping.csv; defines Stage-1 inclusion."),
    ("timestamp", "Datetime the activity was completed", "Datetime",
     "BPIC event field 'time:timestamp'", "2016-03-12 09:14:22",
     "Anchors all duration and SLA computations",
     "Computes processing time, SLA breach flag, month index for ITS."),
    ("lifecycle_transition", "Lifecycle phase of the activity",
     "Categorical (start, complete, schedule, etc.)",
     "BPIC event field 'lifecycle:transition'", "complete",
     "Distinguishes when a step started vs ended",
     "Filtered to 'complete' for duration calculations."),
    ("resource", "Identifier for the human or system processor", "String",
     "BPIC event field 'org:resource'", "User_104",
     "Indicates capacity attribution at the event",
     "Constructs resource-workload feature; resource-level audit."),
    ("requested_amount", "Loan amount requested by applicant", "Numeric (EUR)",
     "BPIC case attribute 'AMOUNT_REQ'", "15000",
     "Credit and operational risk indicator",
     "Log-transformed feature for RQ1, RQ2; segmentation in EDA."),
    ("submission_channel", "Channel through which the application originated",
     "Categorical (branch, web, partner)",
     "Derived from resource and event sequence", "web",
     "Identifies origination pathway",
     "One-hot encoded feature for RQ1 and RQ2."),
    ("product_type", "Loan product family", "Categorical (consumer, mortgage, SME)",
     "Derived from BPIC documentation and amount band", "consumer",
     "Operational complexity proxy",
     "Feature for RQ1 and RQ2; subgroup robustness."),
    ("product_complexity_index", "Ordinal complexity score (1–5)", "Numeric (ordinal)",
     "Engineered from product_type and amount", "3",
     "Captures handling complexity in a single covariate",
     "Feature for RQ1 turnaround time model."),
    ("completeness_flag",
     "Whether the application reached A_Complete without entering A_Incomplete",
     "Binary (0/1)", "Derived from event sequence", "1",
     "Quality of submission at intake",
     "Feature for RQ1 and RQ2; key intervention lever."),
    ("exception_flag",
     "Whether the case experienced an A_Incomplete event during Stage 1",
     "Binary (0/1)", "Derived from event sequence", "0",
     "Stage-1 exception indicator",
     "Outcome component for RQ2 risk flag; KPI for RQ1 and RQ3."),
    ("rework_indicator", "Number of times the case visited A_Incomplete", "Integer",
     "Derived from event sequence", "0",
     "Severity of intake rework",
     "Feature for RQ1; descriptive for EDA."),
    ("stage1_processing_time",
     "Duration from A_Create Application to A_Validating (hours)", "Numeric",
     "Derived from timestamps", "12.4",
     "Stage-1 turnaround time per case",
     "Outcome for RQ1; aggregated to KPI for RQ3."),
    ("sla_breach_flag",
     "Whether stage1_processing_time exceeds the pooled 75th percentile",
     "Binary (0/1)", "Derived using stage-level threshold", "0",
     "Operational-target adherence",
     "Outcome component for RQ2 risk flag; KPI for RQ3."),
    ("risk_flag",
     "Composite outcome: 1 if exception_flag=1 OR any sla_breach in case else 0",
     "Binary (0/1)", "Engineered", "1",
     "Composite Stage-1 risk indicator",
     "Target for RQ2 logistic-regression classifier."),
    ("customer_segment", "Segment derived from amount band and product type",
     "Categorical (4 levels)", "Engineered", "mass-affluent",
     "Customer-mix descriptor",
     "Feature for RQ1 and RQ2; subgroup analysis."),
    ("recent_exception_rate",
     "Resource-level exception rate over the trailing 7 days",
     "Numeric (proportion)", "Engineered from event sequence", "0.18",
     "Capacity-strain proxy",
     "Feature for RQ1; sensitivity in RQ2."),
    ("resource_workload",
     "Number of active cases assigned to the resource at the case timestamp",
     "Integer", "Engineered from event sequence", "11",
     "Operational capacity strain indicator",
     "Feature for RQ1 and RQ2."),
    ("era", "Pre- or post-system-change indicator", "Binary (0/1)",
     "Engineered (0 = BPIC12, 1 = BPIC17)", "1",
     "Identifies the natural-experiment period",
     "Used in RQ3 ITS as the change indicator D_t."),
    ("month_index", "Sequential month index across the combined panel",
     "Integer (1-19)", "Engineered", "9",
     "Time variable for the ITS regression",
     "Used in RQ3 ITS as the time covariate t."),
    ("approval_verification_outcome",
     "Result of the W_Validate application activity at end of Stage 1",
     "Categorical (validated, returned-for-rework, escalated)",
     "Derived from terminal Stage-1 event", "validated",
     "Stage-1 verification disposition; closes the intake stage",
     "Auxiliary outcome for Stage-1 quality monitoring; not used as a feature in RQ2."),
    ("risk_category",
     "Discrete band derived from the model's continuous risk score",
     "Categorical (low, medium, high)",
     "Engineered from RQ2 model output (P<0.30, 0.30-0.65, >=0.65)", "medium",
     "Operational routing label used by the workflow router",
     "Output variable of the RQ2 classifier; consumed by the deployment scenario."),
    ("final_transaction_outcome",
     "Terminal application disposition observed at end of case",
     "Categorical (A_Pending, A_Cancelled, A_Denied, O_Accepted, O_Refused, O_Cancelled)",
     "BPIC case attribute (terminal activity)", "A_Pending",
     "End-state of the loan application; downstream of Stage 1",
     "Documented for completeness; gold-standard label for risk-flag construction."),
]
DICT_COLS = [
    "variable_name", "description", "data_type", "source",
    "example_value", "business_meaning", "use_in_model_or_analysis",
]
pd.DataFrame(DICT_ROWS, columns=DICT_COLS).to_csv(
    os.path.join(OUT_DIR, "data_dictionary.csv"), index=False
)
print("Wrote data_dictionary.csv")


# ---------------------------------------------------------------------------
# 2) case-level balanced sample (n = 1,000; 500 per class)
# ---------------------------------------------------------------------------
def generate_case_level(n_per_class: int = 500) -> pd.DataFrame:
    """Synthetic case-level data with realistic Stage-1 feature correlations.

    Class signal is intentionally moderate (CV AUC ~0.78) to match the report's
    preliminary findings. Risk-positive cases (risk_flag=1) tend to have:
      - completeness_flag = 0 more often, but not exclusively
      - higher resource_workload (overlapping distributions)
      - higher recent_exception_rate (overlapping distributions)
      - somewhat longer stage1_processing_time
    """
    rows = []
    cid = 0
    for risk_flag in (0, 1):
        for _ in range(n_per_class):
            cid += 1

            # softer class signals: meaningful but with substantial overlap
            if risk_flag == 1:
                completeness_flag = int(RNG.random() < 0.72)  # often complete!
                channel_p = [0.32, 0.48, 0.20]
                workload = int(RNG.normal(12, 4))
                recent_exc = float(np.clip(RNG.normal(0.18, 0.08), 0, 0.6))
                tat_base = RNG.lognormal(mean=3.0, sigma=1.0)
                rework = int(RNG.poisson(0.45))
            else:
                completeness_flag = int(RNG.random() < 0.88)
                channel_p = [0.42, 0.38, 0.20]
                workload = int(RNG.normal(10, 4))
                recent_exc = float(np.clip(RNG.normal(0.13, 0.06), 0, 0.45))
                tat_base = RNG.lognormal(mean=2.6, sigma=1.0)
                rework = int(RNG.poisson(0.20))

            workload = max(1, workload)
            channel = RNG.choice(["branch", "web", "partner"], p=channel_p)
            requested_amount = float(np.clip(RNG.lognormal(mean=9.5, sigma=0.7),
                                             500, 75_000))
            product_type = RNG.choice(["consumer", "mortgage", "SME"],
                                      p=[0.7, 0.2, 0.1])
            complexity = (
                {"consumer": 2, "mortgage": 4, "SME": 3}[product_type]
                + int(RNG.integers(-1, 2))
            )
            complexity = int(np.clip(complexity, 1, 5))

            # TAT is built from explicit feature contributions plus log-normal noise
            # so RQ1 Lasso can recover meaningful coefficients (target R^2 ~ 0.30-0.40).
            channel_effect    = {"branch": 4.0, "web": -2.0, "partner": 0.0}[channel]
            completeness_eff  = -6.0 if completeness_flag == 1 else 8.0
            complexity_eff    = 1.5 * (complexity - 3)
            workload_eff      = 0.4 * (workload - 10)
            recent_exc_eff    = 18.0 * (recent_exc - 0.15)
            log_amount_eff    = 1.0 * (np.log(requested_amount) - 9.5)
            rework_eff        = 4.0 * rework
            base_tat          = 18.0
            noise             = float(RNG.lognormal(mean=0.0, sigma=0.95)) * 9.0
            tat = (base_tat + completeness_eff + channel_effect + complexity_eff
                   + workload_eff + recent_exc_eff + log_amount_eff
                   + rework_eff + noise)
            tat = float(np.clip(tat, 0.5, 240))

            # Outcomes have noise — they are influenced by features but not deterministic
            exception_flag = int(RNG.random() < (0.10 + 0.30 * (1 - completeness_flag)
                                                 + 0.40 * recent_exc))
            sla_breach_flag = int(tat > 36)

            # Honor the assigned risk_flag class as the SAMPLED ground truth, but
            # let the features reflect noisy underlying drivers. We do NOT force-flip
            # features to match the class — that's what was driving AUC to 1.0.
            # Instead, the class label IS the risk_flag we assigned at the top of the
            # loop, which corresponds to the scenario where the case did/did not have
            # downstream risk. The features are the noisy intake-time signal.

            if requested_amount < 5000:
                segment = "mass-market"
            elif requested_amount < 20000:
                segment = "mass-affluent"
            elif requested_amount < 50000:
                segment = "affluent"
            else:
                segment = "high-net-worth"

            era = int(RNG.random() < 0.71)
            month_index = int(RNG.integers(1, 7) if era == 0
                              else RNG.integers(7, 20))

            if completeness_flag == 1 and exception_flag == 0:
                approval = "validated"
            elif completeness_flag == 0:
                approval = "returned-for-rework"
            else:
                approval = "escalated"

            if risk_flag == 0:
                final_outcome = RNG.choice(
                    ["O_Accepted", "A_Pending", "O_Refused"],
                    p=[0.78, 0.15, 0.07])
            else:
                final_outcome = RNG.choice(
                    ["A_Cancelled", "A_Denied", "O_Cancelled",
                     "O_Refused", "O_Accepted"],
                    p=[0.30, 0.25, 0.18, 0.17, 0.10])

            rows.append({
                "case_id": f"Application_{1_000_000 + cid}",
                "requested_amount": round(requested_amount, 2),
                "submission_channel": channel,
                "product_type": product_type,
                "product_complexity_index": complexity,
                "completeness_flag": completeness_flag,
                "exception_flag": exception_flag,
                "rework_indicator": rework,
                "stage1_processing_time": round(tat, 2),
                "sla_breach_flag": sla_breach_flag,
                "risk_flag": risk_flag,
                "customer_segment": segment,
                "recent_exception_rate": round(recent_exc, 3),
                "resource_workload": workload,
                "era": era,
                "month_index": month_index,
                "approval_verification_outcome": approval,
                "final_transaction_outcome": str(final_outcome),
            })
    df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
    return df


case_df = generate_case_level()
case_df.to_csv(os.path.join(OUT_DIR, "case_level_balanced_1000.csv"), index=False)
print(f"Wrote case_level_balanced_1000.csv ({len(case_df)} rows, "
      f"{case_df['risk_flag'].mean():.1%} positive)")


# ---------------------------------------------------------------------------
# 3) stage-month panel (76 rows: 4 stages × 19 months)
# ---------------------------------------------------------------------------
def generate_stage_month_panel() -> pd.DataFrame:
    rows = []
    stages = [
        ("S1", "Application Intake and Validation"),
        ("S2", "Offer Preparation and Dispatch"),
        ("S3", "Customer Response and Callback"),
        ("S4", "Final Decision and Closure"),
    ]
    for stage_id, stage_name in stages:
        # baseline level per stage
        base_pre = {"S1": 38.0, "S2": 22.0, "S3": 31.0, "S4": 18.0}[stage_id]
        base_post = {"S1": 26.0, "S2": 17.0, "S3": 24.0, "S4": 14.0}[stage_id]
        excp_pre = {"S1": 0.21, "S2": 0.13, "S3": 0.18, "S4": 0.09}[stage_id]
        excp_post = {"S1": 0.15, "S2": 0.10, "S3": 0.13, "S4": 0.07}[stage_id]
        for m in range(1, 20):
            era = 0 if m <= 6 else 1
            tat_base = base_pre if era == 0 else base_post
            excp_base = excp_pre if era == 0 else excp_post
            # mild post-period downward slope for TAT
            slope = (-0.20 * (m - 6)) if era == 1 else 0.0
            tat = tat_base + slope + RNG.normal(0, 1.6)
            excp = excp_base + RNG.normal(0, 0.012)
            sla_br = excp * 0.95 + RNG.normal(0, 0.015)
            ftr = 1 - excp - 0.03 + RNG.normal(0, 0.02)
            volume = int(np.clip(RNG.normal(2300 if era == 1 else 1500, 200),
                                 800, 4000))
            rows.append({
                "stage_id": stage_id,
                "stage_name": stage_name,
                "month_index": m,
                "era": era,
                "transaction_volume": volume,
                "mean_processing_time": round(tat, 2),
                "exception_rate": round(np.clip(excp, 0, 1), 4),
                "sla_breach_rate": round(np.clip(sla_br, 0, 1), 4),
                "first_time_right": round(np.clip(ftr, 0, 1), 4),
                "reconciliation_breaks": int(RNG.poisson(8 if era == 0 else 4)),
            })
    return pd.DataFrame(rows)


panel_df = generate_stage_month_panel()
panel_df.to_csv(os.path.join(OUT_DIR, "stage_month_panel.csv"), index=False)
print(f"Wrote stage_month_panel.csv ({len(panel_df)} rows)")


# ---------------------------------------------------------------------------
# 4) activity-to-stage mapping
# ---------------------------------------------------------------------------
mapping = pd.DataFrame({
    "activity_name": [
        "A_Create Application", "A_Concept", "A_Accepted", "A_Complete",
        "A_Validating", "A_Incomplete", "W_Validate application", "W_Handle leads",
        "O_Create Offer", "O_Sent", "W_Assess potential fraud",
        "O_Returned", "W_Call after offers", "W_Call incomplete files",
        "A_Pending", "A_Cancelled", "A_Denied",
        "O_Accepted", "O_Refused", "O_Cancelled",
    ],
    "stage_id": (
        ["S1"] * 8 +
        ["S2"] * 3 +
        ["S3"] * 3 +
        ["S4"] * 6
    ),
    "stage_name": (
        ["Application Intake and Validation"] * 8 +
        ["Offer Preparation and Dispatch"] * 3 +
        ["Customer Response and Callback"] * 3 +
        ["Final Decision and Closure"] * 6
    ),
})
mapping.to_csv(os.path.join(OUT_DIR, "activity_to_stage_mapping.csv"), index=False)
print(f"Wrote activity_to_stage_mapping.csv ({len(mapping)} rows)")

print("\nSynthetic data generation complete.")
