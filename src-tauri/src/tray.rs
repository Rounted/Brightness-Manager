use std::collections::HashMap;
use std::sync::OnceLock;

use tauri::{
    AppHandle, Emitter, Manager,
    menu::{Menu, MenuItem, Submenu},
    tray::TrayIconEvent,
};

use crate::config::{self, AppState};
use crate::overlay;

type Translations = HashMap<&'static str, HashMap<&'static str, &'static str>>;

static STRINGS: OnceLock<Translations> = OnceLock::new();

fn strings() -> &'static Translations {
    STRINGS.get_or_init(|| {
        let mut m: Translations = HashMap::new();
        let keys: &[(&str, &[(&str, &str)])] = &[
            ("disable_filter", &[
                ("en", "Disable Filter"), ("tr", "Filtreyi Kapat"), ("de", "Filter Deaktivieren"),
                ("fr", "Désactiver le Filtre"), ("es", "Desactivar Filtro"), ("it", "Disattiva Filtro"),
                ("pt", "Desativar Filtro"), ("ru", "Выключить Фильтр"), ("ja", "フィルター無効化"),
                ("ko", "필터 비활성화"), ("zh", "关闭滤镜"), ("ar", "تعطيل الفلتر"),
                ("hi", "फ़िल्टर बंद करें"), ("nl", "Filter Uitschakelen"), ("pl", "Wyłącz Filtr"),
            ]),
            ("enable_filter", &[
                ("en", "Enable Filter"), ("tr", "Filtreyi Aç"), ("de", "Filter Aktivieren"),
                ("fr", "Activer le Filtre"), ("es", "Activar Filtro"), ("it", "Attiva Filtro"),
                ("pt", "Ativar Filtro"), ("ru", "Включить Фильтр"), ("ja", "フィルター有効化"),
                ("ko", "필터 활성화"), ("zh", "开启滤镜"), ("ar", "تفعيل الفلتر"),
                ("hi", "फ़िल्टर चालू करें"), ("nl", "Filter Inschakelen"), ("pl", "Włącz Filtr"),
            ]),
            ("modes", &[
                ("en", "Modes"), ("tr", "Modlar"), ("de", "Modi"),
                ("fr", "Modes"), ("es", "Modos"), ("it", "Modalità"),
                ("pt", "Modos"), ("ru", "Режимы"), ("ja", "モード"),
                ("ko", "모드"), ("zh", "模式"), ("ar", "الأوضاع"),
                ("hi", "मोड"), ("nl", "Modi"), ("pl", "Tryby"),
            ]),
            ("settings", &[
                ("en", "Settings"), ("tr", "Ayarlar"), ("de", "Einstellungen"),
                ("fr", "Paramètres"), ("es", "Ajustes"), ("it", "Impostazioni"),
                ("pt", "Configurações"), ("ru", "Настройки"), ("ja", "設定"),
                ("ko", "설정"), ("zh", "设置"), ("ar", "الإعدادات"),
                ("hi", "सेटिंग्स"), ("nl", "Instellingen"), ("pl", "Ustawienia"),
            ]),
            ("quit", &[
                ("en", "Quit"), ("tr", "Çıkış"), ("de", "Beenden"),
                ("fr", "Quitter"), ("es", "Salir"), ("it", "Esci"),
                ("pt", "Sair"), ("ru", "Выход"), ("ja", "終了"),
                ("ko", "종료"), ("zh", "退出"), ("ar", "خروج"),
                ("hi", "बाहर निकलें"), ("nl", "Afsluiten"), ("pl", "Zamknij"),
            ]),
            ("preset_day", &[
                ("en", "Day"), ("tr", "Gündüz"), ("de", "Tag"),
                ("fr", "Jour"), ("es", "Día"), ("it", "Giorno"),
                ("pt", "Dia"), ("ru", "День"), ("ja", "昼間"),
                ("ko", "낮"), ("zh", "白天"), ("ar", "نهار"),
                ("hi", "दिन"), ("nl", "Dag"), ("pl", "Dzień"),
            ]),
            ("preset_office", &[
                ("en", "Office"), ("tr", "Ofis"), ("de", "Büro"),
                ("fr", "Bureau"), ("es", "Oficina"), ("it", "Ufficio"),
                ("pt", "Escritório"), ("ru", "Офис"), ("ja", "オフィス"),
                ("ko", "사무실"), ("zh", "办公"), ("ar", "مكتب"),
                ("hi", "कार्यालय"), ("nl", "Kantoor"), ("pl", "Biuro"),
            ]),
            ("preset_night", &[
                ("en", "Night"), ("tr", "Gece"), ("de", "Nacht"),
                ("fr", "Nuit"), ("es", "Noche"), ("it", "Notte"),
                ("pt", "Noite"), ("ru", "Ночь"), ("ja", "夜間"),
                ("ko", "밤"), ("zh", "夜间"), ("ar", "ليل"),
                ("hi", "रात"), ("nl", "Nacht"), ("pl", "Noc"),
            ]),
            ("preset_reading", &[
                ("en", "Reading"), ("tr", "Okuma"), ("de", "Lesen"),
                ("fr", "Lecture"), ("es", "Lectura"), ("it", "Lettura"),
                ("pt", "Leitura"), ("ru", "Чтение"), ("ja", "読書"),
                ("ko", "독서"), ("zh", "阅读"), ("ar", "قراءة"),
                ("hi", "पठन"), ("nl", "Lezen"), ("pl", "Czytanie"),
            ]),
            ("preset_movie", &[
                ("en", "Movie"), ("tr", "Film"), ("de", "Film"),
                ("fr", "Film"), ("es", "Película"), ("it", "Film"),
                ("pt", "Filme"), ("ru", "Кино"), ("ja", "映画"),
                ("ko", "영화"), ("zh", "电影"), ("ar", "فيلم"),
                ("hi", "फ़िल्म"), ("nl", "Film"), ("pl", "Film"),
            ]),
        ];
        for (key, translations) in keys {
            let mut lang_map = HashMap::new();
            for (lang, text) in *translations {
                lang_map.insert(*lang, *text);
            }
            m.insert(*key, lang_map);
        }
        m
    })
}

