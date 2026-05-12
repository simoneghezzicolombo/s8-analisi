const COLORS = {
  teal: "#177a74",
  tealStrong: "#11655f",
  grid: "#d7e7e5",
  text: "#17313a",
  muted: "#60777d",
  s8: "#F8B1B0",
  s8Strong: "#A64F58",
  s8Soft: "#FDEAEA",
  grey: "#a8b6b8",
  meratese: {
    "Airuno": "#A64F58",
    "Osnago": "#C66B75",
    "Cernusco-Merate": "#E4878F",
    "Olgiate-Calco-Brivio": "#F3B8BA"
  }
};

const LINE_COLORS = {
  "S1": "#E40520",
  "S1/S12": "#E40520",
  "S2": "#00AA87",
  "S3": "#AA0130",
  "S4": "#7EC340",
  "S5": "#F79336",
  "S6": "#F3D018",
  "S7": "#EE007D",
  "S8": "#F8B1B0",
  "S9": "#9E3A98",
  "S11": "#9B8EC4",
  "S12": "#004728",
  "S13": "#89580C",
  "RE6": "#C73834",
  "RE80": "#268BCC",
  "Totale Trenord": "#222222"
};

const LOMBARDY_LINE_CODES = new Set(["S1", "S5", "S6", "S8", "S9", "S11", "S13", "RE6", "RE80"]);

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

const mobileHeights = {
  "plot-linee": 430,
  "plot-delta": 520,
  "plot-top20": 640,
  "plot-metro": 520,
  "plot-stazioni": 500,
  "plot-scatter": 540,
  "plot-punta": 500,
  "plot-morbida": 430
};

