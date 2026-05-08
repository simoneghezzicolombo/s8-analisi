const COLORS = {
  teal: "#177a74",
  tealStrong: "#11655f",
  grid: "#d7e7e5",
  text: "#17313a",
  muted: "#60777d",
  s8: "#df6f91",
  s8Soft: "#f2b8c1",
  grey: "#a8b6b8",
  s1: "#e84b5f",
  s5: "#f39a3d",
  s6: "#d9c62c",
  s9: "#a63ca5",
  meratese: {
    "Airuno": "#c9a52b",
    "Osnago": "#d64fd8",
    "Cernusco-Merate": "#28b9c7",
    "Olgiate-Calco-Brivio": "#ef6bb8"
  }
};

const DATASETS = {
  linee: "data/processed/linee_s_indice_2019_2025.csv",
  delta: "data/processed/variazione_linee_suburbane_2024_2025.csv",
  top20: "data/processed/top20_linee_locali_italia.csv",
  metro: "data/processed/benchmark_metropolitane_s8.csv",
  stazioni: "data/processed/stazioni_s8_indice_2015_2025.csv",
  scatter: "data/processed/scatter_stazioni_lombarde_2019_2025.csv",
  punta: "data/processed/peso_punta_stazioni_s8_2015_2025.csv",
  morbida: "data/processed/crescita_meratese_punta_morbida_2015_2025.csv"
};

const plotConfig = {
  responsive: true,
  displaylogo: false,
  modeBarButtonsToRemove: ["lasso2d", "select2d"]
};

const baseLayout = {
  paper_bgcolor: "#ffffff",
  plot_bgcolor: "#ffffff",
  font: { family: "Aptos, Segoe UI, Arial, sans-serif", color: COLORS.text, size: 13 },
  margin: { l: 58, r: 28, t: 30, b: 58 },
  hoverlabel: {
    bgcolor: "#ffffff",
    bordercolor: COLORS.grid,
    font: { color: COLORS.text }
  },
  legend: {
    orientation: "h",
    y: -0.18,
    x: 0,
    font: { size: 12 }
  },
  xaxis: {
    gridcolor: COLORS.grid,
    zerolinecolor: COLORS.grid,
    tickfont: { color: COLORS.muted }
  },
  yaxis: {
    gridcolor: COLORS.grid,
    zerolinecolor: COLORS.grid,
    tickfont: { color: COLORS.muted }
  }
};

function parseCSV(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const c = text[i];
    const next = text[i + 1];
    if (inQuotes) {
      if (c === "\"" && next === "\"") {
        field += "\"";
        i += 1;
      } else if (c === "\"") {
        inQuotes = false;
      } else {
        field += c;
      }
    } else if (c === "\"") {
      inQuotes = true;
    } else if (c === ",") {
      row.push(field);
      field = "";
    } else if (c === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (c !== "\r") {
      field += c;
    }
  }
  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  const header = rows.shift();
  return rows
    .filter((r) => r.some((v) => v !== ""))
    .map((r) => Object.fromEntries(header.map((h, i) => [h, coerce(r[i] ?? "")])));
}

function coerce(value) {
  const trimmed = String(value).trim();
  if (trimmed === "") return null;
  const normalized = trimmed.replace(",", ".");
  if (/^-?\d+(\.\d+)?$/.test(normalized)) return Number(normalized);
  if (trimmed === "True") return true;
  if (trimmed === "False") return false;
  return trimmed;
}

