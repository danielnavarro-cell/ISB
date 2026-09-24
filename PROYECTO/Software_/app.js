let chart = null;

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

function renderChart(raw, filtered, peaks) {
  const labels = filtered.map((_, i) => i);
  const peakPoints = peaks.map((p) => ({ x: p, y: filtered[p] }));

  const ctx = document.getElementById("ecg-chart").getContext("2d");
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "cruda",
          data: raw,
          borderColor: "#C9A9A6",
          borderWidth: 1,
          pointRadius: 0,
          tension: 0.1,
        },
        {
          label: "filtrada",
          data: filtered,
          borderColor: "#E38AA0",
          borderWidth: 1.5,
          pointRadius: 0,
          tension: 0.1,
        },
        {
          type: "scatter",
          label: "picos R",
          data: peakPoints,
          backgroundColor: "#D46A87",
          pointRadius: 3,
          showLine: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        x: { display: false },
        y: { ticks: { color: "#B98A96", font: { family: "IBM Plex Mono", size: 10 } }, grid: { color: "#F0D9DD" } },
      },
      plugins: { legend: { display: false } },
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

function renderResult(data) {
  renderChart(data.raw, data.filtered, data.peaks);
  renderBeatStrip(data.labels);

  document.getElementById("stat-bpm").textContent = data.bpm;
  document.getElementById("stat-hrv").textContent = data.hrv_sdnn_ms;
  document.getElementById("stat-n").textContent = data.n_latidos;
  document.getElementById("stat-anom").textContent = data.summary.anomalo_pct;
  document.getElementById("pct-normal").textContent = data.summary.normal_pct + "%";
  document.getElementById("pct-anomalo").textContent = data.summary.anomalo_pct + "%";

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