const baseLayout = {
  paper_bgcolor: "#ffffff",
  plot_bgcolor: "#ffffff",
  font: { family: "Aptos, Segoe UI, Arial, sans-serif", color: COLORS.text, size: 13 },
  margin: { l: 74, r: 92, t: 56, b: 62 },
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

function isMobile() {
  return window.matchMedia("(max-width: 720px)").matches;
}

function viewportConfig() {
  return {
    ...plotConfig,
    displayModeBar: isMobile() ? false : "hover"
  };
}

function responsiveLayout(id, layout) {
  if (!isMobile()) return layout;

  const marginById = {
    "plot-linee": { l: 62, r: 86, t: 58, b: 76 },
    "plot-delta": { l: 68, r: 22, t: 58, b: 76 },
    "plot-top20": { l: 82, r: 24, t: 58, b: 76 },
    "plot-metro": { l: 118, r: 92, t: 58, b: 76 },
    "plot-stazioni": { l: 62, r: 92, t: 58, b: 76 },
    "plot-punta": { l: 68, r: 96, t: 58, b: 76 },
    "plot-morbida": { l: 134, r: 100, t: 58, b: 76 },
    "plot-scatter": { l: 56, r: 18, t: 58, b: 78 }
  };

  return {
    ...layout,
    height: mobileHeights[id] || 440,
    font: { ...baseLayout.font, size: 11 },
    title: {
      ...(layout.title || {}),
      font: { ...((layout.title || {}).font || {}), size: 15 }
    },
    margin: { l: 54, r: 14, t: 56, b: 76, ...(marginById[id] || {}) },
    legend: {
      ...(layout.legend || {}),
      orientation: "h",
      x: 0,
      y: -0.28,
      font: { size: 10 }
    },
    xaxis: {
      ...(layout.xaxis || {}),
      title: { text: (layout.xaxis || {}).title || "", font: { size: 11 } },
      tickfont: { size: 10 },
      automargin: true
    },
    yaxis: {
      ...(layout.yaxis || {}),
      title: { text: (layout.yaxis || {}).title || "", font: { size: 11 } },
      tickfont: { size: 10 },
      automargin: true
    }
  };
}

function render(id, traces, layout) {
  const frame = document.querySelector(`#${id}`).closest(".plot-frame");
  return Plotly.newPlot(id, traces, mergeLayout(responsiveLayout(id, layout)), viewportConfig()).then(() => {
    frame.classList.add("ready");
  });
}

function lineColor(name) {
  return LINE_COLORS[name] || COLORS.grey;
}

function endLabelAnnotations(items, options = {}) {
  const minGap = options.minGap ?? 5;
  const sorted = [...items].sort((a, b) => a.y - b.y);
  let previous = -Infinity;
  return sorted.map((item) => {
    const adjustedY = Math.max(item.y, previous + minGap);
    previous = adjustedY;
    return {
      x: options.x ?? item.x,
      y: adjustedY,
      text: item.text,
      showarrow: false,
      xanchor: "left",
      yanchor: "middle",
      align: "left",
      font: { size: options.fontSize ?? 12, color: item.color || COLORS.text },
      bgcolor: options.bgcolor ?? "rgba(255,255,255,0.88)",
      bordercolor: item.color || COLORS.grid,
      borderwidth: options.borderWidth ?? 0.8,
      borderpad: options.borderpad ?? 3
    };
  });
}

function shortMetroLabel(service) {
  if (!isMobile()) return service;
  return service
    .replace("Trenord S8 Lecco-Milano", "S8 Lecco-Milano")
    .replace("Brescia Metro 1", "Brescia M1")
    .replace("Roma Metro C", "Roma C")
    .replace("Genova Metro 1", "Genova M1")
    .replace("Catania Metro 1", "Catania M1")
    .replace("Napoli Linea 11 / Arcobaleno", "Napoli L11")
    .replace("Napoli Linea 6", "Napoli L6");
}

function shortStationLabel(station) {
  if (!isMobile()) return station;
  return station
    .replace("Cernusco-Merate", "Cernusco")
    .replace("Olgiate-Calco-Brivio", "Olgiate")
    .replace("Calolziocorte-Olginate", "Calolziocorte")
    .replace("Milano Porta Garibaldi", "M. Garibaldi")
    .replace("Milano Greco Pirelli", "M. Greco");
}

async function chartLinee() {
  const rows = await loadCSV(DATASETS.linee);
  const order = ["S8", "S1/S12", "S5", "S6", "Totale Trenord"];
  const bySerie = grouped(rows, "Serie");
  const endLabels = [];
  const traces = order.map((serie) => {
    const sub = [...(bySerie[serie] || [])].sort((a, b) => a.Anno - b.Anno);
    const color = LINE_COLORS[serie] || sub.find((d) => d.HEX)?.HEX || COLORS.grey;
    const last = sub[sub.length - 1];
    if (last) {
      endLabels.push({
        x: 2025.18,
        y: last.Indice_2019_100,
        text: `${serie} ${fmt(last.Indice_2019_100, 0)}`,
        color
      });
    }
    return {
      type: "scatter",
      mode: "lines+markers",
      name: serie,
      x: sub.map((d) => d.Anno),
      y: sub.map((d) => d.Indice_2019_100),
      line: { color, width: serie === "S8" ? 4.4 : 2.7, dash: serie === "Totale Trenord" ? "dot" : "solid" },
      marker: {
        size: serie === "S8" ? 8 : 6,
        color,
        line: { color: serie === "S8" ? COLORS.s8Strong : "#ffffff", width: serie === "S8" ? 1.4 : 0.5 }
      },
      customdata: sub.map((d) => [d.Valore, d.Unita, d.Tipo_dato]),
      hovertemplate: `<b>${serie}</b><br>Anno %{x}<br>Indice: %{y:.1f}<br>Passeggeri: %{customdata[0]:,.0f}<br>%{customdata[1]}<br><extra>%{customdata[2]}</extra>`
    };
  });
  return render("plot-linee", traces, {
    title: { text: "Linee suburbane Trenord, indice 2019=100", x: 0.02, font: { size: 18 } },
    yaxis: { title: "Indice 2019=100", range: [0, 170] },
    xaxis: { title: "Anno", dtick: 1, range: [2019, 2026.7] },
    margin: { l: 78, r: 138, t: 62, b: 62 },
    annotations: endLabelAnnotations(endLabels, { x: 2025.22, minGap: isMobile() ? 22 : 14, fontSize: isMobile() ? 10 : 12 })
  });
}

async function chartDelta() {
  const rows = (await loadCSV(DATASETS.delta)).sort((a, b) => a.Delta - b.Delta);
  const names = rows.map((d) => d["N. linea"]);
  const colors = names.map((name) => lineColor(name));
  return render("plot-delta", [{
    type: "bar",
    orientation: "h",
    x: rows.map((d) => d.Delta),
    y: names,
    marker: {
      color: colors,
      opacity: names.map((n) => n === "S8" ? 1 : 0.86),
      line: {
        color: names.map((n) => n === "S8" ? COLORS.s8Strong : "rgba(255,255,255,0.95)"),
        width: names.map((n) => n === "S8" ? 1.8 : 0.7)
      }
    },
    customdata: rows.map((d) => [d["2024"], d["2025"], d.Delta_pct]),
    hovertemplate: "<b>%{y}</b><br>2024: %{customdata[0]:,.0f}<br>2025: %{customdata[1]:,.0f}<br>Delta: %{x:+,.0f}<br>Delta %: %{customdata[2]:+.1f}%<extra></extra>"
  }], {
    title: { text: "Variazione assoluta 2025-2024", x: 0.02, font: { size: 18 } },
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
  const colors = rows.map((d) => {
    if (d.line_code === "S8") return d.color_hex || COLORS.s8;
    return "#c5d0d1";
  });
  return render("plot-top20", [{
    type: "bar",
    orientation: "h",
    x: rows.map((d) => d.central_mln),
    y: rows.map((d) => `${d.rank}. ${d.line_code}`),
    marker: {
      color: colors,
      opacity: rows.map((d) => d.line_code === "S8" ? 1 : LOMBARDY_LINE_CODES.has(d.line_code) ? 0.9 : 0.58),
      line: {
        color: rows.map((d) => d.line_code === "S8" ? COLORS.s8Strong : "rgba(255,255,255,0.92)"),
        width: rows.map((d) => d.line_code === "S8" ? 1.6 : 0.5)
      }
    },
    customdata: rows.map((d) => [d.line_name, d.operator, d.data_year, d.method]),
    hovertemplate: "<b>%{customdata[0]}</b><br>Operatore: %{customdata[1]}<br>Passeggeri annui: %{x:.1f} mln<br>Anno/metodo: %{customdata[2]}<br><extra>%{customdata[3]}</extra>"
  }], {
    title: { text: "Passeggeri annui per linea", x: 0.02, font: { size: 18 } },
    xaxis: { title: "Milioni di passeggeri annui" },
    yaxis: { title: "", automargin: true },
    showlegend: false,
    margin: { l: 96, r: 44, t: 62, b: 62 }
  });
}

async function chartMetro() {
  const rows = await loadCSV(DATASETS.metro);
  rows.sort((a, b) => a.passeggeri_annui - b.passeggeri_annui);
  const labels = rows.map((d) => shortMetroLabel(d.servizio));
  const annotations = rows.map((d, index) => ({
    x: d.passeggeri_annui / 1_000_000 + 0.22,
    y: labels[index],
    text: `${d.passeggeri_annui_label || `${fmt(d.passeggeri_annui / 1_000_000, 1)} mln`} · freq. ${d.frequenza_box || d.freq_label}`,
    showarrow: false,
    xanchor: "left",
    yanchor: "middle",
    align: "left",
    font: { size: isMobile() ? 10 : 11, color: d.servizio.includes("S8") ? COLORS.s8Strong : COLORS.muted }
  }));
  return render("plot-metro", [{
    type: "bar",
    orientation: "h",
    x: rows.map((d) => d.passeggeri_annui / 1_000_000),
    y: labels,
    marker: {
      color: rows.map((d) => d.colore_hex || (d.servizio.includes("S8") ? COLORS.s8 : "#b7c5c7")),
      opacity: rows.map((d) => d.servizio.includes("S8") ? 1 : 0.72),
      line: {
        color: rows.map((d) => d.servizio.includes("S8") ? COLORS.s8Strong : "rgba(255,255,255,0.95)"),
        width: rows.map((d) => d.servizio.includes("S8") ? 1.6 : 0.5)
      }
    },
    customdata: rows.map((d) => [
      d.servizio,
      d.passeggeri_annui_label || `${(d.passeggeri_annui / 1_000_000).toLocaleString("it-IT", { maximumFractionDigits: 2 })} mln`,
      d.frequenza_box || d.freq_label,
      d.tipo_dato_passeggeri || "",
      d.note || ""
    ]),
    hovertemplate: "<b>%{customdata[0]}</b><br>Passeggeri annui: %{customdata[1]}<br>Frequenza: %{customdata[2]}<br>Tipo dato: %{customdata[3]}<br><extra>%{customdata[4]}</extra>"
  }], {
    title: { text: "La S8 ha numeri da metropolitana", x: 0.02, font: { size: 18 } },
    xaxis: { title: "Milioni di passeggeri annui", range: [0, 21.5] },
    yaxis: { title: "", automargin: true },
    showlegend: false,
    margin: { l: 190, r: 210, t: 62, b: 62 },
    annotations
  });
}

async function chartStazioni() {
  const rows = await loadCSV(DATASETS.stazioni);
  const byStation = grouped(rows, "Stazione");
  const labelStations = new Set(Object.keys(COLORS.meratese));
  const endLabels = [];
  const traces = Object.entries(byStation).map(([station, values]) => {
    const sub = values.sort((a, b) => a.Anno - b.Anno);
    const isMer = Boolean(COLORS.meratese[station]);
    const last = sub[sub.length - 1];
    if (last && labelStations.has(station)) {
      endLabels.push({
        x: 2025.18,
        y: last.Indice_2019_100,
        text: `${shortStationLabel(station)} ${fmt(last.Indice_2019_100, 0)}`,
        color: isMer ? COLORS.meratese[station] : "#859399"
      });
    }
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
      hovertemplate: `<b>${station}</b><br>Anno %{x}<br>Indice: %{y:.1f}<br>Passeggeri saliti/giorno: %{customdata[0]:,.0f}<br><extra>%{customdata[1]}</extra>`
    };
  });
  return render("plot-stazioni", traces, {
    title: { text: "Passeggeri nelle stazioni S8, base 2019=100", x: 0.02, font: { size: 18 } },
    yaxis: { title: "Indice 2019=100" },
    xaxis: { title: "Anno", dtick: 2, range: [2015, 2027.3] },
    legend: { orientation: "h", y: -0.25, x: 0 },
    margin: { l: 78, r: isMobile() ? 86 : 190, t: 62, b: 68 },
    annotations: endLabelAnnotations(endLabels, { x: 2025.22, minGap: isMobile() ? 30 : 21, fontSize: isMobile() ? 10 : 11 })
  });
}

async function chartScatter() {
  const mobile = isMobile();
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
    hovertemplate: "<b>%{text}</b><br>Crescita passeggeri: %{x:.1f}%<br>Cambio passeggeri/corsa: %{y:.1f}%<br>Crescita passeggeri/giorno: %{customdata[0]:+,.0f}<br>Corse 2019-2025: %{customdata[1]:.0f} -> %{customdata[2]:.0f}<extra></extra>"
  }];
  traces.push({
    type: "scatter",
    mode: "markers",
    name: "Stazioni meratesi",
    x: mer.map((d) => d.Growth_pct_Saliti24H),
    y: mer.map((d) => d.Growth_pct_Saliti_per_corsa),
    text: mer.map((d) => d.Label),
    textposition: ["top right", "top right", "bottom right", "bottom right"],
    marker: {
      size: mobile ? 15 : 17,
      color: mer.map((d) => COLORS.meratese[d.Label] || COLORS.s8),
      line: { color: "#ffffff", width: 1.5 }
    },
    textfont: { size: mobile ? 10 : 12 },
    customdata: mer.map((d) => [d.Delta_abs_Saliti24H, d.Corse24H_2019, d.Corse24H_2025]),
    hovertemplate: "<b>%{text}</b><br>Crescita passeggeri: %{x:.1f}%<br>Cambio passeggeri/corsa: %{y:.1f}%<br>Crescita passeggeri/giorno: %{customdata[0]:+,.0f}<br>Corse 2019-2025: %{customdata[1]:.0f} -> %{customdata[2]:.0f}<extra></extra>"
  });
  const keyLabels = ["MILANO S.CRISTOFORO", "Cernusco-Merate", "Olgiate-Calco-Brivio", "Airuno", "Osnago", "CARNATE USMATE", "ARCORE"];
  const labelOffsets = {
    "MILANO S.CRISTOFORO": { dx: 2, dy: 9 },
    "Cernusco-Merate": { dx: 2.5, dy: 12 },
    "Olgiate-Calco-Brivio": { dx: 2.5, dy: -8 },
    "CARNATE USMATE": { dx: 2, dy: 7 },
    "ARCORE": { dx: -7, dy: -5 }
  };
  const annotations = rows
    .filter((d) => keyLabels.includes(d.Label))
    .map((d) => ({
      x: d.Growth_pct_Saliti24H + (labelOffsets[d.Label]?.dx ?? (d.IsMeratese ? 2.2 : 1.3)),
      y: d.Growth_pct_Saliti_per_corsa + (labelOffsets[d.Label]?.dy ?? 2.5),
      text: d.Label,
      showarrow: false,
      xanchor: "left",
      yanchor: "middle",
      font: { size: d.IsMeratese ? 12 : 10.5, color: d.IsMeratese ? (COLORS.meratese[d.Label] || COLORS.s8Strong) : "#69777d" },
      bgcolor: "rgba(255,255,255,0.88)",
      bordercolor: d.IsMeratese ? (COLORS.meratese[d.Label] || COLORS.s8Strong) : "#ccd7d9",
      borderwidth: 0.8,
      borderpad: 3
    }));
  return render("plot-scatter", traces, {
    title: { text: "Crescita passeggeri nelle stazioni lombarde", x: 0.02, font: { size: 18 } },
    xaxis: { title: "Crescita % passeggeri 2019-2025", zeroline: true },
    yaxis: { title: "Cambiamento % passeggeri per corsa", zeroline: true },
    shapes: [
      { type: "line", x0: 0, x1: 0, y0: -80, y1: 150, line: { color: "#9fb1b4", width: 1, dash: "dot" } },
      { type: "line", x0: -80, x1: 170, y0: 0, y1: 0, line: { color: "#9fb1b4", width: 1, dash: "dot" } }
    ],
    legend: { orientation: "h", y: -0.2, x: 0 },
    annotations
  });
}