async function loadCSV(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Impossibile caricare ${path}`);
  return parseCSV(await response.text());
}

function grouped(rows, key) {
  return rows.reduce((acc, row) => {
    const value = row[key];
    if (!acc[value]) acc[value] = [];
    acc[value].push(row);
    return acc;
  }, {});
}

function fmt(value, digits = 0) {
  return Number(value).toLocaleString("it-IT", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  });
}

function mergeLayout(layout) {
  return {
    ...baseLayout,
    ...layout,
    xaxis: { ...baseLayout.xaxis, ...(layout.xaxis || {}) },
    yaxis: { ...baseLayout.yaxis, ...(layout.yaxis || {}) },
    legend: { ...baseLayout.legend, ...(layout.legend || {}) },
    margin: { ...baseLayout.margin, ...(layout.margin || {}) }
  };
}

function render(id, traces, layout) {
  const frame = document.querySelector(`#${id}`).closest(".plot-frame");
  return Plotly.newPlot(id, traces, mergeLayout(layout), plotConfig).then(() => {
    frame.classList.add("ready");
  });
}

function lineColor(name) {
  if (name === "S8") return COLORS.s8;
  if (name === "S1/S12") return COLORS.s1;
  if (name === "S5") return COLORS.s5;
  if (name === "S6") return COLORS.s6;
  if (name === "Totale Trenord") return COLORS.muted;
  return COLORS.grey;
}

async function chartLinee() {
  const rows = await loadCSV(DATASETS.linee);
  const order = ["S8", "S1/S12", "S5", "S6", "Totale Trenord"];
  const bySerie = grouped(rows, "Serie");
  const traces = order.map((serie) => {
    const sub = [...(bySerie[serie] || [])].sort((a, b) => a.Anno - b.Anno);
    return {
      type: "scatter",
      mode: "lines+markers",
      name: serie,
      x: sub.map((d) => d.Anno),
      y: sub.map((d) => d.Indice_2019_100),
      line: { color: lineColor(serie), width: serie === "S8" ? 4 : 2.7, dash: serie === "Totale Trenord" ? "dot" : "solid" },
      marker: { size: serie === "S8" ? 8 : 6 },
      customdata: sub.map((d) => [d.Valore, d.Unita, d.Tipo_dato]),
      hovertemplate: `<b>${serie}</b><br>Anno %{x}<br>Indice: %{y:.1f}<br>Valore: %{customdata[0]:,.0f}<br>%{customdata[1]}<br><extra>%{customdata[2]}</extra>`
    };
  });
  return render("plot-linee", traces, {
    title: { text: "Linee suburbane Trenord, indice 2019=100", x: 0, font: { size: 18 } },
    yaxis: { title: "Indice 2019=100", range: [0, 170] },
    xaxis: { title: "Anno", dtick: 1 }
  });
}

async function chartDelta() {
  const rows = (await loadCSV(DATASETS.delta)).sort((a, b) => a.Delta - b.Delta);
  const names = rows.map((d) => d["N. linea"]);
  const colors = names.map((name) => ({
    "S8": COLORS.s8,
    "S1/S12": COLORS.s1,
    "S5": COLORS.s5,
    "S6": COLORS.s6,
    "S9": COLORS.s9
  }[name] || COLORS.grey));
  return render("plot-delta", [{
    type: "bar",
    orientation: "h",
    x: rows.map((d) => d.Delta),
    y: names,
    marker: { color: colors, opacity: names.map((n) => n === "S8" ? 1 : 0.78) },
    customdata: rows.map((d) => [d["2024"], d["2025"], d.Delta_pct]),
    hovertemplate: "<b>%{y}</b><br>2024: %{customdata[0]:,.0f}<br>2025: %{customdata[1]:,.0f}<br>Delta: %{x:+,.0f}<br>Delta %: %{customdata[2]:+.1f}%<extra></extra>"
  }], {
    title: { text: "Variazione assoluta 2025-2024", x: 0, font: { size: 18 } },
    xaxis: { title: "Passeggeri/giorno feriale, somma campagne comparabili", zeroline: true },
    yaxis: { title: "" },
    showlegend: false,
    annotations: [{
      x: 15400,
      y: "S1/S12",
      text: "da 70 a 130 corse/giorno<br>grazie alla S12",
      showarrow: false,
      align: "left",
      xanchor: "left",
      yanchor: "middle",
      font: { size: 12, color: COLORS.text },
      bgcolor: "#ffffff",
      bordercolor: COLORS.grid,
      borderpad: 8,
      borderwidth: 1
    }]
  });
}

