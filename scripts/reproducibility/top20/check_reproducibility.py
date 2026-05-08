from pathlib import Path
import pandas as pd
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "reproducibility" / "top20"
RAW = ROOT / "data" / "raw"
FIG = ROOT / "figures" / "reproducibility" / "top20"

required = [
    DATA / "top20_lines.csv",
    RAW / "regione_lombardia_frequentazione_linee_sfr_20260424.csv",
    DATA / "lombardia_2025_weights.csv",
    DATA / "s8_14_8063_calculation_detail.csv",
    DATA / "lombardia_2025_annualized_top20_lines.csv",
]
for p in required:
    if not p.exists():
        raise FileNotFoundError(p)

# Recalculate Lombardia annualization before checking.
subprocess.check_call([sys.executable, str(SCRIPT_DIR / "calculate_lombardia_annualization.py")])
subprocess.check_call([sys.executable, str(SCRIPT_DIR / "plot_static_bar_slide.py")])

top = pd.read_csv(DATA / "top20_lines.csv")
ann = pd.read_csv(DATA / "lombardia_2025_annualized_top20_lines.csv")
merged = ann.merge(top[["line_code", "central_mln", "status"]], on="line_code", suffixes=("_ann", "_top"))
merged = merged[merged["status"].eq("L25")].copy()
merged["diff"] = (merged["annual_mln"] - merged["central_mln_top"]).abs()
max_diff = float(merged["diff"].max())
if max_diff > 1e-6:
    print(merged[["line_code", "annual_mln", "central_mln_top", "diff"]])
    raise AssertionError(f"L25 mismatch: max diff {max_diff}")

s8 = pd.read_csv(DATA / "s8_14_8063_calculation_detail.csv")
s8_total = float(s8.loc[s8["line_name_raw"].eq("TOTALE"), "annual_contribution_mln"].iloc[0])
if abs(s8_total - 14.8063) > 1e-6:
    raise AssertionError(f"S8 expected 14.8063, got {s8_total}")

figs = [
    FIG / "s8_top20_static_bar_slide.png",
]
missing = [p for p in figs if not p.exists()]
if missing:
    raise FileNotFoundError(f"Missing figures: {missing}")

print("OK: reproducibility check passed")
print(f"S8 annualized = {s8_total:.4f} mln")
print(f"L25 max diff = {max_diff:.8f}")
