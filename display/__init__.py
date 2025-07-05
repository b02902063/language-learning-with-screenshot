from typing import List, Dict, Any
from PyQt5 import QtWidgets

class WordEntry:
    def __init__(self, word: str, difficulty: int, data: dict, is_grammar: bool = False):
        self.word = word
        self.difficulty = difficulty
        self.data = data
        self.is_grammar = is_grammar
        self.description = data.get('definition', '')

def _dict_to_markdown(data: Dict[str, Any], level: int = 2) -> str:
    """Convert a nested dictionary into markdown headers.

    The top level starts at ``level`` and each nested level increases the
    header depth. Lists of dictionaries are rendered as tables when possible.
    """

    lines: List[str] = []
    for key, value in data.items():
        header = '#' * level + f" {key}"
        if isinstance(value, dict):
            lines.append(header)
            lines.append(_dict_to_markdown(value, level + 1))
        elif isinstance(value, list):
            lines.append(header)
            if value and all(isinstance(v, dict) for v in value):
                cols = sorted({k for item in value for k in item.keys()})
                lines.append('|' + '|'.join(cols) + '|')
                lines.append('|' + '|'.join(['---'] * len(cols)) + '|')
                for item in value:
                    row = [str(item.get(c, '')) for c in cols]
                    lines.append('|' + '|'.join(row) + '|')
            else:
                for v in value:
                    if isinstance(v, dict):
                        lines.append(_dict_to_markdown(v, level + 1))
                    else:
                        lines.append(f"- {v}")
        else:
            lines.append(header)
            lines.append(str(value))
    return '\n'.join(lines)


def item_to_markdown(entry: WordEntry) -> str:
    """Return a markdown representation of ``entry`` starting at level 2."""

    data = dict(entry.data)
    if entry.is_grammar:
        title = data.pop('grammar_point', '')
    else:
        title = f"{data.pop('word', '')} ({data.pop('reading', '')})"
    lines = [f"## {title}"]
    if data:
        lines.append(_dict_to_markdown(data, level=3))
    return '\n'.join(lines)


class DisplayArea(QtWidgets.QWidget):
    """Widget showing vocabulary/grammar lists with a preview pane."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._vocab_entries: List[WordEntry] = []
        self._grammar_entries: List[WordEntry] = []

        layout = QtWidgets.QHBoxLayout(self)

        self.text_view = QtWidgets.QTextEdit()
        self.text_view.setReadOnly(True)
        layout.addWidget(self.text_view, 3)

        list_container = QtWidgets.QWidget()
        list_layout = QtWidgets.QVBoxLayout(list_container)

        vocab_box = QtWidgets.QGroupBox('Vocabulary')
        vocab_layout = QtWidgets.QVBoxLayout(vocab_box)
        self.vocab_list = QtWidgets.QListWidget()
        vocab_layout.addWidget(self.vocab_list)

        grammar_box = QtWidgets.QGroupBox('Grammar')
        grammar_layout = QtWidgets.QVBoxLayout(grammar_box)
        self.grammar_list = QtWidgets.QListWidget()
        grammar_layout.addWidget(self.grammar_list)

        list_layout.addWidget(vocab_box)
        list_layout.addWidget(grammar_box)

        layout.addWidget(list_container, 1)

        self.vocab_list.itemClicked.connect(lambda item: self.show_detail(item, False))
        self.grammar_list.itemClicked.connect(lambda item: self.show_detail(item, True))

    def set_entries(self, entries: List[WordEntry], level: int) -> None:
        self._vocab_entries = [e for e in entries if not e.is_grammar and e.difficulty <= level]
        self._grammar_entries = [e for e in entries if e.is_grammar and e.difficulty <= level]
        self.update_lists()
        self.text_view.clear()

    def update_lists(self) -> None:
        self.vocab_list.clear()
        for e in self._vocab_entries:
            self.vocab_list.addItem(e.word)

        self.grammar_list.clear()
        for e in self._grammar_entries:
            self.grammar_list.addItem(e.word)

    def show_detail(self, item: QtWidgets.QListWidgetItem, is_grammar: bool) -> None:
        if is_grammar:
            index = self.grammar_list.row(item)
            entry = self._grammar_entries[index]
        else:
            index = self.vocab_list.row(item)
            entry = self._vocab_entries[index]
        md = item_to_markdown(entry)
        self.text_view.setMarkdown(md)

