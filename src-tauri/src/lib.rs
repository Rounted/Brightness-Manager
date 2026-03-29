mod config;
mod overlay;
mod tray;

use config::{AppState, Config};
use overlay::MonitorInfo;
use tauri::Manager;
use tauri_plugin_autostart::ManagerExt;

#[tauri::command]
fn get_config(state: tauri::State<'_, AppState>) -> Config {
    state.config.lock().unwrap().clone()
}

#[tauri::command]
fn set_brightness(value: u32, app: tauri::AppHandle, state: tauri::State<'_, AppState>) {
    state.update_and_apply(&app, |c| c.brightness = value.clamp(10, 100));
}

#[tauri::command]
fn set_temperature(value: u32, app: tauri::AppHandle, state: tauri::State<'_, AppState>) {
    state.update_and_apply(&app, |c| c.temperature = value.clamp(1000, 6500));
}

#[tauri::command]
fn toggle_filter(enabled: bool, app: tauri::AppHandle, state: tauri::State<'_, AppState>) {
    state.update_and_apply(&app, |c| c.enabled = enabled);
    let _ = tray::rebuild_tray_menu(&app);
}

#[tauri::command]
fn apply_preset(key: String, app: tauri::AppHandle, state: tauri::State<'_, AppState>) {
    if let Some(preset) = config::presets().get(&key) {
        let b = preset.brightness;
        let t = preset.temperature;
        state.update_and_apply(&app, |c| {
            c.brightness = b;
            c.temperature = t;
        });
    }
}

#[tauri::command]
fn set_screens(indices: Vec<usize>, app: tauri::AppHandle, state: tauri::State<'_, AppState>) {
    state.update_and_apply(&app, |c| c.screens = indices);
}

#[tauri::command]
fn set_language(lang: String, app: tauri::AppHandle, state: tauri::State<'_, AppState>) {
    {
        let mut config = state.config.lock().unwrap();
        config.language = lang;
        config.save();
    }
    let _ = tray::rebuild_tray_menu(&app);
}

#[tauri::command]
fn set_autostart(enabled: bool, app: tauri::AppHandle) {
    let autostart = app.autolaunch();
    if enabled {
        let _ = autostart.enable();
    } else {
        let _ = autostart.disable();
    }
}

#[tauri::command]
fn get_monitors(app: tauri::AppHandle) -> Vec<MonitorInfo> {
    overlay::get_monitors(&app)
}

#[tauri::command]
fn quit_app(app: tauri::AppHandle) {
    overlay::hide_all_overlays(&app);
    app.exit(0);
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            None,
        ))
        .manage(AppState::new())
        .invoke_handler(tauri::generate_handler![
            get_config,
            set_brightness,
            set_temperature,
            toggle_filter,
            apply_preset,
            set_screens,
            set_language,
            set_autostart,
            get_monitors,
            quit_app,
        ])
        .setup(|app| {
            // Create overlay windows
            overlay::create_overlay_windows(app.handle());

            // Tray: right-click menu + double-click to open settings
            if let Some(tray) = app.tray_by_id("main-tray") {
                let menu = tray::build_tray_menu(app.handle())?;
                tray.set_menu(Some(menu))?;
                tray.set_show_menu_on_left_click(false)?;

                let handle = app.handle().clone();
                tray.on_tray_icon_event(move |_tray, event| {
                    tray::handle_tray_event(&handle, event);
                });

                let handle2 = app.handle().clone();
                tray.on_menu_event(move |_app, event| {
                    tray::handle_menu_event(&handle2, event);
                });
            }

            // Apply initial overlay state
            let state = app.state::<AppState>();
            let config = state.config.lock().unwrap();
            overlay::update_overlays_from_config(app.handle(), &config);

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
