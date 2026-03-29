import ctypes
import atexit

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter


# Windows constants for click-through overlay
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
GWL_EXSTYLE = -20


class OverlayWindow(QWidget):
    """Overlay for a single screen."""

    def __init__(self, screen_index):
        super().__init__()
        self._color = QColor(0, 0, 0, 0)
        self._screen_index = screen_index
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.update_geometry()

    def update_geometry(self):
        desktop = QApplication.desktop()
        if self._screen_index < desktop.screenCount():
            geo = desktop.screenGeometry(self._screen_index)
            self.setGeometry(geo)

    def showEvent(self, event):
        super().showEvent(event)
        hwnd = int(self.winId())
        user32 = ctypes.windll.user32
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(
            hwnd, GWL_EXSTYLE,
            style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
        )

    def set_color(self, r, g, b, alpha):
        self._color = QColor(r, g, b, alpha)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), self._color)
        p.end()


class GammaController:
    """Controls screen brightness and color temperature via per-monitor overlays."""

    def __init__(self):
        screen_count = QApplication.desktop().screenCount()
        self._overlays = {}
        for i in range(screen_count):
            self._overlays[i] = OverlayWindow(i)
        self._active_screens = set()
        atexit.register(self.restore)

    @staticmethod
    def get_screen_count():
        return QApplication.desktop().screenCount()

    @staticmethod
    def get_screen_info():
        """Return list of screen info dicts."""
        desktop = QApplication.desktop()
        screens = []
        for i in range(desktop.screenCount()):
            geo = desktop.screenGeometry(i)
            is_primary = (i == desktop.primaryScreen())
            screens.append({
                "index": i,
                "width": geo.width(),
                "height": geo.height(),
                "x": geo.x(),
                "y": geo.y(),
                "primary": is_primary,
            })
        return screens

    def apply(self, brightness, temperature, screen_indices=None):
        """Apply filter to specific screens. If screen_indices is None, apply to all."""
        brightness = max(10, min(100, brightness))

        dark_alpha = int((1.0 - brightness / 100.0) * 200)
        temp_factor = 1.0 - (temperature - 1000) / 5500.0
        tint_alpha = int(temp_factor * 80)
        total_alpha = min(dark_alpha + tint_alpha, 220)

        tint_r = int(40 * temp_factor)
        tint_g = int(20 * temp_factor)

        target = set(screen_indices) if screen_indices is not None else set(self._overlays.keys())

        for idx, overlay in self._overlays.items():
            if idx in target and total_alpha > 0:
                overlay.set_color(tint_r, tint_g, 0, total_alpha)
                if idx not in self._active_screens:
                    overlay.show()
                    self._active_screens.add(idx)
            else:
                if idx in self._active_screens:
                    overlay.hide()
                    self._active_screens.discard(idx)

    def restore(self):
        try:
            for overlay in self._overlays.values():
                overlay.hide()
            self._active_screens.clear()
        except Exception:
            pass
