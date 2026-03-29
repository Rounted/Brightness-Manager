from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon

from config import Config, PRESETS
from gamma_controller import GammaController
from settings_window import SettingsWindow
from lang import t


class TrayApp:
    def __init__(self, icon_path):
        self.config = Config()
        self.gamma = GammaController()

        screen_infos = self.gamma.get_screen_info()
        self.settings_win = SettingsWindow(self.config, screen_infos)

        self.tray = QSystemTrayIcon(QIcon(icon_path))
        self.tray.setToolTip(self._tooltip())
        self.tray.activated.connect(self._on_tray_activated)

        self._build_menu()

        self.tray.setContextMenu(self.menu)

        # Connect settings window signals
        self.settings_win.brightness_changed.connect(self._on_value_changed)
        self.settings_win.temperature_changed.connect(self._on_value_changed)
        self.settings_win.toggled.connect(self._on_toggled_from_settings)
        self.settings_win.screens_changed.connect(self._on_screens_changed)
        self.settings_win.quit_requested.connect(self._quit)
        self.settings_win.language_changed.connect(self._on_language_changed)

        self._apply_current()
        self.tray.show()

    def _lang(self):
        return self.config.language

    def _t(self, key):
        return t(key, self._lang())

    def _build_menu(self):
        self.menu = QMenu()

        self.toggle_action = QAction(self._t("disable_filter"))
        self.toggle_action.triggered.connect(self._toggle)
        self.menu.addAction(self.toggle_action)

        self.presets_menu = self.menu.addMenu(self._t("modes"))
        for key in PRESETS:
            action = QAction(self._t(f"preset_{key}"), self.presets_menu)
            action.triggered.connect(lambda checked, k=key: self._apply_preset(k))
            self.presets_menu.addAction(action)

        self.menu.addSeparator()

        self.settings_action = QAction(self._t("settings"))
        self.settings_action.triggered.connect(self._show_settings)
        self.menu.addAction(self.settings_action)

        self.menu.addSeparator()

        self.quit_action = QAction(self._t("quit"))
        self.quit_action.triggered.connect(self._quit)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)

    def _tooltip(self):
        state = self._t("active") if self.config.enabled else self._t("passive")
        screens = self.config.screens
        s_str = ", ".join(str(s + 1) for s in screens) if screens else self._t("all")
        bri = self._t("brightness")
        temp = self._t("temperature")
        scr = self._t("screens")
        return (f"Brightness App [{state}]\n"
                f"{bri}: {self.config.brightness}%  {temp}: {self.config.temperature}K\n"
                f"{scr}: {s_str}")

    def _get_screen_indices(self):
        screens = self.config.screens
        return screens if screens else None

    def _apply_current(self):
        if self.config.enabled:
            self.gamma.apply(
                self.config.brightness,
                self.config.temperature,
                self._get_screen_indices(),
            )
        else:
            self.gamma.restore()
        self.tray.setToolTip(self._tooltip())
        self._sync_toggle_text()

    def _sync_toggle_text(self):
        self.toggle_action.setText(
            self._t("disable_filter") if self.config.enabled else self._t("enable_filter")
        )

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.settings_win.isVisible():
                self.settings_win.hide()
            else:
                self._show_settings()

    def _show_settings(self):
        self.settings_win.show()
        self.settings_win.activateWindow()

    def _toggle(self):
        self.config.enabled = not self.config.enabled
        self.settings_win.set_enabled(self.config.enabled)
        self._apply_current()

    def _on_toggled_from_settings(self, enabled):
        self._apply_current()

    def _on_value_changed(self, _value=None):
        self._apply_current()

    def _on_screens_changed(self, screens):
        self._apply_current()

    def _on_language_changed(self, lang):
        self._build_menu()
        self.tray.setToolTip(self._tooltip())

    def _apply_preset(self, key):
        preset = PRESETS[key]
        self.config.set_preset(preset["brightness"], preset["temperature"])
        self.settings_win.reload_config()
        self._apply_current()

    def _quit(self):
        self.gamma.restore()
        QApplication.quit()