async function chartTop20() {
  const rows = (await loadCSV(DATASETS.top20)).sort((a, b) => b.rank - a.rank);
  return render("plot-top20", [{
    type: "bar",
    orientation: "h",
    x: rows.map((d) => d.central_mln),
    y: rows.map((d) => `${d.rank}. ${d.line_code}`),
    marker: { color: rows.map((d) => d.line_code === "S8" ? COLORS.s8 : "#b7c5c7") },
    customdata: rows.map((d) => [d.line_name, d.operator, d.data_year, d.method]),
    hovertemplate: "<b>%{customdata[0]}</b><br>Operatore: %{customdata[1]}<br>Passeggeri annui: %{x:.1f} mln<br>Anno/metodo: %{customdata[2]}<br><extra>%{customdata[3]}</extra>"
  }], {
    title: { text: "Passeggeri annui per linea", x: 0, font: { size: 18 } },
    xaxis: { title: "Milioni di passeggeri annui" },
    yaxis: { title: "", automargin: true },
    showlegend: false,
    margin: { l: 92, r: 26, t: 42, b: 62 }
  });
}

async function chartMetro() {
  const rows = await loadCSV(DATASETS.metro);
  rows.sort((a, b) => a.passeggeri_annui - b.passeggeri_annui);
  return render("plot-metro", [{
    type: "bar",
    orientation: "h",
    x: rows.map((d) => d.passeggeri_annui / 1_000_000),
    y: rows.map((d) => d.servizio),
    marker: { color: rows.map((d) => d.servizio.includes("S8") ? COLORS.s8 : "#b7c5c7") },
    customdata: rows.map((d) => [
      d.passeggeri_annui_label || `${(d.passeggeri_annui / 1_000_000).toLocaleString("it-IT", { maximumFractionDigits: 2 })} mln`,
      d.frequenza_box || d.freq_label,
      d.tipo_dato_passeggeri || "",
      d.note || ""
    ]),
    hovertemplate: "<b>%{y}</b><br>Passeggeri annui: %{customdata[0]}<br>Frequenza: %{customdata[1]}<br>Tipo dato: %{customdata[2]}<br><extra>%{customdata[3]}</extra>"
  }], {
    title: { text: "La S8 ha numeri da metropolitana", x: 0, font: { size: 18 } },
    xaxis: { title: "Milioni di passeggeri annui" },
    yaxis: { title: "", automargin: true },
    showlegend: false,
    margin: { l: 190, r: 26, t: 42, b: 62 }
  });
}

async function chartStazioni() {
  const rows = await loadCSV(DATASETS.stazioni);
  const byStation = grouped(rows.filter((d) => d.Stazione !== "Vercurago-S. Girolamo"), "Stazione");
  const traces = Object.entries(byStation).map(([station, values]) => {
    const sub = values.sort((a, b) => a.Anno - b.Anno);
    const isMer = Boolean(COLORS.meratese[station]);
    return {
      type: "scatter",
      mode: "lines+markers",
      name: station,
      x: sub.map((d) => d.Anno),
      y: sub.map((d) => d.Indice_2019_100),
      line: { color: isMer ? COLORS.meratese[station] : "#b7c5c7", width: isMer ? 3.6 : 1.4 },
      marker: { size: isMer ? 7 : 4 },
      opacity: isMer ? 1 : 0.45,
      customdata: sub.map((d) => [d.Saliti24H, d.Fonte_periodo]),
      hovertemplate: `<b>${station}</b><br>Anno %{x}<br>Indice: %{y:.1f}<br>Saliti24H: %{customdata[0]:,.0f}<br><extra>%{customdata[1]}</extra>`
    };
  });
  return render("plot-stazioni", traces, {
    title: { text: "Passeggeri nelle stazioni S8, base 2019=100", x: 0, font: { size: 18 } },
    yaxis: { title: "Indice 2019=100" },
    xaxis: { title: "Anno", dtick: 2 },
    legend: { orientation: "h", y: -0.25, x: 0 }
  });
}

