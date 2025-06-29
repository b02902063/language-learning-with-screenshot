from typing import List
from PyQt5 import QtWidgets

class WordEntry:
    def __init__(self, word: str, difficulty: int, data: dict, is_grammar: bool = False):
        self.word = word
        self.difficulty = difficulty
        self.data = data
        self.is_grammar = is_grammar
        self.description = data.get('definition', '')


def _vocab_to_markdown(item: dict) -> str:
    lines = [f"# {item.get('word', '')} ({item.get('reading', '')})", "", item.get('definition', '')]
    pos = item.get('pos', {})
    label = pos.get('label')
    if label:
        subtype = pos.get('subtype')
        label_line = f"**{label}**"
        if subtype:
            label_line += f" ({subtype})"
        lines.append(label_line)
    conj = item.get('conjugation')
    if conj:
        lines.append('## Conjugation')
        for f in conj.get('forms', []):
            lines.append(f"- {f}")
    examples = item.get('examples', [])
    if examples:
        lines.append('## Examples')
        for ex in examples:
            tl = ex.get('target_language', '')
            ul = ex.get('user_language', '')
            lines.append(f"- {tl} — {ul}")
    return '\n'.join(lines)


def _grammar_to_markdown(item: dict) -> str:
    lines = [f"# {item.get('grammar_point', '')}", '', item.get('definition', '')]
    structure = item.get('structure', [])
    if structure:
        lines.append('## Structure')
        for s in structure:
            lines.append(f"- {s}")
    usage = item.get('usage_note')
    if usage:
        lines.append(f"**Usage:** {usage}")
    examples = item.get('examples', [])
    if examples:
        lines.append('## Examples')
        for ex in examples:
            tl = ex.get('target_language', '')
            ul = ex.get('user_language', '')
            lines.append(f"- {tl} — {ul}")
    return '\n'.join(lines)


def item_to_markdown(entry: WordEntry) -> str:
    return _grammar_to_markdown(entry.data) if entry.is_grammar else _vocab_to_markdown(entry.data)


class DisplayArea(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries: List[WordEntry] = []
        self.stacked = QtWidgets.QStackedLayout(self)

        self.list_widget = QtWidgets.QListWidget()
        self.stacked.addWidget(self.list_widget)

        detail_container = QtWidgets.QWidget()
        dlayout = QtWidgets.QVBoxLayout(detail_container)
        self.back_button = QtWidgets.QPushButton('Back')
        self.text_view = QtWidgets.QTextEdit()
        self.text_view.setReadOnly(True)
        dlayout.addWidget(self.back_button)
        dlayout.addWidget(self.text_view)
        self.stacked.addWidget(detail_container)

        self.list_widget.itemClicked.connect(self.show_detail)
        self.back_button.clicked.connect(self.show_list)

    def set_entries(self, entries: List[WordEntry], level: int) -> None:
        self._entries = [e for e in entries if e.difficulty <= level]
        self.show_list()

    def show_list(self) -> None:
        self.list_widget.clear()
        for e in self._entries:
            self.list_widget.addItem(e.word)
        self.stacked.setCurrentIndex(0)

    def show_detail(self, item: QtWidgets.QListWidgetItem) -> None:
        index = self.list_widget.row(item)
        entry = self._entries[index]
        md = item_to_markdown(entry)
        self.text_view.setMarkdown(md)
        self.stacked.setCurrentIndex(1)

