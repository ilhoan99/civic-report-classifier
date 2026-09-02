/* Demo logic. All predictions are precomputed real model outputs
 * (docs/data/examples.json); nothing is mocked in the browser. */
"use strict";

const AGENCIES = {
  LocalGov: { en: "Local government",              ko: "지자체" },
  Police:   { en: "National Police Agency",        ko: "경찰청" },
  KEPCO:    { en: "Korea Electric Power Corp.",    ko: "한국전력공사" },
  MOEL:     { en: "Ministry of Employment & Labor", ko: "고용노동부" },
  KEC:      { en: "Korea Expressway Corp.",        ko: "한국도로공사" },
  KORAIL:   { en: "Korea Railroad Corp.",          ko: "한국철도공사" },
  EduOff:   { en: "Office of Education",           ko: "교육청" },
  LH:       { en: "Land & Housing Corp.",          ko: "한국토지주택공사" },
  KRC:      { en: "Korea Rural Community Corp.",   ko: "한국농어촌공사" },
  MOLIT:    { en: "Ministry of Land & Transport",  ko: "국토교통부" },
  MSIT:     { en: "Ministry of Science & ICT",     ko: "과학기술정보통신부" },
  KCTA:     { en: "Telecom Operators Assoc.",      ko: "한국통신사업자연합회" },
};
const RARE = new Set(["KRC", "KORAIL", "MSIT", "KEC", "EduOff", "LH", "MOLIT"]);

const state = { data: null, ex: 0, mode: "m1", sel: null };
let map, baseLayer, candLayer, chipMarkers = [];

const $ = (id) => document.getElementById(id);
const key = (d) => d.sido + "|" + d.sigungu;

function currentExample() { return state.data.examples[state.ex]; }

/* ---------- left panel ---------- */

function renderTabs() {
  const tabs = $("example-tabs");
  tabs.innerHTML = "";
  state.data.examples.forEach((ex, i) => {
    const b = document.createElement("button");
    b.textContent = ex.title;
    b.className = i === state.ex ? "on" : "";
    b.onclick = () => { state.ex = i; state.sel = key(ex.districts[0]); syncAll(); };
    tabs.appendChild(b);
  });
}

function renderPanel() {
  const ex = currentExample();
  $("report-ko").textContent = ex.text_ko;
  $("report-en").textContent = ex.text_en;
  const noteEl = $("example-note");
  noteEl.innerHTML = "";
  (ex.points || []).forEach((pt) => {
    const li = document.createElement("li");
    li.textContent = pt;
    noteEl.appendChild(li);
  });
  $("btn-m1").className = state.mode === "m1" ? "on" : "";
  $("btn-t0").className = state.mode === "t0" ? "on" : "";

  const d = ex.districts.find((x) => key(x) === state.sel) || ex.districts[0];
  const mi = $("model-input");
  if (state.mode === "m1") {
    mi.innerHTML = '<span class="prefix">[' + d.sido + " " + d.sigungu + "]</span> "
      + escapeHtml(ex.text_ko);
    $("pred-title").textContent = "prediction — filed in " + d.name_en;
  } else {
    mi.textContent = ex.text_ko;
    $("pred-title").textContent = "prediction — location ignored (same in every district)";
  }

  const pred = state.mode === "m1" ? d : ex.text_only;
  renderBars(pred.top, state.mode === "t0");
  renderBadge(pred);
}

function renderBars(top, baseline) {
  const box = $("pred-bars");
  box.innerHTML = "";
  top.forEach((t) => {
    const row = document.createElement("div");
    row.className = "bar-row" + (baseline ? " baseline" : "")
      + (!baseline && RARE.has(t.agency) ? " rare" : "");
    row.innerHTML =
      '<span class="name" title="' + AGENCIES[t.agency].ko + '">' + t.agency + "</span>"
      + '<span class="track"><span class="fill"></span></span>'
      + '<span class="pct">' + (t.p * 100).toFixed(1) + "%</span>";
    box.appendChild(row);
    requestAnimationFrame(() => requestAnimationFrame(() => {
      row.querySelector(".fill").style.width = (t.p * 100) + "%";
    }));
  });
}

function renderBadge(pred) {
  const tau = state.data.meta.deferral_threshold;
  const el = $("pred-badge");
  const p1 = pred.top[0].p;
  if (pred.defer) {
    el.innerHTML = '<span class="badge defer">defer to human review</span>'
      + '<span class="badge-note">top confidence ' + (p1 * 100).toFixed(1)
      + "% &lt; threshold " + (tau * 100).toFixed(1) + "%</span>";
  } else {
    el.innerHTML = '<span class="badge auto">auto-route to '
      + AGENCIES[pred.top[0].agency].en + "</span>"
      + '<span class="badge-note">top confidence ' + (p1 * 100).toFixed(1)
      + "% &ge; threshold " + (tau * 100).toFixed(1) + "%</span>";
  }
}

