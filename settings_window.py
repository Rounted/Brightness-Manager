from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton,
    QGraphicsDropShadowEffect, QApplication, QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import (
    QColor, QFont, QPainter, QLinearGradient, QPainterPath, QBrush, QPen,
)

from config import PRESETS, PRESET_ICONS
from lang import t

ICON_SUN = "\u2600"
ICON_TEMP = "\u2668"


class AnimatedToggle(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(52, 28)
        self.setCursor(Qt.PointingHandCursor)
        self._checked = True
        self._circle_x = 26.0
        self._anim = QPropertyAnimation(self, b"circle_x")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

    def isChecked(self):
        return self._checked

    def setChecked(self, val):
        self._checked = val
        self._circle_x = 26.0 if val else 4.0
        self.update()

    def _get_circle_x(self):
        return self._circle_x

    def _set_circle_x(self, val):
        self._circle_x = val
        self.update()

    from PyQt5.QtCore import pyqtProperty
    circle_x = pyqtProperty(float, _get_circle_x, _set_circle_x)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._anim.setStartValue(self._circle_x)
        self._anim.setEndValue(26.0 if self._checked else 4.0)
        self._anim.start()
        self.toggled.emit(self._checked)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        track_color = QColor("#4cd964") if self._checked else QColor("#48484a")
        p.setBrush(QBrush(track_color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(0, 0, 52, 28), 14, 14)
        p.setBrush(QBrush(QColor("#ffffff")))
        p.setPen(QPen(QColor(0, 0, 0, 40), 0.5))
        p.drawEllipse(QRectF(self._circle_x, 2, 22, 22))
        p.end()


class ModernSlider(QSlider):
    def __init__(self, orientation, gradient_colors=None, parent=None):
        super().__init__(orientation, parent)
        self._colors = gradient_colors or ["#ff9500", "#ffcc00"]
        self.setFixedHeight(36)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        track_y, track_h, handle_r = h / 2 - 3, 6, 10
        ratio = (self.value() - self.minimum()) / max(1, self.maximum() - self.minimum())
        handle_x = handle_r + ratio * (w - 2 * handle_r)

        p.setBrush(QBrush(QColor("#2c2c2e")))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(0, track_y, w, track_h), 3, 3)

        if handle_x > 0:
            grad = QLinearGradient(0, 0, handle_x, 0)
            for i, c in enumerate(self._colors):
                grad.setColorAt(i / max(1, len(self._colors) - 1), QColor(c))
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(QRectF(0, track_y, handle_x, track_h), 3, 3)

        glow = QColor(self._colors[-1])
        glow.setAlpha(50)
        p.setBrush(QBrush(glow))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QRectF(handle_x - handle_r - 3, h / 2 - handle_r - 3,
                              (handle_r + 3) * 2, (handle_r + 3) * 2))

        hg = QLinearGradient(handle_x, h / 2 - handle_r, handle_x, h / 2 + handle_r)
        hg.setColorAt(0, QColor("#ffffff"))
        hg.setColorAt(1, QColor("#e0e0e0"))
        p.setBrush(QBrush(hg))
        p.setPen(QPen(QColor(0, 0, 0, 30), 1))
        p.drawEllipse(QRectF(handle_x - handle_r, h / 2 - handle_r,
                              handle_r * 2, handle_r * 2))
        p.end()


class PresetCard(QPushButton):
    def __init__(self, name, icon_char, parent=None):
        super().__init__(parent)
        self._name = name
        self._icon = icon_char
        self._active = False
        self.setFixedSize(64, 68)
        self.setCursor(Qt.PointingHandCursor)

    def set_active(self, val):
        self._active = val
        self.update()

    def set_name(self, name):
        self._name = name
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        r = QRectF(1, 1, self.width() - 2, self.height() - 2)
        if self._active:
            grad = QLinearGradient(0, 0, 0, self.height())
            grad.setColorAt(0, QColor("#ff9f0a"))
            grad.setColorAt(1, QColor("#ff6b00"))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            text_color = QColor("#ffffff")
        else:
            p.setBrush(QBrush(QColor("#2c2c2e")))
            p.setPen(QPen(QColor("#3a3a3c"), 1))
            text_color = QColor("#98989d")
        path = QPainterPath()
        path.addRoundedRect(r, 14, 14)
        p.drawPath(path)

        p.setPen(text_color)
        f1 = QFont("Segoe UI Symbol", 16)
        f1.setStyleStrategy(QFont.PreferAntialias)
        p.setFont(f1)
        p.drawText(QRectF(0, 4, self.width(), 36), Qt.AlignHCenter | Qt.AlignBottom, self._icon)

        f2 = QFont("Segoe UI", 8, QFont.Bold)
        f2.setStyleStrategy(QFont.PreferAntialias)
        p.setFont(f2)
        p.drawText(QRectF(0, 42, self.width(), 20), Qt.AlignHCenter | Qt.AlignTop, self._name)
        p.end()


