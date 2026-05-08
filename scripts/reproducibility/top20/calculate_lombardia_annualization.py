"""
Rigenera l'annualizzazione Lombardia/Trenord 2025 usata per le righe L25 della Top 20.

Input:
- data/raw/regione_lombardia_frequentazione_linee_sfr_20260424.csv
- data/reproducibility/top20/top20_lines.csv

Output:
- data/reproducibility/top20/lombardia_2025_weights.csv
- data/reproducibility/top20/lombardia_2025_holidays.csv
- data/reproducibility/top20/s8_14_8063_calculation_detail.csv
- data/reproducibility/top20/lombardia_2025_line_contributions_top20.csv
- data/reproducibility/top20/lombardia_2025_annualized_top20_lines.csv
- data/reproducibility/top20/lombardia_2025_line_contributions_all_lines.csv
- data/reproducibility/top20/lombardia_2025_annualized_all_lines.csv
"""
from pathlib import Path
import pandas as pd
import calendar
import datetime

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "reproducibility" / "top20"
RAW = ROOT / "data" / "raw"

raw = pd.read_csv(RAW / "regione_lombardia_frequentazione_linee_sfr_20260424.csv")
top = pd.read_csv(DATA / "top20_lines.csv")

period_months = {
    "ordinario_novembre_proxy": [1, 2, 3, 4, 10, 11, 12],
    "spalla_maggio_proxy": [5, 6, 9],
    "estate_luglio_proxy": [7, 8],
}
period_campaign = {
    "ordinario_novembre_proxy": "c2025Novembre",
    "spalla_maggio_proxy": "c2025Maggio",
    "estate_luglio_proxy": "c2025Luglio",
}
period_labels = {
    "ordinario_novembre_proxy": "Ordinario (proxy novembre)",
    "spalla_maggio_proxy": "Spalla/inizio estate (proxy maggio)",
    "estate_luglio_proxy": "Estate/vacanza (proxy luglio)",
}
holidays = {
    datetime.date(2025, 1, 1): "Capodanno",
    datetime.date(2025, 1, 6): "Epifania",
    datetime.date(2025, 4, 20): "Pasqua",
    datetime.date(2025, 4, 21): "Lunedì dell’Angelo",
    datetime.date(2025, 4, 25): "Liberazione",
    datetime.date(2025, 5, 1): "Festa del lavoro",
    datetime.date(2025, 6, 2): "Festa della Repubblica",
    datetime.date(2025, 8, 15): "Ferragosto",
    datetime.date(2025, 11, 1): "Ognissanti",
    datetime.date(2025, 12, 8): "Immacolata",
    datetime.date(2025, 12, 25): "Natale",
    datetime.date(2025, 12, 26): "Santo Stefano",
}

def build_weights():
    rows = []
    for period, months in period_months.items():
        counts = {"Feriale": 0, "Sabato": 0, "Festivo": 0}
        for month in months:
            for day in range(1, calendar.monthrange(2025, month)[1] + 1):
                date = datetime.date(2025, month, day)
                weekday = date.weekday()
                if date in holidays:
                    tipo = "Festivo"
                elif weekday < 5:
                    tipo = "Feriale"
                elif weekday == 5:
                    tipo = "Sabato"
                else:
                    tipo = "Festivo"
                counts[tipo] += 1
        for tipo in ["Feriale", "Sabato", "Festivo"]:
            rows.append({
                "period_id": period,
                "period_label": period_labels[period],
                "proxy_campaign": period_campaign[period],
                "months_covered": ",".join(str(m).zfill(2) for m in months),
                "tipo_giorno": tipo,
                "days_weight": counts[tipo],
                "calendar_basis": "Calendario 2025; festività nazionali italiane trattate come Festivo",
            })
    return pd.DataFrame(rows)

