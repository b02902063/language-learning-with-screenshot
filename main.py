import sys
import os
import io
import base64
from typing import List
import json

import psutil
from PIL import ImageGrab

# Configuration file to store the API key when the user chooses to remember it.
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".language_helper.json")


def load_saved_key() -> str:
    """Load API key from config file if it exists."""
    if not os.path.exists(CONFIG_FILE):
        return ""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("api_key", "")
    except Exception:
        return ""


def save_key(key: str) -> None:
    """Persist API key to config file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"api_key": key}, f)
    except Exception:
        pass


def clear_saved_key() -> None:
    """Remove stored API key."""
    try:
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
    except Exception:
        pass

try:
    import openai
    from PyQt5 import QtWidgets, QtCore
except ImportError:
    openai = None
    QtWidgets = None


class WordEntry:
    def __init__(self, word: str, difficulty: int, description: str):
        self.word = word
        self.difficulty = difficulty
        self.description = description


class LoginDialog(QtWidgets.QDialog):  # type: ignore
    """Dialog to ask the user for their OpenAI API key."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter API Key")
        layout = QtWidgets.QVBoxLayout()

        self.api_edit = QtWidgets.QLineEdit()
        self.api_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(QtWidgets.QLabel("OpenAI API Key"))
        layout.addWidget(self.api_edit)

        self.remember_box = QtWidgets.QCheckBox("Remember API Key")
        layout.addWidget(self.remember_box)

        button = QtWidgets.QPushButton("Continue")
        button.clicked.connect(self.accept)
        layout.addWidget(button)

        self.setLayout(layout)

        saved_key = load_saved_key()
        if saved_key:
            self.api_edit.setText(saved_key)
            self.remember_box.setChecked(True)

    @property
    def api_key(self) -> str:
        return self.api_edit.text().strip()


class MainWindow(QtWidgets.QWidget):  # type: ignore
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.setWindowTitle("Screenshot Language Helper")
        self.resize(600, 400)

        layout = QtWidgets.QVBoxLayout()

        form = QtWidgets.QFormLayout()
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(["English", "Japanese", "French"])  # example
        form.addRow("Target Language", self.language_combo)

        self.level_combo = QtWidgets.QComboBox()
        self.level_combo.addItems(["A1", "A2", "B1", "B2", "C1", "C2"])
        form.addRow("Your Level", self.level_combo)

        self.process_combo = QtWidgets.QComboBox()
        for p in psutil.process_iter(['pid', 'name']):
            self.process_combo.addItem(f"{p.info['name']} ({p.info['pid']})", p.info['pid'])
        form.addRow("Process", self.process_combo)

        layout.addLayout(form)

        self.capture_button = QtWidgets.QPushButton("Capture && Analyze")
        self.capture_button.clicked.connect(self.capture_and_analyze)
        layout.addWidget(self.capture_button)

        self.filter_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.filter_slider.setMinimum(1)
        self.filter_slider.setMaximum(6)
        self.filter_slider.setValue(6)
        self.filter_slider.valueChanged.connect(self.update_display)
        layout.addWidget(self.filter_slider)

        self.result_box = QtWidgets.QTextEdit()
        layout.addWidget(self.result_box)

        self.setLayout(layout)

        self.words: List[WordEntry] = []

    def capture_and_analyze(self):
        if QtWidgets is None or openai is None:
            QtWidgets.QMessageBox.warning(self, "Missing deps", "PyQt5 and openai are required")
            return

        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        prompt = (
            "List vocabulary words and grammar items found in the image with their difficulty level (1-6). "
            "Respond in JSON as a list with fields word, difficulty and description."
        )

        if not self.api_key:
            QtWidgets.QMessageBox.warning(self, "Error", "API key not provided")
            return
        openai.api_key = self.api_key

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                        ],
                    }
                ],
                max_tokens=500,
            )
            text = response.choices[0].message.content
            self.words = self.parse_words(text)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "API error", str(e))
            return

        self.update_display()

    def parse_words(self, text: str) -> List[WordEntry]:
        try:
            data = json.loads(text)
            result = [WordEntry(d.get('word', ''), int(d.get('difficulty', 0)), d.get('description', '')) for d in data]
            return result
        except Exception:
            return []

    def update_display(self):
        level = self.filter_slider.value()
        self.result_box.clear()
        for entry in self.words:
            if entry.difficulty <= level:
                self.result_box.append(f"{entry.word} (level {entry.difficulty}): {entry.description}")


def main():
    if QtWidgets is None:
        print("PyQt5 not installed")
        return
    app = QtWidgets.QApplication(sys.argv)

    login = LoginDialog()
    if login.exec_() != QtWidgets.QDialog.Accepted:
        return

    key = login.api_key
    if login.remember_box.isChecked() and key:
        save_key(key)
    elif not login.remember_box.isChecked():
        clear_saved_key()

    window = MainWindow(key)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
