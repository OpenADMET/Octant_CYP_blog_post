"""
Pull standardized SMILES from Databricks and update local data files.

Reads batch IDs from all data files that contain an ocnt_batch column,
queries octant.chem_ml.standardized_batch_smiles for canonical SMILES,
and overwrites the SMILES columns in each file.

Usage:
    uv run python scripts/update_smiles.py
"""

import configparser
import os
from pathlib import Path

import pandas as pd
from databricks import sql

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# --- connect to Databricks ---

cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser("~/.databrickscfg"))
host = cfg["DEFAULT"]["host"].replace("https://", "")
token = cfg["DEFAULT"]["token"]

conn = sql.connect(
    server_hostname=host,
    http_path="/sql/1.0/warehouses/18eff2791deb3c1d",
    access_token=token,
)

# --- collect all unique batch IDs ---

inhibition = pd.read_csv(DATA_DIR / "inhibition.tsv", sep="\t")
inhibition_wells = pd.read_csv(DATA_DIR / "inhibition_wells.tsv", sep="\t")
reactivity = pd.read_csv(DATA_DIR / "reactivity.tsv", sep="\t")
willitfly = pd.read_csv(DATA_DIR / "willitfly.tsv", sep="\t")
clearance = pd.read_csv(DATA_DIR / "clearance_snippet.tsv", sep="\t")

all_batches = set(
    inhibition["ocnt_batch"].dropna().unique().tolist()
    + inhibition_wells["ocnt_batch"].dropna().unique().tolist()
    + reactivity["ocnt_batch"].dropna().unique().tolist()
    + willitfly["ocnt_batch"].dropna().unique().tolist()
    + clearance["ocnt_batch"].dropna().unique().tolist()
)
print(f"Total unique batches across all files: {len(all_batches)}")

# --- query in chunks (Databricks has a limit on IN clause size) ---

batch_list = sorted(all_batches)
chunk_size = 500
smiles_rows = []

cursor = conn.cursor()
for i in range(0, len(batch_list), chunk_size):
    chunk = batch_list[i : i + chunk_size]
    placeholders = ",".join(f"'{b}'" for b in chunk)
    cursor.execute(f"""
        SELECT batch, standardized_smiles
        FROM octant.chem_ml.standardized_batch_smiles
        WHERE batch IN ({placeholders})
    """)
    smiles_rows.extend(cursor.fetchall())
    print(f"  Fetched {len(smiles_rows)} rows so far...")

cursor.close()
conn.close()

smiles_lookup = pd.DataFrame(smiles_rows, columns=["ocnt_batch", "standardized_smiles"])
smiles_lookup = smiles_lookup.drop_duplicates(subset="ocnt_batch")
print(f"Got SMILES for {len(smiles_lookup)} batches")

# --- update inhibition.tsv ---

smiles_col_inh = next(
    (c for c in ("smiles", "standardized_smiles") if c in inhibition.columns), None
)
if smiles_col_inh:
    n_before = inhibition[smiles_col_inh].notna().sum()
    inhibition = inhibition.drop(columns=[smiles_col_inh])
else:
    n_before = 0
inhibition = inhibition.merge(
    smiles_lookup,
    on="ocnt_batch",
    how="left",
)
n_after = inhibition["standardized_smiles"].notna().sum()
n_missing = inhibition["standardized_smiles"].isna().sum()
inhibition.to_csv(DATA_DIR / "inhibition.tsv", sep="\t", index=False)
print(f"inhibition.tsv: {n_before} → {n_after} with SMILES ({n_missing} missing)")

# --- update reactivity.tsv ---

smiles_col = "cxsmiles" if "cxsmiles" in reactivity.columns else "standardized_smiles"
n_before = reactivity[smiles_col].notna().sum()
reactivity = reactivity.drop(columns=[smiles_col]).merge(
    smiles_lookup,
    on="ocnt_batch",
    how="left",
)
n_after = reactivity["standardized_smiles"].notna().sum()
n_missing = reactivity["standardized_smiles"].isna().sum()
reactivity.to_csv(DATA_DIR / "reactivity.tsv", sep="\t", index=False)
print(f"reactivity.tsv: {n_before} → {n_after} with SMILES ({n_missing} missing)")

# --- update willitfly.tsv ---

if "standardized_smiles" in willitfly.columns:
    willitfly = willitfly.drop(columns=["standardized_smiles"])
willitfly = willitfly.merge(smiles_lookup, on="ocnt_batch", how="left")
n_with = willitfly["standardized_smiles"].notna().sum()
n_missing = willitfly["standardized_smiles"].isna().sum()
willitfly.to_csv(DATA_DIR / "willitfly.tsv", sep="\t", index=False)
print(f"willitfly.tsv: {n_with} with SMILES ({n_missing} missing)")

# --- update inhibition_wells.tsv ---

if "standardized_smiles" in inhibition_wells.columns:
    inhibition_wells = inhibition_wells.drop(columns=["standardized_smiles"])
inhibition_wells = inhibition_wells.merge(smiles_lookup, on="ocnt_batch", how="left")
n_with = inhibition_wells["standardized_smiles"].notna().sum()
n_missing = inhibition_wells["standardized_smiles"].isna().sum()
inhibition_wells.to_csv(DATA_DIR / "inhibition_wells.tsv", sep="\t", index=False)
print(f"inhibition_wells.tsv: {n_with} with SMILES ({n_missing} missing)")

# --- update clearance_snippet.tsv ---

if "standardized_smiles" in clearance.columns:
    clearance = clearance.drop(columns=["standardized_smiles"])
clearance = clearance.merge(smiles_lookup, on="ocnt_batch", how="left")
n_with = clearance["standardized_smiles"].notna().sum()
n_missing = clearance["standardized_smiles"].isna().sum()
clearance.to_csv(DATA_DIR / "clearance_snippet.tsv", sep="\t", index=False)
print(f"clearance_snippet.tsv: {n_with} with SMILES ({n_missing} missing)")