class ScreenButton(QPushButton):
    screen_toggled = pyqtSignal(int, bool)

    def __init__(self, index, info, parent=None):
        super().__init__(parent)
        self._index = index
        self._info = info
        self._selected = True
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._on_click)
        self.setFixedSize(90, 72)

    @property
    def is_selected(self):
        return self._selected

    def set_selected(self, val):
        self._selected = val
        self.update()

    def _on_click(self):
        self._selected = not self._selected
        self.update()
        self.screen_toggled.emit(self._index, self._selected)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        w, h = self.width(), self.height()

        body = QRectF(8, 4, w - 16, h - 26)
        path = QPainterPath()
        path.addRoundedRect(body, 4, 4)

        if self._selected:
            grad = QLinearGradient(0, body.top(), 0, body.bottom())
            grad.setColorAt(0, QColor("#0a84ff"))
            grad.setColorAt(1, QColor("#0064d2"))
            p.fillPath(path, QBrush(grad))
            p.setPen(QPen(QColor("#409cff"), 1.5))
            text_color = QColor("#ffffff")
        else:
            p.fillPath(path, QBrush(QColor("#2c2c2e")))
            p.setPen(QPen(QColor("#48484a"), 1))
            text_color = QColor("#636366")
        p.drawPath(path)

        cx = w / 2
        p.setPen(Qt.NoPen)
        sc = QColor("#409cff") if self._selected else QColor("#48484a")
        p.setBrush(QBrush(sc))
        p.drawRect(QRectF(cx - 5, body.bottom(), 10, 5))
        p.drawRoundedRect(QRectF(cx - 12, body.bottom() + 4, 24, 4), 2, 2)

        p.setPen(text_color)
        nf = QFont("Segoe UI", 10, QFont.Bold)
        nf.setStyleStrategy(QFont.PreferAntialias)
        p.setFont(nf)
        label = str(self._index + 1)
        if self._info.get("primary"):
            label += "*"
        p.drawText(body, Qt.AlignCenter, label)

        p.setPen(QColor("#636366"))
        rf = QFont("Segoe UI", 7)
        rf.setStyleStrategy(QFont.PreferAntialias)
        p.setFont(rf)
        p.drawText(QRectF(0, body.bottom() + 10, w, 14), Qt.AlignHCenter | Qt.AlignTop,
                   f"{self._info['width']}x{self._info['height']}")
        p.end()


class LangButton(QPushButton):
    """Small language toggle button with custom paint."""
    def __init__(self, code, label, active=False, parent=None):
        super().__init__(parent)
        self._code = code
        self._label = label
        self._active = active
        self.setFixedSize(36, 24)
        self.setCursor(Qt.PointingHandCursor)

    def set_active(self, val):
        self._active = val
        self.repaint()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        r = QRectF(0, 0, self.width(), self.height())

        if self._active:
            p.setBrush(QBrush(QColor("#0a84ff")))
            text_color = QColor("#ffffff")
        elif self.underMouse():
            p.setBrush(QBrush(QColor("#3a3a3c")))
            text_color = QColor("#98989d")
        else:
            p.setBrush(QBrush(QColor("#2c2c2e")))
            text_color = QColor("#636366")

        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, 6, 6)

        p.setPen(text_color)
        f = QFont("Segoe UI", 9, QFont.Bold)
        f.setStyleStrategy(QFont.PreferAntialias)
        p.setFont(f)
        p.drawText(r, Qt.AlignCenter, self._label)
        p.end()