async function chartPunta() {
  const rows = await loadCSV(DATASETS.punta);
  const byStation = grouped(rows, "Stazione");
  const labelStations = new Set(Object.keys(COLORS.meratese));
  const endLabels = [];
  const traces = Object.entries(byStation).map(([station, values]) => {
    const sub = values.sort((a, b) => a.Anno - b.Anno);
    const isMer = Boolean(COLORS.meratese[station]);
    const last = sub[sub.length - 1];
    if (last && labelStations.has(station)) {
      endLabels.push({
        x: 2025.18,
        y: last.Peso_punta_pct,
        text: `${shortStationLabel(station)} ${fmt(last.Peso_punta_pct, 1)}%`,
        color: isMer ? COLORS.meratese[station] : "#859399"
      });
    }
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
      hovertemplate: `<b>${station}</b><br>Anno %{x}<br>Quota 7-9: %{y:.1f}%<br>Passeggeri 7-9: %{customdata[0]:,.0f}<br>Passeggeri/giorno: %{customdata[1]:,.0f}<extra></extra>`
    };
  });
  return render("plot-punta", traces, {
    title: { text: "Quota della punta mattutina nelle stazioni S8", x: 0.02, font: { size: 18 } },
    yaxis: { title: "Quota dei passeggeri tra le 7 e le 9 (%)", range: [0, 65] },
    xaxis: { title: "Anno", dtick: 2, range: [2015, 2027.3] },
    legend: { orientation: "h", y: -0.25, x: 0 },
    margin: { l: 88, r: isMobile() ? 92 : 190, t: 62, b: 68 },
    annotations: endLabelAnnotations(endLabels, { x: 2025.22, minGap: isMobile() ? 9 : 7.5, fontSize: isMobile() ? 10 : 11 })
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
  const annotations = rowsPlot.map((d) => ({
    x: d.totale + 120,
    y: d.station,
    text: `+${fmt(d.morbida)} fuori 7-9`,
    showarrow: false,
    xanchor: "left",
    yanchor: "middle",
    font: { size: isMobile() ? 10 : 12, color: COLORS.s8Strong },
    bgcolor: "rgba(255,255,255,0.88)",
    bordercolor: COLORS.s8Soft,
    borderpad: 3
  }));
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
    title: { text: "Crescita meratese: punta e resto della giornata", x: 0.02, font: { size: 18 } },
    barmode: "stack",
    xaxis: { title: "Passeggeri/giorno, variazione 2025-2019", range: [0, 5200] },
    yaxis: { title: "", automargin: true, tickfont: { size: 13 } },
    legend: { orientation: "h", y: -0.18, x: 0 },
    margin: { l: 190, r: 160, t: 62, b: 68 },
    annotations
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
