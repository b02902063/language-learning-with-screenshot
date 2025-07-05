from typing import List
from PyQt5 import QtWidgets, QtCore
import pygetwindow as gw

from display import DisplayArea, WordEntry

import config
from config import t, UI_STRINGS, save_settings
from openai_client import analyze_image
from mock_openai_client import mock_identify_terms, mock_fetch_details

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings):
        super().__init__()
        self._settings = settings
        self.setWindowTitle(t("Settings"))

        form = QtWidgets.QFormLayout()

        self.api_edit = QtWidgets.QLineEdit(settings.get("api_key", ""))
        self.api_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow(t("OpenAI API Key"), self.api_edit)

        self.remember_box = QtWidgets.QCheckBox(t("Remember API Key"))
        self.remember_box.setChecked(bool(settings.get("api_key")))
        form.addRow(self.remember_box)

        self.ui_lang_combo = QtWidgets.QComboBox()
        self.ui_lang_combo.addItems(UI_STRINGS.keys())
        self.ui_lang_combo.setCurrentText(settings.get("ui_language", "en"))
        form.addRow(t("Interface Language"), self.ui_lang_combo)

        self.report_lang_combo = QtWidgets.QComboBox()
        self.report_lang_combo.addItems(["en", "zh-TW"])
        self.report_lang_combo.setCurrentText(settings.get("report_language", "en"))
        form.addRow(t("Report Language"), self.report_lang_combo)

        self.test_mode_box = QtWidgets.QCheckBox(t("Test Mode"))
        self.test_mode_box.setChecked(settings.get("test_mode", False))
        form.addRow(self.test_mode_box)

        button = QtWidgets.QPushButton(t("Continue"))
        button.clicked.connect(self.accept)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(button)
        self.setLayout(layout)

    def get_settings(self) -> dict:
        return {
            "api_key": self.api_edit.text().strip() if self.remember_box.isChecked() else "",
            "ui_language": self.ui_lang_combo.currentText(),
            "report_language": self.report_lang_combo.currentText(),
            "test_mode": self.test_mode_box.isChecked(),
        }


class MainWindow(QtWidgets.QWidget):
    def __init__(self, settings: dict):
        super().__init__()
        self.settings = settings
        self.api_key = settings.get("api_key", "")
        self.report_language = settings.get("report_language", "en")
        self.test_mode = settings.get("test_mode", False)
        config.current_ui_language = settings.get("ui_language", "en")
        self.identify_func = mock_identify_terms if self.test_mode else None
        self.fetch_func = mock_fetch_details if self.test_mode else None
        self.setWindowTitle(t("Screenshot Language Helper"))
        self.resize(1500, 800)

        layout = QtWidgets.QHBoxLayout()

        self.display_area = DisplayArea()
        layout.addWidget(self.display_area, 11)

        right_layout = QtWidgets.QVBoxLayout()
        form = QtWidgets.QFormLayout()
        self.language_combo = QtWidgets.QComboBox()
        self.languages = self.load_language_config()
        self.language_combo.addItems(self.languages.keys())
        self.language_combo.setFixedSize(150, 25)
        self.language_combo.currentTextChanged.connect(self.update_levels)
        self.label_target_language = QtWidgets.QLabel(t("Target Language"))
        form.addRow(self.label_target_language, self.language_combo)

        self.level_combo = QtWidgets.QComboBox()
        self.level_combo.setFixedSize(150, 25)
        self.label_level = QtWidgets.QLabel(t("Your Level"))
        form.addRow(self.label_level, self.level_combo)
        self.update_levels(self.language_combo.currentText(), update_display=False)
        self.level_combo.currentIndexChanged.connect(self.update_display)

        self.window_combo = QtWidgets.QComboBox()
        self.window_combo.setFixedSize(150, 25)
        for w in gw.getAllWindows():
            title = w.title.strip()
            if title:
                self.window_combo.addItem(title)
        self.label_window = QtWidgets.QLabel(t("Window"))
        form.addRow(self.label_window, self.window_combo)

        right_layout.addLayout(form)

        self.capture_button = QtWidgets.QPushButton(t("Capture & Analyze"))
        self.capture_button.setFixedSize(150, 25)
        self.capture_button.clicked.connect(self.capture_and_analyze)
        right_layout.addWidget(self.capture_button, alignment=QtCore.Qt.AlignCenter)

        right_layout.addStretch(1)

        self.settings_button = QtWidgets.QPushButton(t("Settings"))
        self.settings_button.clicked.connect(self.open_settings)
        right_layout.addWidget(self.settings_button, alignment=QtCore.Qt.AlignRight)

        layout.addLayout(right_layout, 1)
        self.setLayout(layout)
        self.words: List[WordEntry] = []

    def load_language_config(self) -> dict:
        import json
        import os
        path = os.path.join(os.path.dirname(__file__), "language_config.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"English": ["A1", "A2", "B1", "B2", "C1", "C2"]}

    def update_levels(self, language: str, update_display: bool=True) -> None:
        levels = self.languages.get(language, [])
        self.level_combo.clear()
        self.level_combo.addItems(levels)
        if update_display:
            self.update_display()

    def capture_and_analyze(self):
        if not self.api_key and not self.test_mode:
            QtWidgets.QMessageBox.warning(self, t("Error"), t("API key not provided"))
            return
        title = self.window_combo.currentText()
        data = analyze_image(
            title,
            self.language_combo.currentText(),
            self.report_language,
            self.api_key,
            identify_func=self.identify_func,
            fetch_func=self.fetch_func,
        )
        self.words = self.parse_words(data)
        self.update_display()

    def open_settings(self):
        dialog = SettingsDialog(self.settings)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.settings.update(dialog.get_settings())
            save_settings(self.settings)
            self.api_key = self.settings.get("api_key", "")
            self.report_language = self.settings.get("report_language", "en")
            self.test_mode = self.settings.get("test_mode", False)
            config.current_ui_language = self.settings.get("ui_language", "en")
            self.identify_func = mock_identify_terms if self.test_mode else None
            self.fetch_func = mock_fetch_details if self.test_mode else None
            self.refresh_ui_texts()

    def refresh_ui_texts(self):
        self.setWindowTitle(t("Screenshot Language Helper"))
        self.label_target_language.setText(t("Target Language"))
        self.label_level.setText(t("Your Level"))
        self.label_window.setText(t("Window"))
        self.capture_button.setText(t("Capture & Analyze"))
        self.settings_button.setText(t("Settings"))

    def parse_words(self, data: dict) -> List[WordEntry]:
        result: List[WordEntry] = []
        levels = self.languages.get(self.language_combo.currentText(), [])
        for level_key, info in data.items():
            try:
                difficulty = levels.index(level_key) + 1
            except ValueError:
                difficulty = len(levels)
            for vocab in info.get("vocabulary", []):
                word = vocab.get("word", "")
                pos = vocab.get("pos")
                subtype = pos['subtype']
                label = pos['label']
                pos_text = f"{label},{subtype}" if subtype is not None else label
                result.append(WordEntry(word, difficulty, vocab, pos=pos_text))
            for gram in info.get("grammar", []):
                word = gram.get("grammar_point", "")
                result.append(WordEntry(word, difficulty, gram, is_grammar=True))
        
        result = sorted(
            result,
            key=lambda x: (x.is_grammar, x.pos, x.difficulty)
        )

        return result

    def update_display(self):
        level = self.level_combo.currentIndex() + 1
        self.display_area.set_entries(self.words, level)

