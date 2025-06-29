import sys

from PyQt5 import QtWidgets

from config import load_settings, save_settings
from ui import SettingsDialog, MainWindow


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    settings = load_settings()
    dialog = SettingsDialog(settings)
    if dialog.exec_() != QtWidgets.QDialog.Accepted:
        return
    settings.update(dialog.get_settings())
    save_settings(settings)

    window = MainWindow(settings)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