function escapeHtml(s) {
  return s.replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

/* ---------- main map ---------- */

function initMap(districtsGeo) {
  map = L.map("map", { scrollWheelZoom: false, zoomSnap: 0.5 })
    .setView([36.35, 127.9], 7);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
    maxZoom: 12,
    className: "muted-tiles",
  }).addTo(map);
  baseLayer = L.geoJSON(districtsGeo, {
    style: { color: "#c3cad3", weight: 0.5, fill: true,
             fillColor: "#ffffff", fillOpacity: 0.05 },
    interactive: false,
  }).addTo(map);
}

function renderMap() {
  const ex = currentExample();
  const wanted = new Set(ex.districts.map(key));
  if (candLayer) candLayer.remove();
  chipMarkers.forEach((m) => m.remove());
  chipMarkers = [];

  candLayer = L.geoJSON(state.data._districtsGeo, {
    filter: (f) => wanted.has(f.properties.sido + "|" + f.properties.sigungu),
    style: (f) => styleFor(f.properties.sido + "|" + f.properties.sigungu),
    onEachFeature: (f, layer) => {
      const k = f.properties.sido + "|" + f.properties.sigungu;
      layer.on("click", () => { state.sel = k; syncAll(); });
    },
  }).addTo(map);

  ex.districts.forEach((d) => {
    const pred = state.mode === "m1" ? d : currentExample().text_only;
    const cls = "district-chip"
      + (state.mode === "t0" ? " baseline"
         : RARE.has(pred.top[0].agency) ? " rare" : "")
      + (key(d) === state.sel ? " sel" : "");
    const html = '<div class="' + cls + '">' + pred.top[0].agency
      + " <small>" + (pred.top[0].p * 100).toFixed(0) + "%</small></div>";
    const mk = L.marker(d.center, {
      icon: L.divIcon({ className: "", html: html, iconSize: null,
                        iconAnchor: [30, 12] }),
    }).addTo(map);
    mk.on("click", () => { state.sel = key(d); syncAll(); });
    chipMarkers.push(mk);
  });

  if (renderMap._lastEx !== state.ex) {
    map.fitBounds(candLayer.getBounds().pad(0.25));
    renderMap._lastEx = state.ex;
  }
}

function styleFor(k) {
  const sel = k === state.sel;
  return {
    color: "#2f7d5f", weight: sel ? 2.5 : 1.4,
    fillColor: "#2f7d5f", fillOpacity: sel ? 0.3 : 0.12,
  };
}

function syncAll() {
  renderTabs();
  renderPanel();
  renderMap();
}

/* ---------- province choropleth ---------- */

function initChoropleth(provGeo, results) {
  const acc = {};
  results.provinces.forEach((p) => { acc[p.sido] = p; });
  const lo = 0.87, hi = 0.965;
  const color = (a) => {
    const t = Math.max(0, Math.min(1, (a - lo) / (hi - lo)));
    const mix = (x, y) => Math.round(x + (y - x) * t);
    return "rgb(" + mix(219, 30) + "," + mix(230, 79) + "," + mix(247, 156) + ")";
  };
  const pm = L.map("provmap", {
    zoomControl: false, scrollWheelZoom: false, dragging: false,
    doubleClickZoom: false, boxZoom: false, keyboard: false,
    attributionControl: false,
  });
  const layer = L.geoJSON(provGeo, {
    style: (f) => ({
      color: "#ffffff", weight: 1,
      fillColor: color(acc[f.properties.sido].accuracy), fillOpacity: 1,
    }),
    onEachFeature: (f, l) => {
      const p = acc[f.properties.sido];
      l.bindTooltip(
        "<b>" + p.name_en + "</b><br>accuracy " + (p.accuracy * 100).toFixed(1)
        + "%<br>macro-F1 " + (p.macro_f1 * 100).toFixed(1)
        + "<br>n = " + p.n.toLocaleString(),
        { sticky: true });
      l.on("mouseover", () => l.setStyle({ weight: 2, color: "#111827" }));
      l.on("mouseout", () => l.setStyle({ weight: 1, color: "#ffffff" }));
    },
  }).addTo(pm);
  pm.fitBounds(layer.getBounds().pad(0.02));

  const lg = $("prov-legend");
  lg.innerHTML = "<span>" + (lo * 100).toFixed(0) + "%</span>";
  for (let i = 0; i <= 4; i++) {
    const sw = document.createElement("span");
    sw.className = "sw";
    sw.style.background = color(lo + (hi - lo) * (i / 4));
    lg.appendChild(sw);
  }
  lg.insertAdjacentHTML("beforeend", "<span>" + (hi * 100).toFixed(1)
    + "%</span><span style='margin-left:8px'>accuracy</span>");
}

