const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;
const { getCurrentWindow } = window.__TAURI__.window;

let currentLang = "en";
let monitors = [];

const PRESETS = {
  day: { brightness: 100, temperature: 6500 },
  office: { brightness: 85, temperature: 5500 },
  night: { brightness: 70, temperature: 3400 },
  reading: { brightness: 60, temperature: 4200 },
  movie: { brightness: 80, temperature: 5000 },
};

// Cache all DOM refs upfront
const $brightnessSlider = document.getElementById("slider-brightness");
const $temperatureSlider = document.getElementById("slider-temperature");
const $brightnessVal = document.getElementById("val-brightness");
const $temperatureVal = document.getElementById("val-temperature");
const $switchFilter = document.getElementById("switch-filter");
const $switchStartup = document.getElementById("switch-startup");
const $lblFilter = document.getElementById("lbl-filter");
const $screensRow = document.getElementById("screens-row");
const $langSelect = document.getElementById("lang-select");
const $lblScreens = document.getElementById("lbl-screens");
const $lblBrightness = document.getElementById("lbl-brightness");
const $lblTemperature = document.getElementById("lbl-temperature");
const $lblPresets = document.getElementById("lbl-presets");
const $lblStartup = document.getElementById("lbl-startup");
const $btnQuitText = document.getElementById("btn-quit-text");
const $presetDay = document.getElementById("preset-day");
const $presetOffice = document.getElementById("preset-office");
const $presetNight = document.getElementById("preset-night");
const $presetReading = document.getElementById("preset-reading");
const $presetMovie = document.getElementById("preset-movie");
const $presetPills = document.querySelectorAll(".preset-pill");

// Throttle helper: fires at most once per animation frame
function throttleRAF(fn) {
  let pending = false;
  let lastArgs;
  return function (...args) {
    lastArgs = args;
    if (!pending) {
      pending = true;
      requestAnimationFrame(() => {
        pending = false;
        fn(...lastArgs);
      });
    }
  };
}

// Build language dropdown
function buildLangSelect() {
  $langSelect.innerHTML = "";
  for (const [code, name] of Object.entries(window.LANG.LANG_NAMES)) {
    const opt = document.createElement("option");
    opt.value = code;
    opt.textContent = name;
    $langSelect.appendChild(opt);
  }
  $langSelect.value = currentLang;
}

// Slider gradient
function updateSliderGradient(slider, colors) {
  const min = parseFloat(slider.min);
  const max = parseFloat(slider.max);
  const val = parseFloat(slider.value);
  const pct = ((val - min) / (max - min)) * 100;
  const n = colors.length;
  const stops = colors.map((c, i) => `${c} ${(i / (n - 1)) * pct}%`);
  stops.push(`#ededf0 ${pct}%`);
  stops.push(`#ededf0 100%`);
  slider.style.background = `linear-gradient(to right, ${stops.join(", ")})`;
}

function updateBrightnessGradient() {
  updateSliderGradient($brightnessSlider, ["#ff6b00", "#ff9f0a", "#ffcc00"]);
}
function updateTemperatureGradient() {
  updateSliderGradient($temperatureSlider, ["#ff6b6b", "#ff9f0a", "#64d2ff"]);
}

// Detect active preset (uses cached NodeList)
function detectPreset() {
  const b = parseInt($brightnessSlider.value);
  const t = parseInt($temperatureSlider.value);
  $presetPills.forEach((pill) => {
    const key = pill.dataset.preset;
    const p = PRESETS[key];
    pill.classList.toggle("active", p.brightness === b && p.temperature === t);
  });
}

// Throttled backend calls for sliders
const invokeBrightness = throttleRAF((v) => invoke("set_brightness", { value: v }));
const invokeTemperature = throttleRAF((v) => invoke("set_temperature", { value: v }));

// Brightness slider
$brightnessSlider.addEventListener("input", () => {
  const v = parseInt($brightnessSlider.value);
  $brightnessVal.textContent = `${v}%`;
  updateBrightnessGradient();
  detectPreset();
  invokeBrightness(v);
});

// Temperature slider
$temperatureSlider.addEventListener("input", () => {
  const v = parseInt($temperatureSlider.value);
  $temperatureVal.textContent = `${v}K`;
  updateTemperatureGradient();
  detectPreset();
  invokeTemperature(v);
});

// Presets
$presetPills.forEach((pill) => {
  pill.addEventListener("click", () => {
    const key = pill.dataset.preset;
    const p = PRESETS[key];
    $brightnessSlider.value = p.brightness;
    $temperatureSlider.value = p.temperature;
    $brightnessVal.textContent = `${p.brightness}%`;
    $temperatureVal.textContent = `${p.temperature}K`;
    updateBrightnessGradient();
    updateTemperatureGradient();
    detectPreset();
    invoke("apply_preset", { key });
  });
});

