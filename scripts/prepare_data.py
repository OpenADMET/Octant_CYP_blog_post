#!/usr/bin/env python3
"""Preprocess raw data files into clean outputs for the blog post.

Reactivity: reads from data/raw/.
Inhibition + DRC plots: downloaded from Argo LIMS.

Requires ARGO_BASE_URL and ARGO_API_KEY environment variables.
"""

import shutil
from io import BytesIO
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import pandas as pd
import requests
from pathlib import Path

from argo_api import get_experiments, get_analysis_data_by_id

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"

INHIBITION_EXPERIMENT = "OPA_C3A4IAP-005"
POSITIVE_CONTROL = "OCNT-1911793"

# ---- Reactivity ----

peak_areas = pd.read_csv(
    RAW / "20260209_CBR-1304-cpds_vs_CYP3A4,2J2_primary_ind-reps_filtered.csv"
)

# keep only molecules present in BOTH CYP3A4 and CYP2J2
molecules_by_enzyme = peak_areas.groupby("enzyme")["ocnt_batch"].apply(set)
both = molecules_by_enzyme["CYP3A4"] & molecules_by_enzyme["CYP2J2"]
peak_areas = peak_areas[peak_areas["ocnt_batch"].isin(both)]

# join SMILES from compound table
cpds = pd.read_csv(
    RAW / "2025-09-10_selected-cpds.tsv",
    sep="\t",
    usecols=["ocnt_batch", "cxsmiles"],
).drop_duplicates(subset="ocnt_batch")
peak_areas = peak_areas.merge(cpds, on="ocnt_batch", how="left")

peak_areas = peak_areas[
    [
        "ocnt_batch", "cxsmiles",                        # molecule
        "enzyme", "condition", "plate", "well",           # experimental design
        "time_start", "time_end",                         # time window
        "mz_query", "mz_observed", "mass_error_ppm",      # mass spec
        "area",                                           # measurement
    ]
]
peak_areas.to_csv(OUT / "reactivity.tsv", sep="\t", index=False)
print(
    f"reactivity.tsv  : {len(peak_areas):,} rows, "
    f"{peak_areas['ocnt_batch'].nunique()} molecules  "
    f"(kept {len(both)} with both enzymes)"
)

# ---- Inhibition (from Argo) ----

print(f"\nFetching experiment {INHIBITION_EXPERIMENT} from Argo...")
experiments = get_experiments(name=INHIBITION_EXPERIMENT)
assert len(experiments) == 1, (
    f"Expected 1 experiment, got {len(experiments)}"
)
experiment = experiments[0]
analysis_id = experiment["primary_analysis"]
assert analysis_id is not None, "No primary analysis set for experiment"
print(f"  Primary analysis ID: {analysis_id}")

analysis_data = get_analysis_data_by_id(analysis_id)
processed_url = next(
    item["data"] for item in analysis_data if item["file_type"] == "PROCESSED_DATA"
)

print("  Downloading processed data zip...")
with NamedTemporaryFile(suffix=".zip", delete=True) as tf:
    with requests.get(processed_url, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=2**14):
            if chunk:
                tf.write(chunk)
    tf.flush()

    with ZipFile(tf.name) as zf:
        # find the prefix (top-level folder name in the zip)
        prefix = next(
            (n for n in zf.namelist() if n.endswith("curves-bayesian.tsv")), None
        )
        assert prefix is not None, "curves-bayesian.tsv not found in zip"
        prefix = prefix.rsplit("curves-bayesian.tsv", 1)[0]

        # extract text data files
        curves_bytes = zf.read(prefix + "curves-bayesian.tsv")
        qcflags_bytes = zf.read(prefix + "qcflags.tsv")
        qc_plate_bytes = zf.read(prefix + "qc_plate_decision.tsv")
        stats_bytes = zf.read(prefix + "stats.tsv")
        outliers_bytes = zf.read(prefix + "outliers_drc.tsv")

        # extract DRC plot PNGs
        drc_dir = OUT / "inhibition_drc-plots"
        drc_dir.mkdir(exist_ok=True)
        n_plots = 0
        for name in zf.namelist():
            if "drc-plots/" in name and name.endswith("_no-ctrls.png"):
                png_filename = name.split("/")[-1]
                if png_filename:
                    zf.extract(name, path=tf.name + "_tmp")
                    shutil.move(
                        Path(tf.name + "_tmp") / name,
                        drc_dir / png_filename,
                    )
                    n_plots += 1
        # clean up temp extraction dir
        tmp_dir = Path(tf.name + "_tmp")
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        print(f"  Extracted {n_plots} DRC plot images to data/inhibition_drc-plots/")

# parse curves-bayesian.tsv → inhibition.tsv
curves = pd.read_csv(BytesIO(curves_bytes), sep="\t")
qcflags = pd.read_csv(BytesIO(qcflags_bytes), sep="\t")
qc_plate = pd.read_csv(BytesIO(qc_plate_bytes), sep="\t")

# build ocnt_batch from molecule_name + batch_name
curves["ocnt_batch"] = curves["molecule_name"] + "-" + curves["batch_name"]
qcflags["ocnt_batch"] = qcflags["molecule_name"] + "-" + qcflags["batch_name"]

