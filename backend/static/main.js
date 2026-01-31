let pm25ChartInstance = null;
let pm10ChartInstance = null;
let aqiChartInstance  = null;

// fetch history
async function fetchHistory() {
  const res = await fetch("/api/history");
  return await res.json();
}

// render dashboard
async function renderDashboard() {
  const history = await fetchHistory();
  if (!history || history.length < 4) return;

  const labels = history.map(d => {
    const t = new Date(d.timestamp_utc);
    return t.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  });

  const pm25 = history.map(d => d.pm2_5);
  const pm10 = history.map(d => d.pm10);
  const historyAQI = history.map(d => d.current_aqi);

  const len = history.length;
  const actualAQI = history[len - 1].current_aqi;
  const predictedForNow = history[len - 4].predicted_aqi_3h;

  /* AQI Card */
  const currentEl = document.getElementById("currentAQI");
  const catEl = document.getElementById("aqiCategory");
  const predEl = document.getElementById("predictedNow");
  const deltaEl = document.getElementById("aqiDelta");

  currentEl.textContent = actualAQI;
  predEl.textContent = predictedForNow;

  let category = "Good";
  let color = "#22c55e";
  if (actualAQI > 50)  { category = "Moderate"; color = "#eab308"; }
  if (actualAQI > 100) { category = "Poor";     color = "#f97316"; }
  if (actualAQI > 200) { category = "Very Poor";color = "#ef4444"; }

  catEl.textContent = category;
  currentEl.style.color = color;

  const delta = actualAQI - predictedForNow;
  deltaEl.textContent = delta > 0 ? `+${delta}` : delta;
  deltaEl.style.color = Math.abs(delta) <= 15 ? "#22c55e" : "#ef4444";

  /* Forecast chart logic */
  const futureAQI = history.slice(-3).map(d => d.predicted_aqi_3h);
  const extendedLabels = [...labels, "+1h", "+2h", "+3h"];

  const aqiHistoryLine = historyAQI.concat([null, null, null]);
  const aqiForecastLine =
    new Array(historyAQI.length - 1).fill(null)
      .concat([historyAQI[historyAQI.length - 1]])
      .concat(futureAQI);

  if (pm25ChartInstance) pm25ChartInstance.destroy();
  if (pm10ChartInstance) pm10ChartInstance.destroy();
  if (aqiChartInstance)  aqiChartInstance.destroy();

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "nearest", intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: { yAlign: "bottom", caretPadding: 10, padding: 10 }
    }
  };

  pm25ChartInstance = new Chart(pm25Chart, {
    type: "line",
    data: { labels, datasets: [{ data: pm25, borderColor: "#0ea5e9", tension: 0.35 }] },
    options: commonOptions
  });

  pm10ChartInstance = new Chart(pm10Chart, {
    type: "line",
    data: { labels, datasets: [{ data: pm10, borderColor: "#6366f1", tension: 0.35 }] },
    options: commonOptions
  });

  aqiChartInstance = new Chart(aqiChart, {
    type: "line",
    data: {
      labels: extendedLabels,
      datasets: [
        { data: aqiHistoryLine, borderColor: "#ef4444", tension: 0.35 },
        { data: aqiForecastLine, borderColor: "#22c55e", borderDash: [6,6], tension: 0.35 }
      ]
    },
    options: commonOptions
  });
}

renderDashboard();
setInterval(renderDashboard, 15 * 60 * 1000);