async function chartScatter() {
  const rows = await loadCSV(DATASETS.scatter);
  const others = rows.filter((d) => !d.IsMeratese);
  const mer = rows.filter((d) => d.IsMeratese);
  const traces = [{
    type: "scatter",
    mode: "markers",
    name: "Altre stazioni lombarde",
    x: others.map((d) => d.Growth_pct_Saliti24H),
    y: others.map((d) => d.Growth_pct_Saliti_per_corsa),
    text: others.map((d) => d.Label),
    marker: {
      size: others.map((d) => Math.max(7, Math.min(28, Math.sqrt(Math.max(d.Delta_abs_Saliti24H, 1)) / 1.7))),
      color: "rgba(120,135,140,0.35)",
      line: { width: 0 }
    },
    customdata: others.map((d) => [d.Delta_abs_Saliti24H, d.Corse24H_2019, d.Corse24H_2025]),
    hovertemplate: "<b>%{text}</b><br>Crescita passeggeri: %{x:.1f}%<br>Cambio passeggeri/corsa: %{y:.1f}%<br>Delta saliti24H: %{customdata[0]:+,.0f}<br>Corse 2019→2025: %{customdata[1]:.0f}→%{customdata[2]:.0f}<extra></extra>"
  }];
  traces.push({
    type: "scatter",
    mode: "markers+text",
    name: "Stazioni meratesi",
    x: mer.map((d) => d.Growth_pct_Saliti24H),
    y: mer.map((d) => d.Growth_pct_Saliti_per_corsa),
    text: mer.map((d) => d.Label),
    textposition: ["top right", "top right", "bottom right", "bottom right"],
    marker: {
      size: 17,
      color: mer.map((d) => COLORS.meratese[d.Label] || COLORS.s8),
      line: { color: "#ffffff", width: 1.5 }
    },
    customdata: mer.map((d) => [d.Delta_abs_Saliti24H, d.Corse24H_2019, d.Corse24H_2025]),
    hovertemplate: "<b>%{text}</b><br>Crescita passeggeri: %{x:.1f}%<br>Cambio passeggeri/corsa: %{y:.1f}%<br>Delta saliti24H: %{customdata[0]:+,.0f}<br>Corse 2019→2025: %{customdata[1]:.0f}→%{customdata[2]:.0f}<extra></extra>"
  });
  return render("plot-scatter", traces, {
    title: { text: "Crescita passeggeri nelle stazioni lombarde", x: 0, font: { size: 18 } },
    xaxis: { title: "Crescita % passeggeri 2019-2025", zeroline: true },
    yaxis: { title: "Cambiamento % passeggeri per corsa", zeroline: true },
    shapes: [
      { type: "line", x0: 0, x1: 0, y0: -80, y1: 150, line: { color: "#9fb1b4", width: 1, dash: "dot" } },
      { type: "line", x0: -80, x1: 170, y0: 0, y1: 0, line: { color: "#9fb1b4", width: 1, dash: "dot" } }
    ],
    legend: { orientation: "h", y: -0.2, x: 0 }
  });
}

