use tauri::{AppHandle, Emitter, Manager, WebviewUrl, WebviewWindowBuilder};

const MAX_MONITORS: usize = 16;

#[derive(Debug, Clone, serde::Serialize)]
pub struct OverlayColor {
    pub r: u8,
    pub g: u8,
    pub b: u8,
    pub a: u8,
}

pub fn calculate_overlay_color(brightness: u32, temperature: u32) -> OverlayColor {
    let brightness = brightness.clamp(10, 100);
    let temperature = temperature.clamp(1000, 6500);

    let dark_alpha = (1.0 - brightness as f64 / 100.0) * 200.0;
    let temp_factor = 1.0 - (temperature as f64 - 1000.0) / 5500.0;
    let tint_alpha = temp_factor * 80.0;
    let total_alpha = (dark_alpha + tint_alpha).min(220.0) as u8;

    let tint_r = (40.0 * temp_factor) as u8;
    let tint_g = (20.0 * temp_factor) as u8;

    OverlayColor {
        r: tint_r,
        g: tint_g,
        b: 0,
        a: total_alpha,
    }
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct MonitorInfo {
    pub index: usize,
    pub width: u32,
    pub height: u32,
    pub x: i32,
    pub y: i32,
    pub primary: bool,
}

pub fn get_monitors(app: &AppHandle) -> Vec<MonitorInfo> {
    let monitors: Vec<_> = app.available_monitors().unwrap_or_default();
    let primary = app.primary_monitor().ok().flatten();
    let primary_name = primary.as_ref().map(|m| m.name().map(|s| s.to_string())).flatten();

    monitors
        .iter()
        .enumerate()
        .map(|(i, m)| {
            let size = m.size();
            let pos = m.position();
            let is_primary = primary_name
                .as_ref()
                .map(|pn| m.name().map(|n| n == pn.as_str()).unwrap_or(false))
                .unwrap_or(i == 0);
            MonitorInfo {
                index: i,
                width: size.width,
                height: size.height,
                x: pos.x,
                y: pos.y,
                primary: is_primary,
            }
        })
        .collect()
}

pub fn create_overlay_windows(app: &AppHandle) {
    let raw_monitors: Vec<_> = app.available_monitors().unwrap_or_default();

    for (i, raw_mon) in raw_monitors.iter().enumerate() {
        let label = format!("overlay-{}", i);
        if app.get_webview_window(&label).is_some() {
            continue;
        }
        let scale = raw_mon.scale_factor();
        let size = raw_mon.size();
        let pos = raw_mon.position();

        let width = size.width as f64 / scale;
        let height = size.height as f64 / scale;
        let x = pos.x as f64 / scale;
        let y = pos.y as f64 / scale;

        if let Ok(win) = WebviewWindowBuilder::new(app, &label, WebviewUrl::App("overlay.html".into()))
            .title("Overlay")
            .inner_size(width, height)
            .position(x, y)
            .decorations(false)
            .transparent(true)
            .always_on_top(true)
            .skip_taskbar(true)
            .visible(false)
            .build()
        {
            let _ = win.set_ignore_cursor_events(true);
            // Set Win32 flags for click-through
            #[cfg(target_os = "windows")]
            {
                use windows::Win32::Foundation::HWND;
                use windows::Win32::UI::WindowsAndMessaging::*;
                if let Ok(raw_hwnd) = win.hwnd() {
                    let hwnd = HWND(raw_hwnd.0 as *mut std::ffi::c_void);
                    unsafe {
                        let ex_style = GetWindowLongW(hwnd, GWL_EXSTYLE);
                        SetWindowLongW(
                            hwnd,
                            GWL_EXSTYLE,
                            ex_style
                                | WS_EX_TOOLWINDOW.0 as i32
                                | WS_EX_NOACTIVATE.0 as i32,
                        );
                    }
                }
            }
        }
    }
}

pub fn update_overlays_from_config(app: &AppHandle, config: &crate::config::Config) {
    update_overlays(app, config.brightness, config.temperature, config.enabled, &config.screens);
}

pub fn update_overlays(app: &AppHandle, brightness: u32, temperature: u32, enabled: bool, screens: &[usize]) {
    let color = calculate_overlay_color(brightness, temperature);

    // Iterate over overlay windows by index instead of querying OS monitors
    for i in 0..MAX_MONITORS {
        let label = format!("overlay-{}", i);
        let Some(win) = app.get_webview_window(&label) else { break };
        let should_show = enabled && (screens.is_empty() || screens.contains(&i));

        if should_show {
            let _ = win.emit("set-overlay-color", &color);
            let _ = win.show();
        } else {
            let _ = win.hide();
        }
    }
}

pub fn hide_all_overlays(app: &AppHandle) {
    for i in 0..MAX_MONITORS {
        let label = format!("overlay-{}", i);
        let Some(win) = app.get_webview_window(&label) else { break };
        let _ = win.hide();
    }
}