// Toggle switch helper
function setupSwitch(el, initialState, onChange) {
  if (initialState) el.classList.add("on");
  else el.classList.remove("on");
  el.addEventListener("click", () => {
    const isOn = el.classList.toggle("on");
    onChange(isOn);
  });
}

// Filter toggle
setupSwitch($switchFilter, true, (on) => {
  $lblFilter.textContent = window.LANG.t(on ? "filter_on" : "filter_off", currentLang);
  invoke("toggle_filter", { enabled: on });
});

// Startup toggle
setupSwitch($switchStartup, false, (on) => {
  invoke("set_autostart", { enabled: on });
});

// Close button
document.getElementById("btn-close").addEventListener("click", () => {
  getCurrentWindow().hide();
});

// Quit button
document.getElementById("btn-quit").addEventListener("click", () => {
  invoke("quit_app");
});

// Language dropdown
$langSelect.addEventListener("change", () => {
  setLanguage($langSelect.value);
});

function setLanguage(lang) {
  if (lang === currentLang) return;
  currentLang = lang;
  $langSelect.value = lang;
  refreshTexts();
  invoke("set_language", { lang });
}

function refreshTexts() {
  const T = (k) => window.LANG.t(k, currentLang);
  $lblScreens.textContent = T("screens");
  $lblBrightness.textContent = T("brightness");
  $lblTemperature.textContent = T("temperature");
  $lblPresets.textContent = T("presets");
  $lblStartup.textContent = T("startup");
  $btnQuitText.textContent = T("quit");

  const filterOn = $switchFilter.classList.contains("on");
  $lblFilter.textContent = T(filterOn ? "filter_on" : "filter_off");

  $presetDay.textContent = T("preset_day");
  $presetOffice.textContent = T("preset_office");
  $presetNight.textContent = T("preset_night");
  $presetReading.textContent = T("preset_reading");
  $presetMovie.textContent = T("preset_movie");
}

// Build screen buttons
function buildScreenButtons(monitorList) {
  monitors = monitorList;
  $screensRow.innerHTML = "";
  monitors.forEach((mon) => {
    const btn = document.createElement("button");
    btn.className = "screen-btn selected";
    btn.dataset.index = mon.index;
    btn.innerHTML = `
      <div class="screen-body">${mon.index + 1}${mon.primary ? "*" : ""}</div>
      <div class="screen-stand"></div>
      <div class="screen-base"></div>
      <div class="screen-res">${mon.width}x${mon.height}</div>
    `;
    btn.addEventListener("click", () => {
      btn.classList.toggle("selected");
      updateSelectedScreens();
    });
    $screensRow.appendChild(btn);
  });
}

function updateSelectedScreens() {
  const selected = [];
  document.querySelectorAll(".screen-btn").forEach((btn) => {
    if (btn.classList.contains("selected")) {
      selected.push(parseInt(btn.dataset.index));
    }
  });
  const indices = selected.length === monitors.length ? [] : selected;
  invoke("set_screens", { indices });
}

function applyScreenSelection(screens) {
  document.querySelectorAll(".screen-btn").forEach((btn) => {
    const idx = parseInt(btn.dataset.index);
    btn.classList.toggle("selected", screens.length === 0 || screens.includes(idx));
  });
}

// Apply config to UI
function applyConfig(config) {
  currentLang = config.language || "en";
  $langSelect.value = currentLang;

  $brightnessSlider.value = config.brightness;
  $brightnessVal.textContent = `${config.brightness}%`;
  updateBrightnessGradient();

  $temperatureSlider.value = config.temperature;
  $temperatureVal.textContent = `${config.temperature}K`;
  updateTemperatureGradient();

  detectPreset();

  if (config.enabled) $switchFilter.classList.add("on");
  else $switchFilter.classList.remove("on");

  if (config.autostart) $switchStartup.classList.add("on");
  else $switchStartup.classList.remove("on");

  applyScreenSelection(config.screens || []);
  refreshTexts();
}

// Init
async function init() {
  buildLangSelect();
  try {
    const [config, monitorList] = await Promise.all([
      invoke("get_config"),
      invoke("get_monitors"),
    ]);
    buildScreenButtons(monitorList);
    applyConfig(config);
  } catch (e) {
    console.error("Init error:", e);
  }
}

// Listen for config changes from tray
listen("config-changed", async () => {
  try {
    const config = await invoke("get_config");
    applyConfig(config);
  } catch (e) {
    console.error("Config change error:", e);
  }
});

document.addEventListener("DOMContentLoaded", init);