async function chartPunta() {
  const rows = await loadCSV(DATASETS.punta);
  const byStation = grouped(rows, "Stazione");
  const traces = Object.entries(byStation).map(([station, values]) => {
    const sub = values.sort((a, b) => a.Anno - b.Anno);
    const isMer = Boolean(COLORS.meratese[station]);
    return {
      type: "scatter",
      mode: "lines+markers",
      name: station,
      x: sub.map((d) => d.Anno),
      y: sub.map((d) => d.Peso_punta_pct),
      line: { color: isMer ? COLORS.meratese[station] : "#b7c5c7", width: isMer ? 3.6 : 1.3 },
      marker: { size: isMer ? 7 : 4 },
      opacity: isMer ? 1 : 0.42,
      customdata: sub.map((d) => [d["Saliti7-9"], d.Saliti24H]),
      hovertemplate: `<b>${station}</b><br>Anno %{x}<br>Peso punta: %{y:.1f}%<br>Saliti 7-9: %{customdata[0]:,.0f}<br>Saliti24H: %{customdata[1]:,.0f}<extra></extra>`
    };
  });
  return render("plot-punta", traces, {
    title: { text: "Peso della punta mattutina nelle stazioni S8", x: 0, font: { size: 18 } },
    yaxis: { title: "Saliti 7-9 / saliti24H (%)", range: [0, 65] },
    xaxis: { title: "Anno", dtick: 2 },
    legend: { orientation: "h", y: -0.25, x: 0 }
  });
}

async function chartMorbida() {
  const rows = await loadCSV(DATASETS.morbida);
  const wanted = ["Airuno", "Osnago", "Cernusco-Merate", "Olgiate-Calco-Brivio"];
  const byStation = grouped(rows.filter((d) => wanted.includes(d.Stazione) && (d.Anno === 2019 || d.Anno === 2025)), "Stazione");
  const computed = wanted.map((station) => {
    const sub = byStation[station] || [];
    const start = sub.find((d) => d.Anno === 2019);
    const end = sub.find((d) => d.Anno === 2025);
    const deltaTot = end.Saliti24H - start.Saliti24H;
    const deltaPunta = end["Saliti7-9"] - start["Saliti7-9"];
    return { station, punta: deltaPunta, morbida: deltaTot - deltaPunta, totale: deltaTot };
  });
  const total = computed.reduce((acc, row) => ({
    station: "Meratese totale",
    punta: acc.punta + row.punta,
    morbida: acc.morbida + row.morbida,
    totale: acc.totale + row.totale
  }), { punta: 0, morbida: 0, totale: 0 });
  const rowsPlot = [total, ...computed].reverse();
  const y = rowsPlot.map((d) => d.station);
  return render("plot-morbida", [
    {
      type: "bar",
      orientation: "h",
      name: "Punta 7-9",
      x: rowsPlot.map((d) => d.punta),
      y,
      marker: { color: "#8e3d7a" },
      customdata: rowsPlot.map((d) => d.totale),
      hovertemplate: "<b>%{y}</b><br>Crescita in punta: %{x:+,.0f}<br>Crescita totale: %{customdata:+,.0f}<extra></extra>"
    },
    {
      type: "bar",
      orientation: "h",
      name: "Fuori 7-9",
      x: rowsPlot.map((d) => d.morbida),
      y,
      marker: { color: COLORS.s8Soft },
      customdata: rowsPlot.map((d) => [d.totale, d.morbida / d.totale * 100]),
      hovertemplate: "<b>%{y}</b><br>Crescita fuori 7-9: %{x:+,.0f}<br>Quota fuori punta: %{customdata[1]:.1f}%<br>Crescita totale: %{customdata[0]:+,.0f}<extra></extra>"
    }
  ], {
    title: { text: "Crescita meratese: punta e resto della giornata", x: 0, font: { size: 18 } },
    barmode: "stack",
    xaxis: { title: "Saliti/giorno, variazione 2025-2019" },
    yaxis: { title: "" },
    legend: { orientation: "h", y: -0.18, x: 0 }
  });
}

function init() {
  Promise.all([
    chartLinee(),
    chartDelta(),
    chartTop20(),
    chartMetro(),
    chartStazioni(),
    chartScatter(),
    chartPunta(),
    chartMorbida()
  ]).catch((error) => {
    console.error(error);
    document.querySelectorAll(".plot-status").forEach((el) => {
      el.textContent = "Errore nel caricamento del grafico. Controllare i file CSV.";
    });
  });
}

window.addEventListener("DOMContentLoaded", init);