fn t(key: &str, lang: &str) -> String {
    strings()
        .get(key)
        .and_then(|m| m.get(lang).or_else(|| m.get("en")))
        .map(|s| (*s).to_string())
        .unwrap_or_else(|| key.to_string())
}

pub fn build_tray_menu(app: &AppHandle) -> tauri::Result<Menu<tauri::Wry>> {
    let state = app.state::<AppState>();
    let config = state.config.lock().unwrap();
    let lang = config.language.clone();
    let enabled = config.enabled;
    drop(config);

    let toggle_text = if enabled {
        t("disable_filter", &lang)
    } else {
        t("enable_filter", &lang)
    };

    let toggle_item = MenuItem::with_id(app, "toggle", &toggle_text, true, None::<&str>)?;

    let preset_day = MenuItem::with_id(app, "preset_day", t("preset_day", &lang), true, None::<&str>)?;
    let preset_office = MenuItem::with_id(app, "preset_office", t("preset_office", &lang), true, None::<&str>)?;
    let preset_night = MenuItem::with_id(app, "preset_night", t("preset_night", &lang), true, None::<&str>)?;
    let preset_reading = MenuItem::with_id(app, "preset_reading", t("preset_reading", &lang), true, None::<&str>)?;
    let preset_movie = MenuItem::with_id(app, "preset_movie", t("preset_movie", &lang), true, None::<&str>)?;

    let modes_sub = Submenu::with_items(
        app,
        t("modes", &lang),
        true,
        &[
            &preset_day,
            &preset_office,
            &preset_night,
            &preset_reading,
            &preset_movie,
        ],
    )?;

    let settings_item = MenuItem::with_id(app, "settings", t("settings", &lang), true, None::<&str>)?;
    let quit_item = MenuItem::with_id(app, "quit", t("quit", &lang), true, None::<&str>)?;

    let menu = Menu::with_items(
        app,
        &[
            &toggle_item,
            &modes_sub,
            &settings_item,
            &quit_item,
        ],
    )?;

    Ok(menu)
}

pub fn handle_tray_event(app: &AppHandle, event: TrayIconEvent) {
    if let TrayIconEvent::DoubleClick { button, .. } = event {
        if button == tauri::tray::MouseButton::Left {
            toggle_settings_window(app);
        }
    }
}

pub fn handle_menu_event(app: &AppHandle, event: tauri::menu::MenuEvent) {
    let id = event.id().0.as_str();
    match id {
        "toggle" => {
            let state = app.state::<AppState>();
            state.update_and_apply(app, |c| c.enabled = !c.enabled);
            let _ = rebuild_tray_menu(app);
            let _ = app.emit("config-changed", ());
        }
        "settings" => {
            toggle_settings_window(app);
        }
        "quit" => {
            overlay::hide_all_overlays(app);
            app.exit(0);
        }
        id if id.starts_with("preset_") => {
            let key = id.strip_prefix("preset_").unwrap_or("");
            if let Some(preset) = config::presets().get(key) {
                let b = preset.brightness;
                let t = preset.temperature;
                let state = app.state::<AppState>();
                state.update_and_apply(app, |c| {
                    c.brightness = b;
                    c.temperature = t;
                });
                let _ = app.emit("config-changed", ());
            }
        }
        _ => {}
    }
}

fn toggle_settings_window(app: &AppHandle) {
    if let Some(win) = app.get_webview_window("settings") {
        if win.is_visible().unwrap_or(false) {
            let _ = win.hide();
        } else {
            let _ = win.center();
            let _ = win.show();
            let _ = win.set_focus();
        }
    }
}

pub fn rebuild_tray_menu(app: &AppHandle) -> tauri::Result<()> {
    if let Some(tray) = app.tray_by_id("main-tray") {
        let menu = build_tray_menu(app)?;
        tray.set_menu(Some(menu))?;
    }
    Ok(())
}