# extract pEC50 estimates
pec50 = curves[curves["term"] == "pEC50"][
    ["ocnt_batch", "compound_class", "estimate", "std.error", "conf.low", "conf.high"]
].copy()
pec50 = pec50.rename(columns={
    "estimate": "CYP3A4_pIC50",
    "std.error": "CYP3A4_pIC50_se",
    "conf.low": "CYP3A4_pIC50_ci_lower",
    "conf.high": "CYP3A4_pIC50_ci_upper",
})

# extract hill slope (SlopeLog2) and amplitude (EmaxLog2FC) for curve reconstruction
slope = curves[curves["term"] == "SlopeLog2"][
    ["ocnt_batch", "estimate"]
].rename(columns={"estimate": "slope_log2"})
pec50 = pec50.merge(slope, on="ocnt_batch", how="left")

emax = curves[curves["term"] == "EmaxLog2FC"][
    ["ocnt_batch", "estimate"]
].rename(columns={"estimate": "emax_log2fc"})
pec50 = pec50.merge(emax, on="ocnt_batch", how="left")

# merge QC flags (following Scott's CDD upload approach)
qc_combined = qcflags.merge(qc_plate, how="outer")
qc_combined["plate_qc_status"] = qc_combined["pass"].map({True: "PASS", False: "FAIL"})
qc_combined = qc_combined.drop(columns=["pass"])
qc_combined = qc_combined.rename(columns={
    "status": "drc_qc_status",
    "qc_flag": "drc_qc_flag",
})

qc_cols = [
    "ocnt_batch", "activity_status", "rollover_status", "saturation_status",
    "direction", "drc_qc_status", "drc_qc_flag", "qc_flag_primary",
    "plate_qc_status",
]
pec50 = pec50.merge(qc_combined[qc_cols], on="ocnt_batch", how="left")

# NA out pIC50 values for failed QC (DRC or plate level)
bad_rows = (pec50["drc_qc_status"] == "FAIL") | (pec50["plate_qc_status"] == "FAIL")
pec50.loc[bad_rows, ["CYP3A4_pIC50", "CYP3A4_pIC50_se",
                      "CYP3A4_pIC50_ci_lower", "CYP3A4_pIC50_ci_upper"]] = pd.NA

# remove positive control and non-library compounds
pec50 = pec50[pec50["compound_class"] == "Library"]
pec50 = pec50[~pec50["ocnt_batch"].str.startswith(POSITIVE_CONTROL)]

inhibition = pec50[[
    "ocnt_batch", "CYP3A4_pIC50", "CYP3A4_pIC50_se",
    "CYP3A4_pIC50_ci_lower", "CYP3A4_pIC50_ci_upper",
    "slope_log2", "emax_log2fc",
    "activity_status", "rollover_status", "saturation_status",
    "direction", "drc_qc_status", "drc_qc_flag", "qc_flag_primary",
    "plate_qc_status",
]].copy()
inhibition = inhibition.sort_values("CYP3A4_pIC50", ascending=False, na_position="last")
inhibition.to_csv(OUT / "inhibition.tsv", sep="\t", index=False)
print(
    f"inhibition.tsv  : {len(inhibition):,} rows, "
    f"{inhibition['ocnt_batch'].nunique()} compounds  "
    f"({inhibition['CYP3A4_pIC50'].notna().sum()} with pIC50, "
    f"{bad_rows.sum()} QC-failed)"
)

# ---- Well-level fluorescence data ----

stats = pd.read_csv(BytesIO(stats_bytes), sep="\t")
outliers = pd.read_csv(BytesIO(outliers_bytes), sep="\t")

# outlier wells are excluded from stats.tsv — concatenate them back in
stats["outlier"] = False
outlier_rows = outliers[["plate", "row", "col", "molecule_name", "batch_name",
                          "chem_id", "chem_m"]].copy()
outlier_rows["outlier"] = True
# outlier rows don't have luci/luci_norm/compound_class — fill with NA
for col in ["luci", "luci_norm", "compound_class"]:
    outlier_rows[col] = pd.NA
well_all = pd.concat([stats, outlier_rows], ignore_index=True)

# build ocnt_batch and select columns
well_all["ocnt_batch"] = well_all["molecule_name"] + "-" + well_all["batch_name"]
well_data = well_all[[
    "ocnt_batch", "compound_class", "plate", "row", "col",
    "chem_m", "luci", "luci_norm", "outlier",
]].copy()
well_data = well_data.rename(columns={
    "chem_m": "concentration_M",
    "luci": "fluorescence",
    "luci_norm": "fluorescence_norm",
})
well_data = well_data.sort_values("outlier", ascending=True)
well_data.to_csv(OUT / "inhibition_wells.tsv", sep="\t", index=False)
n_outliers = well_data["outlier"].sum()
print(
    f"inhibition_wells: {len(well_data):,} rows, "
    f"{well_data['ocnt_batch'].nunique()} compounds  "
    f"({n_outliers} outlier wells flagged, {len(stats):,} kept)"
)

