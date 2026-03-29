import sys
import os
import signal

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from tray_app import TrayApp


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)

    # Keep running when all windows are closed (tray app)
    app.setQuitOnLastWindowClosed(False)

    # Determine icon path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "resources", "icon.png")

    tray = TrayApp(icon_path)

    # Restore gamma on quit
    app.aboutToQuit.connect(tray.gamma.restore)

    # Allow Ctrl+C in terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
