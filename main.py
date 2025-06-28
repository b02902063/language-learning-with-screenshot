import sys
import os
import io
import base64
from typing import List
import json

import psutil
from PIL import ImageGrab

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


class MainWindow(QtWidgets.QWidget):  # type: ignore
    def __init__(self):
        super().__init__()
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

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            QtWidgets.QMessageBox.warning(self, "Error", "OPENAI_API_KEY not set")
            return
        openai.api_key = api_key

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
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