weights = build_weights()
weights.to_csv(DATA / "lombardia_2025_weights.csv", index=False)
pd.DataFrame([
    {"date": d.isoformat(), "name": name, "weekday": d.strftime("%A")}
    for d, name in holidays.items()
]).to_csv(DATA / "lombardia_2025_holidays.csv", index=False)

def calc_for_line(code):
    sub = raw[raw["N. linea"].astype(str).eq(str(code))]
    rows = []
    for _, w in weights.iterrows():
        match = sub[(sub["Campagna"] == w["proxy_campaign"]) & (sub["Tipo giorno"] == w["tipo_giorno"])]
        if match.empty:
            continue
        val = float(match["Viaggiatori"].iloc[0])
        days = int(w["days_weight"])
        rows.append({
            "line_code": code,
            "line_name_raw": match["Linea"].iloc[0],
            "period_id": w["period_id"],
            "period_label": w["period_label"],
            "proxy_campaign": w["proxy_campaign"],
            "tipo_giorno": w["tipo_giorno"],
            "daily_travellers_thousand": val,
            "days_weight": days,
            "annual_contribution_mln": val * days / 1000,
            "formula": "daily_travellers_thousand × days_weight / 1000",
        })
    return rows

l25_lines = top[top["status"].eq("L25")]["line_code"].tolist()
contrib = []
for code in l25_lines:
    contrib.extend(calc_for_line(code))
contrib = pd.DataFrame(contrib)
contrib.to_csv(DATA / "lombardia_2025_line_contributions_top20.csv", index=False)
annual = contrib.groupby(["line_code", "line_name_raw"], dropna=False).agg(
    annual_mln=("annual_contribution_mln", "sum"),
    input_cells=("annual_contribution_mln", "count"),
).reset_index()
annual = annual.merge(top[["line_code", "line_name", "central_mln", "rank"]], on="line_code", how="left")
annual["check_vs_top20_mln"] = annual["annual_mln"] - annual["central_mln"]
annual.sort_values("annual_mln", ascending=False).to_csv(DATA / "lombardia_2025_annualized_top20_lines.csv", index=False)

s8 = contrib[contrib["line_code"].eq("S8")].copy()
s8_total_mln = float(s8["annual_contribution_mln"].sum())
s8_total_days = int(s8["days_weight"].sum())
s8_out = s8.copy()
s8_out["daily_travellers_thousand"] = s8_out["daily_travellers_thousand"].astype(object)
s8_out.loc[len(s8_out)] = {
    "line_code": "S8",
    "line_name_raw": "TOTALE",
    "period_id": "",
    "period_label": "",
    "proxy_campaign": "",
    "tipo_giorno": "",
    "daily_travellers_thousand": "",
    "days_weight": s8_total_days,
    "annual_contribution_mln": s8_total_mln,
    "formula": "somma contributi",
}
s8_out.to_csv(DATA / "s8_14_8063_calculation_detail.csv", index=False)

all_codes = sorted(raw[raw["Campagna"].str.startswith("c2025", na=False)]["N. linea"].astype(str).unique())
all_contrib = []
for code in all_codes:
    rows = calc_for_line(code)
    if len(rows) == 9:
        all_contrib.extend(rows)
all_contrib = pd.DataFrame(all_contrib)
all_contrib.to_csv(DATA / "lombardia_2025_line_contributions_all_lines.csv", index=False)
pivot = all_contrib.pivot_table(index=["line_code", "line_name_raw"], columns="period_id", values="annual_contribution_mln", aggfunc="sum").reset_index()
value_cols = [c for c in pivot.columns if c not in ["line_code", "line_name_raw"]]
pivot["annual_mln"] = pivot[value_cols].sum(axis=1)
pivot.sort_values("annual_mln", ascending=False).to_csv(DATA / "lombardia_2025_annualized_all_lines.csv", index=False)

print("S8 annualizzata:", round(s8_total_mln, 4))
print("Pesi totali:", int(weights["days_weight"].sum()))