class SettingsWindow(QWidget):
    brightness_changed = pyqtSignal(int)
    temperature_changed = pyqtSignal(int)
    toggled = pyqtSignal(bool)
    screens_changed = pyqtSignal(list)
    quit_requested = pyqtSignal()
    language_changed = pyqtSignal(str)

    def __init__(self, config, screen_infos):
        super().__init__()
        self.config = config
        self._screen_infos = screen_infos
        self._lang = config.language
        self._preset_cards = {}
        self._screen_buttons = {}
        self._drag_pos = None
        self._labels = {}
        self._init_ui()
        self.reload_config()

    def _t(self, key):
        return t(key, self._lang)

    def _init_ui(self):
        self.setWindowTitle("Brightness App")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 660)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        self._container = QWidget()
        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(0)
        outer.addWidget(self._container)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 8)
        self._container.setGraphicsEffect(shadow)

        # ---- Title bar ----
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        for c in ["#ff5f57", "#febc2e", "#28c840"]:
            title_row.addWidget(self._dot(c))
        title_row.addSpacing(12)
        title = QLabel("Brightness App")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet("color: #f5f5f7;")
        title_row.addWidget(title)
        title_row.addStretch()

        # Language toggle
        self._lang_tr = LangButton("tr", "TR", self._lang == "tr")
        self._lang_en = LangButton("en", "EN", self._lang == "en")
        self._lang_tr.clicked.connect(lambda: self._set_language("tr"))
        self._lang_en.clicked.connect(lambda: self._set_language("en"))
        title_row.addWidget(self._lang_tr)
        title_row.addWidget(self._lang_en)
        title_row.addSpacing(6)

        close_btn = QPushButton()
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("QPushButton { background: transparent; border: none; border-radius: 15px; }"
                                "QPushButton:hover { background: #ff453a; }")
        close_btn.clicked.connect(self.hide)
        close_btn.paintEvent = lambda e, btn=close_btn: self._paint_close_btn(btn)
        title_row.addWidget(close_btn)
        layout.addLayout(title_row)
        layout.addSpacing(16)

        # ---- Screens ----
        self._lbl_screens = self._section_label("screens")
        layout.addWidget(self._lbl_screens)
        layout.addSpacing(8)

        screen_row = QHBoxLayout()
        screen_row.setSpacing(12)
        for info in self._screen_infos:
            btn = ScreenButton(info["index"], info)
            btn.screen_toggled.connect(self._on_screen_toggled)
            screen_row.addWidget(btn)
            self._screen_buttons[info["index"]] = btn
        screen_row.addStretch()
        layout.addLayout(screen_row)
        layout.addSpacing(12)
        layout.addWidget(self._sep())
        layout.addSpacing(12)

        # ---- Brightness ----
        lbl_row = QHBoxLayout()
        b_icon = QLabel(ICON_SUN)
        b_icon.setFont(QFont("Segoe UI Symbol", 14))
        b_icon.setStyleSheet("color: #ff9f0a;")
        self._lbl_brightness = QLabel(self._t("brightness"))
        self._lbl_brightness.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._lbl_brightness.setStyleSheet("color: #f5f5f7;")
        self.brightness_label = QLabel("100%")
        self.brightness_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.brightness_label.setStyleSheet("color: #ff9f0a;")
        self.brightness_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_row.addWidget(b_icon)
        lbl_row.addSpacing(6)
        lbl_row.addWidget(self._lbl_brightness)
        lbl_row.addStretch()
        lbl_row.addWidget(self.brightness_label)
        layout.addLayout(lbl_row)
        layout.addSpacing(4)

        self.brightness_slider = ModernSlider(Qt.Horizontal, ["#ff6b00", "#ff9f0a", "#ffcc00"])
        self.brightness_slider.setRange(10, 100)
        layout.addWidget(self.brightness_slider)
        layout.addSpacing(12)

        # ---- Temperature ----
        lbl_row2 = QHBoxLayout()
        t_icon = QLabel(ICON_TEMP)
        t_icon.setFont(QFont("Segoe UI Symbol", 14))
        t_icon.setStyleSheet("color: #64d2ff;")
        self._lbl_temp = QLabel(self._t("temperature"))
        self._lbl_temp.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._lbl_temp.setStyleSheet("color: #f5f5f7;")
        self.temp_label = QLabel("6500K")
        self.temp_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.temp_label.setStyleSheet("color: #64d2ff;")
        self.temp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_row2.addWidget(t_icon)
        lbl_row2.addSpacing(6)
        lbl_row2.addWidget(self._lbl_temp)
        lbl_row2.addStretch()
        lbl_row2.addWidget(self.temp_label)
        layout.addLayout(lbl_row2)
        layout.addSpacing(4)

        self.temp_slider = ModernSlider(Qt.Horizontal, ["#ff6b6b", "#ff9f0a", "#64d2ff"])
        self.temp_slider.setRange(1000, 6500)
        self.temp_slider.setSingleStep(100)
        layout.addWidget(self.temp_slider)
        layout.addSpacing(14)
        layout.addWidget(self._sep())
        layout.addSpacing(10)

        # ---- Presets ----
        self._lbl_presets = self._section_label("presets")
        layout.addWidget(self._lbl_presets)
        layout.addSpacing(8)

        presets_row = QHBoxLayout()
        presets_row.setSpacing(10)
        for key in PRESETS:
            display = self._t(f"preset_{key}")
            card = PresetCard(display, PRESET_ICONS[key])
            card.clicked.connect(lambda checked, k=key: self._on_preset(k))
            presets_row.addWidget(card)
            self._preset_cards[key] = card
        presets_row.addStretch()
        layout.addLayout(presets_row)

        layout.addSpacing(10)
        layout.addWidget(self._sep())
        layout.addSpacing(10)

        # ---- Startup toggle ----
        startup_row = QHBoxLayout()
        startup_row.setSpacing(8)
        self._lbl_startup = QLabel(self._t("startup"))
        self._lbl_startup.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self._lbl_startup.setStyleSheet("color: #f5f5f7;")
        self.startup_toggle = AnimatedToggle()
        self.startup_toggle.setChecked(self.config.autostart)
        self.startup_toggle.toggled.connect(self._on_startup_toggled)
        startup_row.addWidget(self._lbl_startup)
        startup_row.addStretch()
        startup_row.addWidget(self.startup_toggle)
        layout.addLayout(startup_row)

        layout.addStretch()
        layout.addWidget(self._sep())
        layout.addSpacing(10)

        # ---- Bottom row ----
        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(8)
        self.toggle_label = QLabel(self._t("filter_on"))
        self.toggle_label.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self.toggle_label.setStyleSheet("color: #f5f5f7;")
        self.toggle_switch = AnimatedToggle()
        self.toggle_switch.toggled.connect(self._on_toggle)
        toggle_row.addWidget(self.toggle_label)
        toggle_row.addWidget(self.toggle_switch)
        bottom.addLayout(toggle_row)
        bottom.addStretch()

        self.quit_btn = QPushButton(self._t("quit"))
        self.quit_btn.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self.quit_btn.setCursor(Qt.PointingHandCursor)
        self.quit_btn.setFixedSize(100, 36)
        self.quit_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #ff453a;
                border: 1.5px solid #ff453a; border-radius: 10px; }
            QPushButton:hover { background: #ff453a; color: #ffffff; }
        """)
        self.quit_btn.clicked.connect(lambda: self.quit_requested.emit())
        bottom.addWidget(self.quit_btn)
        layout.addLayout(bottom)

        # Connections
        self.brightness_slider.valueChanged.connect(self._on_brightness)
        self.temp_slider.valueChanged.connect(self._on_temperature)

    # ---- helpers ----

    def _section_label(self, key):
        lbl = QLabel(self._t(key))
        lbl.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        lbl.setStyleSheet("color: #98989d;")
        return lbl

    @staticmethod
    def _paint_close_btn(btn):
        p = QPainter(btn)
        p.setRenderHint(QPainter.Antialiasing)
        if btn.underMouse():
            p.setBrush(QBrush(QColor("#ff453a")))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(0, 0, 30, 30), 15, 15)
            pen_color = QColor("#ffffff")
        else:
            pen_color = QColor("#636366")
        p.setPen(QPen(pen_color, 2, Qt.SolidLine, Qt.RoundCap))
        m = 10
        p.drawLine(m, m, 30 - m, 30 - m)
        p.drawLine(30 - m, m, m, 30 - m)
        p.end()

    def _dot(self, color):
        d = QLabel()
        d.setFixedSize(12, 12)
        d.setStyleSheet(f"background: {color}; border-radius: 6px;")
        return d

    def _sep(self):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #2c2c2e;")
        return line

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(12, 12, self.width() - 24, self.height() - 24)
        path = QPainterPath()
        path.addRoundedRect(rect, 20, 20)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#1c1c1e"))
        grad.setColorAt(1, QColor("#0a0a0c"))
        p.fillPath(path, QBrush(grad))
        p.setPen(QPen(QColor(255, 255, 255, 15), 1))
        p.drawPath(path)
        p.end()

    # ---- language ----

    def _set_language(self, lang):
        if lang == self._lang:
            return
        self._lang = lang
        self.config.language = lang
        self._lang_tr.set_active(lang == "tr")
        self._lang_en.set_active(lang == "en")
        self._refresh_texts()
        self.language_changed.emit(lang)

    def _refresh_texts(self):
        self._lbl_screens.setText(self._t("screens"))
        self._lbl_brightness.setText(self._t("brightness"))
        self._lbl_temp.setText(self._t("temperature"))
        self._lbl_presets.setText(self._t("presets"))
        self._lbl_startup.setText(self._t("startup"))
        self.quit_btn.setText(self._t("quit"))
        enabled = self.toggle_switch.isChecked()
        self.toggle_label.setText(self._t("filter_on") if enabled else self._t("filter_off"))
        for key, card in self._preset_cards.items():
            card.set_name(self._t(f"preset_{key}"))
        # Force full repaint
        self.update()
        self._container.update()

    # ---- config sync ----

    def reload_config(self):
        self.brightness_slider.setValue(self.config.brightness)
        self.temp_slider.setValue(self.config.temperature)
        self.toggle_switch.setChecked(self.config.enabled)
        self._update_toggle_text(self.config.enabled)
        self._detect_active_preset()
        self.startup_toggle.setChecked(self.config.autostart)

        saved = self.config.screens
        for idx, btn in self._screen_buttons.items():
            btn.set_selected(idx in saved if saved else True)

    def get_selected_screens(self):
        return [idx for idx, btn in self._screen_buttons.items() if btn.is_selected]

    # ---- slots ----

    def _on_screen_toggled(self, index, selected):
        screens = self.get_selected_screens()
        self.config.screens = screens
        self.screens_changed.emit(screens)

    def _on_brightness(self, value):
        self.brightness_label.setText(f"{value}%")
        self.config.brightness = value
        self._detect_active_preset()
        self.brightness_changed.emit(value)

    def _on_temperature(self, value):
        self.temp_label.setText(f"{value}K")
        self.config.temperature = value
        self._detect_active_preset()
        self.temperature_changed.emit(value)

    def _on_preset(self, key):
        preset = PRESETS[key]
        self.brightness_slider.setValue(preset["brightness"])
        self.temp_slider.setValue(preset["temperature"])

    def _detect_active_preset(self):
        current = None
        for key, pr in PRESETS.items():
            if pr["brightness"] == self.config.brightness and pr["temperature"] == self.config.temperature:
                current = key
                break
        for key, card in self._preset_cards.items():
            card.set_active(key == current)

    def _on_toggle(self, enabled):
        self._update_toggle_text(enabled)
        self.config.enabled = enabled
        self.toggled.emit(enabled)

    def _on_startup_toggled(self, enabled):
        self.config.autostart = enabled

    def _update_toggle_text(self, enabled):
        self.toggle_label.setText(self._t("filter_on") if enabled else self._t("filter_off"))
        self.toggle_label.setStyleSheet("color: #f5f5f7;" if enabled else "color: #636366;")

    def set_enabled(self, enabled):
        self.toggle_switch.setChecked(enabled)
        self._update_toggle_text(enabled)

    # ---- drag ----

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def closeEvent(self, event):
        event.ignore()
        self.hide()
