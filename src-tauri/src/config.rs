use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::sync::{Mutex, OnceLock};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub brightness: u32,
    pub temperature: u32,
    pub enabled: bool,
    pub screens: Vec<usize>,
    pub language: String,
    pub autostart: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            brightness: 100,
            temperature: 6500,
            enabled: true,
            screens: vec![],
            language: "en".into(),
            autostart: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Preset {
    pub brightness: u32,
    pub temperature: u32,
}

static PRESETS: OnceLock<HashMap<String, Preset>> = OnceLock::new();

pub fn presets() -> &'static HashMap<String, Preset> {
    PRESETS.get_or_init(|| {
        let mut m = HashMap::new();
        m.insert("day".into(), Preset { brightness: 100, temperature: 6500 });
        m.insert("office".into(), Preset { brightness: 85, temperature: 5500 });
        m.insert("night".into(), Preset { brightness: 70, temperature: 3400 });
        m.insert("reading".into(), Preset { brightness: 60, temperature: 4200 });
        m.insert("movie".into(), Preset { brightness: 80, temperature: 5000 });
        m
    })
}

static CONFIG_PATH: OnceLock<PathBuf> = OnceLock::new();

fn config_path() -> &'static PathBuf {
    CONFIG_PATH.get_or_init(|| {
        let home = dirs::home_dir().unwrap_or_else(|| PathBuf::from("."));
        home.join(".brightness_app").join("config.json")
    })
}

impl Config {
    pub fn load() -> Self {
        let path = config_path();
        if let Ok(data) = fs::read_to_string(path) {
            serde_json::from_str(&data).unwrap_or_default()
        } else {
            Config::default()
        }
    }

    pub fn save(&self) {
        let path = config_path();
        if let Some(parent) = path.parent() {
            let _ = fs::create_dir_all(parent);
        }
        if let Ok(json) = serde_json::to_string_pretty(self) {
            let _ = fs::write(path, json);
        }
    }
}

pub struct AppState {
    pub config: Mutex<Config>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            config: Mutex::new(Config::load()),
        }
    }

    /// Lock config, apply mutation, save, and update overlays.
    pub fn update_and_apply(&self, app: &tauri::AppHandle, mutate: impl FnOnce(&mut Config)) {
        let mut config = self.config.lock().unwrap();
        mutate(&mut config);
        config.save();
        crate::overlay::update_overlays_from_config(app, &config);
    }
}
