let chart = null;

const COLORS = {
  raw: "#C9A9A6",
  filtered: "#E38AA0",
  peak: "#D46A87",
  annNormal: "#7FA88F",
  annAnomalo: "#B3261E",
  falsePositive: "#5A3B42",
  missed: "#B3261E",
  axis: "#B98A96",
};

function setStatus(text, variant) {
  const pill = document.getElementById("status-pill");
  pill.textContent = text;
  pill.className = "status-pill status-pill--" + variant;
}

function showError(msg) {
  const el = document.getElementById("error-msg");
  if (!msg) {
    el.hidden = true;
    el.textContent = "";
    return;
  }
  el.hidden = false;
  el.textContent = msg;
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function renderChart(data) {
  const fsDs = data.fs_ds;
  const filtered = data.filtered;
  const v = data.validation;

  const toXY = (arr) => arr.map((val, i) => ({ x: i / fsDs, y: val }));
  const onFiltered = (idxs) => idxs.map((i) => ({ x: i / fsDs, y: filtered[i] }));

  // Rango vertical para ubicar la fila de latidos anotados arriba de la señal
  let yMin = Infinity;
  let yMax = -Infinity;
  for (const arr of [data.raw, filtered]) {
    for (const val of arr) {
      if (val < yMin) yMin = val;
      if (val > yMax) yMax = val;
    }
  }
  const span = yMax - yMin || 1;
  const yRow = yMax + 0.12 * span;
  const onRow = (idxs) => idxs.map((i) => ({ x: i / fsDs, y: yRow }));

  const datasets = [
    {
      type: "line",
      label: "cruda",
      data: toXY(data.raw),
      parsing: false,
      borderColor: COLORS.raw,
      borderWidth: 1,
      pointRadius: 0,
    },
    {
      type: "line",
      label: "filtrada",
      data: toXY(filtered),
      parsing: false,
      borderColor: COLORS.filtered,
      borderWidth: 1.5,
      pointRadius: 0,
    },
    {
      type: "scatter",
      label: "picos R",
      data: onFiltered(data.peaks),
      backgroundColor: COLORS.peak,
      pointRadius: 3,
      showLine: false,
    },
  ];

  if (v) {
    datasets.push(
      {
        type: "scatter",
        label: "anotado normal",
        data: onRow(v.ann_normal),
        backgroundColor: COLORS.annNormal,
        pointStyle: "triangle",
        rotation: 180, // apunta hacia abajo, hacia el latido
        pointRadius: 5,
        showLine: false,
      },
      {
        type: "scatter",
        label: "anotado anómalo",
        data: onRow(v.ann_anomalo),
        backgroundColor: COLORS.annAnomalo,
        pointStyle: "triangle",
        rotation: 180,
        pointRadius: 6,
        showLine: false,
      },
      {
        type: "scatter",
        label: "falso positivo",
        data: onFiltered(v.fp_peaks),
        borderColor: COLORS.falsePositive,
        borderWidth: 2,
        pointStyle: "crossRot",
        pointRadius: 7,
        showLine: false,
      },
      {
        type: "scatter",
        label: "latido no detectado",
        data: onFiltered(v.fn_beats),
        backgroundColor: "transparent",
        borderColor: COLORS.missed,
        borderWidth: 2,
        pointStyle: "rectRot",
        pointRadius: 8,
        showLine: false,
      }
    );
  }

  const ctx = document.getElementById("ecg-chart").getContext("2d");
  if (chart) chart.destroy();

  const tickFont = { family: "IBM Plex Mono", size: 10 };

  chart = new Chart(ctx, {
    type: "line",
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      normalized: true,
      scales: {
        x: {
          type: "linear",
          min: 0,
          max: (filtered.length - 1) / fsDs,
          grid: { display: false },
          ticks: { color: COLORS.axis, font: tickFont, maxTicksLimit: 16 },
          title: { display: true, text: "tiempo (s)", color: COLORS.axis, font: tickFont },
        },
        y: {
          ...(v ? { suggestedMax: yRow + 0.08 * span } : {}),
          ticks: { color: COLORS.axis, font: tickFont },
          grid: { color: "#F0D9DD" },
        },
      },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
    },
  });
}

function renderBeatStrip(labels) {
  const strip = document.getElementById("beat-strip");
  strip.innerHTML = "";
  labels.forEach((label) => {
    const div = document.createElement("div");
    div.className = "beat " + (label === "Normal" ? "beat--normal" : "beat--anomalo");
    div.title = label;
    strip.appendChild(div);
  });
}

function setBar(prefix, anomaloPct) {
  const a = Math.max(0, Math.min(100, anomaloPct));
  document.getElementById(`bar-${prefix}-normal`).style.width = 100 - a + "%";
  document.getElementById(`bar-${prefix}-anomalo`).style.width = a + "%";
}

function renderValidation(data) {
  const v = data.validation;
  const body = document.getElementById("val-body");
  const note = document.getElementById("val-note");
  const legendVal = document.getElementById("legend-val");

  if (!v) {
    body.hidden = true;
    note.hidden = false;
    legendVal.hidden = true;
    return;
  }

  body.hidden = false;
  note.hidden = true;
  legendVal.hidden = false;

  setText("val-sens", v.sens);
  setText("val-ppv", v.ppv);
  setText("val-count", `${data.n_latidos} / ${v.n_anotados}`);
  setText("val-errors", `${v.fp} · ${v.fn}`);

  setBar("ann", v.anotado_anomalo_pct);
  setBar("rule", data.summary.anomalo_pct);
  setText("txt-ann", v.anotado_anomalo_pct + "% anómalo");
  setText("txt-rule", data.summary.anomalo_pct + "% anómalo");
}

function renderResult(data) {
  renderChart(data);
  renderBeatStrip(data.labels);
  renderValidation(data);

  setText("stat-bpm", data.bpm);
  setText("stat-hrv", data.hrv_sdnn_ms);
  setText("stat-n", data.n_latidos);
  setText("stat-anom", data.summary.anomalo_pct);
  setText("pct-normal", data.summary.normal_pct + "%");
  setText("pct-anomalo", data.summary.anomalo_pct + "%");

  if (data.summary.anomalo_pct > 15) {
    setStatus("posible alteración", "alert");
  } else {
    setStatus("ritmo normal", "normal");
  }
}

async function loadMitbih() {
  showError(null);
  setStatus("cargando…", "idle");
  const record = document.getElementById("record-id").value.trim() || "100";
  const seconds = document.getElementById("seconds").value;

  try {
    const res = await fetch(`/api/mitbih?record=${encodeURIComponent(record)}&seconds=${seconds}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error desconocido");
    renderResult(data);
  } catch (err) {
    showError(err.message);
    setStatus("sin señal cargada", "idle");
  }
}

async function loadCsv() {
  showError(null);
  const fileInput = document.getElementById("csv-file");
  if (!fileInput.files.length) {
    showError("Selecciona un archivo CSV primero.");
    return;
  }
  setStatus("cargando…", "idle");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("fs", document.getElementById("fs-input").value);

  try {
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error desconocido");
    renderResult(data);
  } catch (err) {
    showError(err.message);
    setStatus("sin señal cargada", "idle");
  }
}

document.getElementById("seconds").addEventListener("input", (e) => {
  document.getElementById("seconds-out").textContent = e.target.value;
});
document.getElementById("load-mitbih").addEventListener("click", loadMitbih);
document.getElementById("load-csv").addEventListener("click", loadCsv);
