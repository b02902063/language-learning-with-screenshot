from typing import List
from PyQt5 import QtWidgets, QtCore, QtGui
import base64
import io
from PIL import Image, ImageChops
import pygetwindow as gw

from display import DisplayArea, WordEntry

import config
from config import t, UI_STRINGS, save_settings
from openai_client import analyze_image
import openai_client
from mock_openai_client import mock_identify_terms, mock_fetch_details
from screenshot import grab_window_image


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
        self.capture_button.clicked.connect(self.capture_and_identify)
        right_layout.addWidget(self.capture_button, alignment=QtCore.Qt.AlignCenter)

        self.analyze_all_button = QtWidgets.QPushButton(t("Analyze All"))
        self.analyze_all_button.setFixedSize(150, 25)
        self.analyze_all_button.clicked.connect(self.capture_and_analyze_all)
        right_layout.addWidget(self.analyze_all_button, alignment=QtCore.Qt.AlignCenter)

        self.preview_button = QtWidgets.QPushButton(t("Preview the screenshot"))
        self.preview_button.setFixedSize(150, 25)
        self.preview_button.clicked.connect(self.preview_screenshot)
        right_layout.addWidget(self.preview_button, alignment=QtCore.Qt.AlignCenter)

        self.view_last_button = QtWidgets.QPushButton(t("View the latest screenshot"))
        self.view_last_button.setFixedSize(150, 25)
        self.view_last_button.clicked.connect(self.show_last_screenshot)
        right_layout.addWidget(self.view_last_button, alignment=QtCore.Qt.AlignCenter)

        self.fetch_details_button = QtWidgets.QPushButton(t("Fetch Details"))
        self.fetch_details_button.setFixedSize(160, 40)
        self.fetch_details_button.clicked.connect(self.fetch_selected_details)
        right_layout.addWidget(self.fetch_details_button, alignment=QtCore.Qt.AlignCenter)

        right_layout.addStretch(1)

        self.settings_button = QtWidgets.QPushButton(t("Settings"))
        self.settings_button.clicked.connect(self.open_settings)
        right_layout.addWidget(self.settings_button, alignment=QtCore.Qt.AlignRight)

        layout.addLayout(right_layout, 1)
        self.setLayout(layout)
        self.words: List[WordEntry] = []
        self.last_image = None
        self.last_img_b64 = None

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

    def capture_and_analyze_all(self, img_b64: str | None = None, pil_image: Image.Image | None = None):
        if not self.api_key and not self.test_mode:
            QtWidgets.QMessageBox.warning(self, t("Error"), t("API key not provided"))
            return
        title = self.window_combo.currentText()
        if img_b64 is None:
            img_b64 = openai_client.grab_window_image(title)
        if pil_image is None and img_b64 is not None:
            pil_image = Image.open(io.BytesIO(base64.b64decode(img_b64)))
        if self.last_image is not None and pil_image is not None:
            diff = self._image_diff_ratio(self.last_image, pil_image)
            if diff <= 0.03:
                if QtWidgets.QMessageBox.question(
                    self,
                    t("Warning"),
                    t("Screenshot looks similar to previous one. Proceed?"),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                ) != QtWidgets.QMessageBox.Yes:
                    return
        data = analyze_image(
            title,
            self.language_combo.currentText(),
            self.report_language,
            self.api_key,
            img_b64=img_b64,
            identify_func=self.identify_func,
            fetch_func=self.fetch_func,
        )
        self.last_image = pil_image
        self.last_img_b64 = img_b64
        self.words = self.parse_words(data)
        self.update_display()

    def capture_and_identify(self, img_b64: str | None = None, pil_image: Image.Image | None = None):
        if not self.api_key and not self.test_mode:
            QtWidgets.QMessageBox.warning(self, t("Error"), t("API key not provided"))
            return
        title = self.window_combo.currentText()
        if img_b64 is None:
            img_b64 = openai_client.grab_window_image(title)
        if pil_image is None and img_b64 is not None:
            pil_image = Image.open(io.BytesIO(base64.b64decode(img_b64)))
        if self.last_image is not None and pil_image is not None:
            diff = self._image_diff_ratio(self.last_image, pil_image)
            if diff <= 0.03:
                if QtWidgets.QMessageBox.question(
                    self,
                    t("Warning"),
                    t("Screenshot looks similar to previous one. Proceed?"),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                ) != QtWidgets.QMessageBox.Yes:
                    return
        data = openai_client.identify_image(
            title,
            self.language_combo.currentText(),
            self.report_language,
            self.api_key,
            img_b64=img_b64,
            identify_func=self.identify_func,
        )
        self.last_image = pil_image
        self.last_img_b64 = img_b64
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
        self.analyze_all_button.setText(t("Analyze All"))
        self.preview_button.setText(t("Preview the screenshot"))
        self.view_last_button.setText(t("View the latest screenshot"))
        self.fetch_details_button.setText(t("Fetch Details"))
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
                if isinstance(vocab, str):
                    word = vocab
                    pos_text = "Unknown"
                    data = {}
                else:
                    word = vocab.get("word", "")
                    pos = vocab.get("pos", {})
                    subtype = pos.get('subtype')
                    label = pos.get('label', 'Unknown')
                    pos_text = f"{label},{subtype}" if subtype is not None else label
                    data = vocab
                result.append(WordEntry(word, difficulty, data, pos=pos_text))
            for gram in info.get("grammar", []):
                if isinstance(gram, str):
                    word = gram
                    data = {}
                else:
                    word = gram.get("grammar_point", "")
                    data = gram
                result.append(WordEntry(word, difficulty, data, is_grammar=True))
        
        result = sorted(
            result,
            key=lambda x: (x.is_grammar, x.pos, x.difficulty)
        )

        return result

    def update_display(self):
        level = self.level_combo.currentIndex() + 1
        self.display_area.set_entries(self.words, level)

    def preview_screenshot(self):
        title = self.window_combo.currentText()
        #img_b64 = openai_client.grab_window_image(title)
        img_b64 = grab_window_image(title)
        img_data = base64.b64decode(img_b64)
        pil_img = Image.open(io.BytesIO(img_data))
        qimg = QtGui.QImage.fromData(img_data)
        pix = QtGui.QPixmap.fromImage(qimg)

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(t("Preview the screenshot"))
        vbox = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel()
        label.setPixmap(pix.scaled(800, 600, QtCore.Qt.KeepAspectRatio))
        vbox.addWidget(label)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        all_btn = buttons.addButton(t("All"), QtWidgets.QDialogButtonBox.ActionRole)
        vbox.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        all_btn.clicked.connect(lambda: dialog.done(2))
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.capture_and_identify(img_b64, pil_img)
        elif dialog.result() == 2:
            self.capture_and_analyze_all(img_b64, pil_img)

    def show_last_screenshot(self):
        if not hasattr(self, "last_img_b64") or not self.last_img_b64:
            return
        img_data = base64.b64decode(self.last_img_b64)
        qimg = QtGui.QImage.fromData(img_data)
        pix = QtGui.QPixmap.fromImage(qimg)
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(t("View the latest screenshot"))
        vbox = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel()
        label.setPixmap(pix.scaled(800, 600, QtCore.Qt.KeepAspectRatio))
        vbox.addWidget(label)
        close_btn = QtWidgets.QPushButton(t("Close"))
        close_btn.clicked.connect(dialog.accept)
        vbox.addWidget(close_btn, alignment=QtCore.Qt.AlignCenter)
        dialog.exec_()

    def fetch_selected_details(self):
        vocab_indexes = self.display_area.vocab_list.selectedIndexes()
        grammar_indexes = self.display_area.grammar_list.selectedIndexes()

        vocab_terms = []
        vocab_entries = []
        for idx in vocab_indexes:
            entry = self.display_area._vocab_entries[idx.row()]
            if not entry.data:
                vocab_terms.append(entry.word)
                vocab_entries.append(entry)

        grammar_terms = []
        grammar_entries = []
        for idx in grammar_indexes:
            entry = self.display_area._grammar_entries[idx.row()]
            if not entry.data:
                grammar_terms.append(entry.word)
                grammar_entries.append(entry)

        if not vocab_terms and not grammar_terms:
            return

        details = openai_client.fetch_details_only(
            vocab_terms,
            grammar_terms,
            self.language_combo.currentText(),
            self.report_language,
            self.api_key,
            fetch_func=self.fetch_func,
        )

        for item in details.get("vocabulary", []):
            word = item.get("word")
            for e in vocab_entries:
                if e.word == word:
                    e.data = item
                    e.description = item.get("definition", "")
                    pos = item.get("pos", {})
                    subtype = pos.get("subtype")
                    label = pos.get("label", "Unknown")
                    e.pos = f"{label},{subtype}" if subtype is not None else label
        for item in details.get("grammar", []):
            point = item.get("grammar_point")
            for e in grammar_entries:
                if e.word == point:
                    e.data = item

        self.update_display()

    @staticmethod
    def _image_diff_ratio(img1: Image.Image, img2: Image.Image) -> float:
        img1 = img1.convert("RGB")
        img2 = img2.convert("RGB")
        if img1.size != img2.size:
            img2 = img2.resize(img1.size)
        diff = ImageChops.difference(img1, img2)
        hist = diff.histogram()
        sq = sum(i * hist[i] for i in range(len(hist)))
        max_diff = 255 * img1.size[0] * img1.size[1] * 3
        return sq / max_diff