/* ---------- deferral curve ---------- */

function initDeferral(results) {
  const curve = results.deferral.curve;
  const op = results.deferral.operating_point;
  const svg = $("defcurve");
  const W = 460, H = 260, mL = 52, mR = 14, mT = 14, mB = 36;
  const yLo = 0.94, yHi = 1.0;
  const X = (c) => mL + (c - 0) * (W - mL - mR);
  const Y = (a) => mT + (yHi - a) / (yHi - yLo) * (H - mT - mB);
  const ns = "http://www.w3.org/2000/svg";
  const el = (tag, attrs, text) => {
    const e = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
    if (text) e.textContent = text;
    svg.appendChild(e);
    return e;
  };

  for (let a = yLo; a <= yHi + 1e-9; a += 0.01) {
    el("line", { x1: mL, x2: W - mR, y1: Y(a), y2: Y(a),
                 stroke: "#E5E7EB", "stroke-width": 1 });
    el("text", { x: mL - 6, y: Y(a) + 4, "text-anchor": "end",
                 "font-size": 11, fill: "#6B7280" }, (a * 100).toFixed(0) + "%");
  }
  [0, 0.25, 0.5, 0.75, 1].forEach((c) => {
    el("text", { x: X(c), y: H - mB + 16, "text-anchor": "middle",
                 "font-size": 11, fill: "#6B7280" }, (c * 100) + "%");
  });
  el("text", { x: (mL + W - mR) / 2, y: H - 4, "text-anchor": "middle",
               "font-size": 11.5, fill: "#6B7280" },
     "coverage (share of reports auto-routed)");

  const pts = curve.map((r) => X(r.coverage) + "," + Y(r.auto_accuracy)).join(" ");
  el("polyline", { points: pts, fill: "none", stroke: "#2563EB",
                   "stroke-width": 2.5, "stroke-linejoin": "round" });

  el("circle", { cx: X(op.coverage), cy: Y(op.auto_accuracy), r: 5,
                 fill: "#fff", stroke: "#b3762e", "stroke-width": 2.5 });
  el("text", { x: X(op.coverage), y: Y(op.auto_accuracy) - 10,
               "text-anchor": "middle", "font-size": 11, "font-weight": 700,
               fill: "#b3762e" }, "deployed: 80% / 98.4%");

  const marker = el("circle", { cx: 0, cy: 0, r: 4.5, fill: "#2563EB" });
  const vline = el("line", { y1: mT, y2: H - mB, stroke: "#2563EB",
                             "stroke-width": 1, "stroke-dasharray": "3 3" });

  const slider = $("defslider");
  slider.max = String(curve.length - 1);
  const update = () => {
    const r = curve[Number(slider.value)];
    marker.setAttribute("cx", X(r.coverage));
    marker.setAttribute("cy", Y(r.auto_accuracy));
    vline.setAttribute("x1", X(r.coverage));
    vline.setAttribute("x2", X(r.coverage));
    $("defreadout").innerHTML =
      "coverage <b>" + (r.coverage * 100).toFixed(0) + "%</b> &rarr; auto-routed accuracy <b>"
      + (r.auto_accuracy * 100).toFixed(2) + "%</b>, confidence threshold "
      + r.threshold.toFixed(3);
  };
  slider.addEventListener("input", update);
  const idx = curve.findIndex((r) => Math.abs(r.coverage - op.coverage) < 1e-6);
  slider.value = String(idx >= 0 ? idx : Math.floor(curve.length * 0.8));
  update();
}

/* ---------- boot ---------- */

Promise.all([
  fetch("data/examples.json").then((r) => r.json()),
  fetch("data/districts.geojson").then((r) => r.json()),
  fetch("data/provinces.geojson").then((r) => r.json()),
  fetch("data/results.json").then((r) => r.json()),
]).then(([examples, districts, provinces, results]) => {
  state.data = examples;
  state.data._districtsGeo = districts;
  state.sel = key(examples.examples[0].districts[0]);

  $("btn-m1").onclick = () => { state.mode = "m1"; syncAll(); };
  $("btn-t0").onclick = () => { state.mode = "t0"; syncAll(); };

  initMap(districts);
  syncAll();
  initChoropleth(provinces, results);
  initDeferral(results);
}).catch((err) => {
  document.querySelector("#demo .section-lede").textContent =
    "Failed to load demo data (" + err + "). If you opened this file directly, "
    + "serve the docs/ directory instead: python -m http.server";
});
