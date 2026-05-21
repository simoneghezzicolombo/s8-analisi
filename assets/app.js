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

function initMapFrameResize() {
  const iframes = Array.from(document.querySelectorAll(".map-frame iframe, .isochrone-static-frame iframe"));
  if (!iframes.length) return;
  const resize = () => {
    iframes.forEach((iframe) => {
      try {
        const doc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!doc) return;
        const height = Math.max(
          doc.body?.scrollHeight || 0,
          doc.documentElement?.scrollHeight || 0
        );
        if (height > 0) {
          iframe.style.height = `${height}px`;
          iframe.style.minHeight = `${height}px`;
        }
      } catch (error) {
        console.warn("Impossibile ridimensionare la mappa incorporata.", error);
      }
    });
  };
  iframes.forEach((iframe) => iframe.addEventListener("load", () => {
    resize();
    window.setTimeout(resize, 800);
    window.setTimeout(resize, 1800);
  }));
  window.addEventListener("resize", resize);
  resize();
}

window.addEventListener("DOMContentLoaded", () => {
  init();
  initMapFrameResize();
  initLanguageToggle();
});

const S8_TRANSLATIONS = [
  ["Navigazione principale", "Primary navigation"],
  ["Risultati", "Results"],
  ["Grafici", "Charts"],
  ["Mappa", "Map"],
  ["Metodo", "Method"],
  ["Dataset", "Datasets"],
  ["Trasporto pubblico · Open data · Analisi territoriale", "Public transport · Open data · Territorial analysis"],
  ["Dati e grafici interattivi sulla linea S8 Lecco-Carnate-Milano e sulle stazioni del Meratese.", "Interactive data and charts on the S8 Lecco-Carnate-Milano rail line and the Meratese stations."],
  ["Questa pagina raccoglie la versione esplorabile dei grafici della presentazione, con dataset, fonti e script collegati per rendere verificabili i numeri discussi nell'incontro.", "This page collects the explorable version of the presentation charts, with datasets, sources and linked scripts so that the figures discussed in the meeting can be checked."],
  ["Esplora i grafici", "Explore the charts"],
  ["Scarica manifest CSV", "Download CSV manifest"],
  ["Presentazione PDF", "Presentation PDF"],
  ["Metodologia completa", "Full methodology"],
  ["Lettura sintetica", "Short reading"],
  ["La S8 non appare come una linea locale marginale: cresce più delle altre linee suburbane considerate, ha volumi annui comparabili ad alcune metropolitane italiane e mostra una crescita molto marcata nelle stazioni del Meratese.", "The S8 does not look like a marginal local line: it grows more than the other suburban lines considered, has annual volumes comparable to some Italian metros, and shows very strong growth in the Meratese stations."],
  ["Il punto più interessante è che la crescita non è concentrata solo nella punta 7-9: una quota molto ampia avviene nel resto della giornata, suggerendo un uso più ordinario e distribuito del treno.", "The most interesting point is that growth is not concentrated only in the 7-9 peak: a very large share happens during the rest of the day, suggesting a more ordinary and distributed use of the train."],
  ["Quattro numeri chiave", "Four key numbers"],
  ["Una lettura rapida prima di entrare nei grafici interattivi.", "A quick reading before entering the interactive charts."],
  ["S8 nel 2025 rispetto al 2019, indice sugli utenti/giorno feriale.", "S8 in 2025 compared with 2019, index on weekday users."],
  ["Stima dei passeggeri annui della S8 Lecco-Carnate-Milano.", "Estimated annual passengers on the S8 Lecco-Carnate-Milano."],
  ["Crescita 2019-2025 delle quattro stazioni meratesi considerate.", "2019-2025 growth of the four Meratese stations considered."],
  ["Quota della crescita meratese fuori dalla fascia 7-9.", "Share of Meratese growth outside the 7-9 time band."],
  ["Grafici interattivi", "Interactive charts"],
  ["Ogni grafico è collegato al proprio CSV, alle fonti dei dati e agli script utili per ricostruire l'analisi.", "Each chart is linked to its CSV, data sources and scripts useful to reconstruct the analysis."],
  ["1. Evoluzione delle linee suburbane Trenord", "1. Evolution of Trenord suburban lines"],
  ["Cosa mostra.", "What it shows."],
  ["La S8 è confrontata con le altre grandi linee suburbane Trenord: S1/S12, S5, S6 e totale Trenord. Nel 2025 arriva a indice 157,7: non è solo recupero post-Covid, ma un cambio di scala per la Lecco-Milano e per il Meratese, dove la crescita delle stazioni è molto più intensa della media.", "The S8 is compared with the other major Trenord suburban lines: S1/S12, S5, S6 and the Trenord total. In 2025 it reaches index 157.7: this is not just a post-Covid recovery, but a scale change for the Lecco-Milano corridor and for the Meratese area, where station growth is far stronger than average."],
  ["2. Variazione assoluta 2025-2024", "2. Absolute change 2025-2024"],
  ["Nel confronto 2025-2024 la S8 è la linea con la crescita assoluta maggiore: +22.800 passeggeri/giorno feriale nelle campagne comparabili. Il caso S1/S12 va letto insieme all'offerta: il servizio passa circa da 70 a 130 corse al giorno grazie alla S12, quindi l'aumento è legato anche a un forte incremento di frequenza.", "In the 2025-2024 comparison, the S8 has the largest absolute increase: +22,800 weekday passengers in comparable counts. The S1/S12 case should be read together with service supply: thanks to the S12, service rises from roughly 70 to 130 trains per day, so the increase is also tied to a strong frequency increase."],
  ["3. Passeggeri annui per linea", "3. Annual passengers by line"],
  ["La S8 è stimata al quarto posto tra le linee locali non AV considerate, con circa 14,8 milioni di passeggeri annui. Prima del Covid non compariva in questa classifica: oggi entra nel gruppo delle linee locali più usate d'Italia, sopra molte relazioni storicamente più riconosciute.", "The S8 is estimated in fourth place among the non-high-speed local lines considered, with around 14.8 million annual passengers. Before Covid it did not appear in this ranking: today it enters the group of Italy's most-used local rail lines, above several historically better-known routes."],
  ["4. S8 e metropolitane italiane", "4. S8 and Italian metro systems"],
  ["Con circa 14,8 milioni di passeggeri annui, la S8 è vicina alla metropolitana di Genova e poco sotto Roma C e Brescia. La differenza decisiva è l'offerta: la S8 viaggia con frequenza indicativa di 30 minuti, mentre molte metropolitane hanno passaggi ogni pochi minuti.", "With around 14.8 million annual passengers, the S8 is close to the Genoa metro and just below Rome C and Brescia. The decisive difference is service supply: the S8 runs roughly every 30 minutes, while many metro systems run every few minutes."],
  ["5. Passeggeri nelle stazioni S8, 2015-2025", "5. Passengers in S8 stations, 2015-2025"],
  ["Le quattro stazioni meratesi crescono tutte in modo marcato dopo il 2022. Nel complesso passano da 4.620 a 8.980 passeggeri saliti in un giorno feriale di novembre: quasi un raddoppio rispetto al 2019, con Airuno e Osnago che superano quota 200 nell'indice.", "The four Meratese stations all grow markedly after 2022. Together they rise from 4,620 to 8,980 passengers boarding on a November weekday: almost double the 2019 level, with Airuno and Osnago both exceeding index 200."],
  ["6. Crescita passeggeri nelle stazioni lombarde", "6. Passenger growth in Lombardy stations"],
  ["Nel confronto con 148 stazioni lombarde comparabili, Airuno e Osnago sono prima e seconda per crescita percentuale; Cernusco-Merate e Olgiate-Calco-Brivio sono quarta e quinta. In mezzo c'è Milano S. Cristoforo, un caso particolare perché pesa l'apertura della M4 e la riorganizzazione legata alla chiusura di Porta Genova. Sono escluse le stazioni sotto 700 passeggeri/giorno nel 2019 e quelle senza confronto omogeneo 2019-2025.", "Compared with 148 comparable Lombardy stations, Airuno and Osnago rank first and second for percentage growth; Cernusco-Merate and Olgiate-Calco-Brivio rank fourth and fifth. Milano S. Cristoforo sits in between, a special case affected by the opening of M4 and the reorganisation linked to the Porta Genova closure. Stations below 700 passengers/day in 2019 and those without a homogeneous 2019-2025 comparison are excluded."],
  ["7. Quota della punta mattutina nelle stazioni S8", "7. Morning-peak share in S8 stations"],
  ["Nel Meratese i passeggeri crescono molto, ma non più solo nella punta pendolare classica. Le quattro stazioni passano da 4.620 a 8.980 passeggeri/giorno tra 2019 e 2025; la fascia 7-9 cresce da 1.990 a 2.530, ma la sua quota scende dal 43,1% al 28,2%. Significa abitudini più distribuite: lavoro ibrido, studio, servizi e spostamenti non concentrati solo sull'andata mattutina.", "In the Meratese area, passengers grow sharply, but no longer only in the classic commuter peak. The four stations rise from 4,620 to 8,980 passengers/day between 2019 and 2025; the 7-9 band grows from 1,990 to 2,530, but its share falls from 43.1% to 28.2%. This suggests more distributed habits: hybrid work, study, services and trips that are not concentrated only in the morning outbound journey."],
  ["8. Quanto cresce in punta e quanto fuori punta?", "8. How much growth is peak and off-peak?"],
  ["La crescita meratese 2019-2025 è di +4.360 passeggeri/giorno. Di questi, +540 sono nella fascia 7-9 e +3.820 sono nel resto della giornata: quasi nove nuovi passeggeri su dieci arrivano fuori dalla punta mattutina. Il problema quindi non è solo \"più pendolari al mattino\", ma una domanda quotidiana più larga e continua.", "Meratese growth in 2019-2025 is +4,360 passengers/day. Of these, +540 are in the 7-9 band and +3,820 are in the rest of the day: almost nine new passengers out of ten arrive outside the morning peak. The issue, then, is not only \"more morning commuters\", but broader and more continuous daily demand."],
  ["Preparazione grafico interattivo...", "Preparing interactive chart..."],
  ["Dataset CSV", "CSV dataset"],
  ["PNG statico", "Static PNG"],
  ["Fonti del grafico:", "Chart sources:"],
  ["tutte le fonti", "all sources"],
  ["Metodo e cautela interpretativa", "Method and interpretive caution"],
  ["I grafici sono pensati per essere leggibili pubblicamente, ma restano collegati a file dati verificabili.", "The charts are designed to be publicly readable, while remaining linked to verifiable data files."],
  ["Definizioni principali", "Main definitions"],
  ["indica i passeggeri saliti in stazione nell'arco della giornata.", "indicates passengers boarding at the station across the day."],
  ["indica la fascia di punta mattutina. Gli indici sono normalizzati con base 2019=100.", "indicates the morning peak band. Indices are normalised with 2019=100 as the base."],
  ["Leggi metodologia completa", "Read full methodology"],
  ["Struttura dei dataset", "Dataset structure"],
  ["Perché alcuni confronti sono delicati", "Why some comparisons are delicate"],
  ["I dati derivano da campagne di frequentazione, non da conteggi continui. Per questo, nei confronti 2024-2025 si usano solo campagne presenti in entrambi gli anni.", "The data comes from ridership campaigns, not continuous counts. For this reason, 2024-2025 comparisons use only campaigns that are present in both years."],
  ["Reference numeri presentazione", "Presentation figures reference"],
  ["Micro-fonti per grafici", "Micro-sources for charts"],
  ["Script e riproducibilità", "Scripts and reproducibility"],
  ["Il codice usato per grafici statici, prove grafiche e pagina interattiva è pubblicato insieme ai dataset.", "The code used for static charts, graphic tests and the interactive page is published together with the datasets."],
  ["Indice degli script", "Script index"],
  ["Riproducibilità grafico per grafico", "Chart-by-chart reproducibility"],
  ["Grafici interattivi della pagina", "Interactive charts on the page"],
  ["Grafici statici per Canva", "Static charts for Canva"],
  ["Extra: bacini potenziali delle fermate S8", "Extra: potential catchment areas of S8 stops"],
  ["Una lettura territoriale complementare ai grafici di frequentazione: non misura i passeggeri, ma la popolazione raggiungibile dalle fermate.", "A territorial reading that complements ridership charts: it does not measure passengers, but the population reachable from the stops."],
  ["La mappa stima il bacino potenziale delle 9 fermate S8 tra Arcore e Lecco, a piedi o in auto, fino a 15 minuti. È utile per capire dove la domanda può crescere: non solo quante persone usano oggi la linea, ma quante persone vivono abbastanza vicino alle fermate da poterla usare con maggiore facilità se il servizio diventa più attrattivo.", "The map estimates the potential catchment area of the 9 S8 stops between Arcore and Lecco, on foot or by car, up to 15 minutes. It helps show where demand can grow: not only how many people use the line today, but how many people live close enough to the stops to use it more easily if the service becomes more attractive."],
  ["Le stazioni di confronto non entrano nei totali S8: servono a delimitare il bacino in modo prudente. Ogni cella di popolazione viene assegnata una sola volta alla stazione più accessibile via rete: se è tra due fermate S8 non viene duplicata, e se è servita meglio da una stazione esterna non entra nel bacino S8 pubblicato.", "Comparison stations are not included in S8 totals: they are used to delimit the catchment area prudently. Each population cell is assigned only once to the most accessible station on the network: if it lies between two S8 stops it is not duplicated, and if it is better served by an external station it is not included in the published S8 catchment."],
  ["Apri mappa standalone", "Open standalone map"],
  ["Fonti mappa", "Map sources"],
  ["Nota riproducibilità", "Reproducibility note"],
  ["Confronto 5, 10 e 15 minuti", "5, 10 and 15-minute comparison"],
  ["La popolazione deriva da WorldPop 2020, una griglia di popolazione residente a circa 100 metri di risoluzione. Ogni cella viene assegnata alla fermata raggiungibile prima via rete, senza duplicare chi sta tra due stazioni.", "Population comes from WorldPop 2020, a resident-population grid at roughly 100-metre resolution. Each cell is assigned to the stop that can be reached first through the network, without duplicating people located between two stations."],
  ["Dataset scaricabili", "Downloadable datasets"],
  ["In alto i CSV già processati per i grafici; in fondo i dati originali e i link ai portali fonte.", "Processed CSV files for the charts are listed first; original data and source portals are listed below."],
  ["Dataset processati", "Processed datasets"],
  ["File già puliti o aggregati, consigliati per verificare e riusare i grafici.", "Cleaned or aggregated files, recommended to verify and reuse the charts."],
  ["Dataset originali e fonti", "Original datasets and sources"],
  ["Link ai portali fonte e copie locali dei file grezzi usati come base.", "Links to source portals and local copies of the raw files used as a base."],
  ["Analisi su dati Regione Lombardia, Trenord e fonti indicate nei dataset.", "Analysis based on Regione Lombardia, Trenord and the sources listed in the datasets."],
  ["Pagina interattiva con dati, grafici e metodologia sulla linea S8 Milano-Lecco e sulle stazioni del Meratese.", "Interactive page with data, charts and methodology on the S8 Milano-Lecco line and the Meratese stations."]
];

function initLanguageToggle() {
  const toEn = new Map(S8_TRANSLATIONS);
  const toIt = new Map(S8_TRANSLATIONS.map(([it, en]) => [en, it]));

  function translate(lang) {
    const map = lang === "en" ? toEn : toIt;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        if (node.parentElement && ["SCRIPT", "STYLE"].includes(node.parentElement.tagName)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      const value = node.nodeValue;
      const trimmed = value.trim();
      const replacement = map.get(trimmed);
      if (replacement) node.nodeValue = value.replace(trimmed, replacement);
    });

    document.querySelectorAll("[aria-label], [title], [content]").forEach((element) => {
      ["aria-label", "title", "content"].forEach((attr) => {
        const value = element.getAttribute(attr);
        if (value && map.has(value)) element.setAttribute(attr, map.get(value));
      });
    });

    document.documentElement.lang = lang;
    document.querySelectorAll("[data-lang-toggle]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.langToggle === lang));
    });
    localStorage.setItem("sgc-s8-language", lang);
  }

  document.querySelectorAll("[data-lang-toggle]").forEach((button) => {
    button.addEventListener("click", () => translate(button.dataset.langToggle));
  });
  translate(localStorage.getItem("sgc-s8-language") || "it");
}
