from typing import List, Dict, Any
from PyQt5 import QtWidgets, QtGui

class WordEntry:
    def __init__(self, word: str, difficulty: int, data: dict, pos: str|None = None, is_grammar: bool = False):
        self.word = word
        self.difficulty = difficulty
        self.data = data
        self.is_grammar = is_grammar
        self.description = data.get('definition', '')
        self.pos = pos
        if pos is None:
            self.pos = "Unknown"

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


def _has_none(value: Any) -> bool:
    """Recursively check if ``value`` or any nested value is ``None``."""
    if value is None:
        return True
    if isinstance(value, dict):
        return any(_has_none(v) for v in value.values())
    if isinstance(value, list):
        return any(_has_none(v) for v in value)
    return False


def vocab_to_markdown(v: Dict[str, Any]) -> str:
    """Return markdown for a vocabulary item following the specified format."""
    if not v.get("word"):
        return ""

    lines: List[str] = [f"# {v['word']}({v['reading']})"]
    lines.append("\n---\n")

    # Definition section
    pos = v.get('pos', {})
    definition = v.get('definition')
    if pos and definition:
        lines.append("## \u5b9a\u7fa9")
        subtype = pos.get('subtype', '')
        pos_str = f"{pos['label']},{subtype}" if subtype else pos['label']
        lines.append(f"[{pos_str}]")
        lines.append(str(definition))
        lines.append("\n---\n")

    # Conjugation section
    conj = v.get('conjugation')
    if conj and not _has_none(conj):
        examples = conj.get('examples', [])
        rows = []
        for ex in examples:
            if _has_none(ex):
                rows = []
                break
            rows.append(f"|{ex['form']}|{ex['usage']}|")
        if rows:
            lines.append("## \u6d3b\u7528")
            lines.append("|\u5f62\u5f0f|\u7528\u6cd5|")
            lines.append("|---|---|")
            lines.extend(rows)
            lines.append("\n---\n")

    # Transitivity section
    trans = v.get('transitivity')
    if trans and not _has_none(trans):
        intra = trans.get('intransitive')
        tran = trans.get('transitive')
        if intra and tran and not _has_none(intra) and not _has_none(tran):
            lines.append("## \u81ea\u4ed6\u52d5\u8a5e\u5c0d")
            lines.append(
                f"### \u81ea\u52d5\u8a5e\uff1a\n{intra['word']}({intra['reading']})[{intra['type']}]\n"
            )
            lines.append(
                f"### \u4ed6\u52d5\u8a5e\uff1a\n{tran['word']}({tran['reading']})[{tran['type']}]\n"
            )
            lines.append("\n---\n")
    
    # Related words section
    related = v.get('related', [])
    table_rows = []
    for r in related:
        subtype = r.get('subtype', "Unknown")
        pos = r.get('pos', "Unknown")
        pos_field = f"{pos},{subtype}"
        difference = r.get('difference', '')
        table_rows.append(
            f"|{r['word']}|{r['reading']}|{pos_field}|{r['definition']}|{difference}|"
        )
    if table_rows:
        lines.append("## \u76f8\u4f3c\u8a5e")
        lines.append("|\u55ae\u5b57|\u8b80\u97f3|\u8a5e\u6027|\u5b9a\u7fa9|\u5340\u5225|")
        lines.append("|---|---|---|---|---|")
        lines.extend(table_rows)
        lines.append("\n---\n")
    
    # Examples section
    examples = v.get('examples', [])
    if examples and not _has_none(examples):
        lines.append("## \u4f8b\u53e5")
        for i, ex in enumerate(examples, start=1):
            lines.append(
                f"{i}. <big>{ex['target_language']}</big>\n<br />\n<small>{ex['user_language']}</small>\n"
            )

    return '\n'.join(lines)


def grammar_to_markdown(g: Dict[str, Any]) -> str:
    """Return markdown for a grammar item following the specified format."""

    title = g.get("grammar_point")
    if not title:
        return ""

    lines: List[str] = [f"# {title}"]
    lines.append("\n---\n")

    # Definition section
    definition = g.get("definition")
    usage_note = g.get("usage_note")
    tags = g.get("tags") or []
    if definition or usage_note or tags:
        lines.append("## \u5b9a\u7fa9")
        if definition:
            lines.append(str(definition))
        if usage_note:
            lines.append(str(usage_note))
        if tags:
            lines.append(", ".join(tags))
        lines.append("\n---\n")

    # Equivalent expressions section
    equivalents = g.get("equivalent_expressions", [])
    rows = []
    for eq in equivalents:
        if _has_none(eq):
            rows = []
            break
        rows.append(f"|{eq['expression']}|{eq['difference']}|")
    if rows:
        lines.append("## \u76f8\u4f3c\u6587\u6cd5")
        lines.append("|\u6587\u6cd5|\u5dee\u7570|")
        lines.append("|---|---|")
        lines.extend(rows)
        lines.append("\n---\n")

    # Related vocabulary section
    related = g.get("related_vocabulary", [])
    rows = []
    for r in related:
        if _has_none(r):
            rows = []
            break
        reading = r.get("reading", "")
        relation = r.get("relation", "")
        rows.append(f"|{r['word']}|{reading}|{r['definition']}|{relation}|")
    if rows:
        lines.append("## \u95dc\u806f\u55ae\u5b57")
        lines.append("|\u55ae\u5b57|\u8b80\u97f3|\u5b9a\u7fa9|\u4ecb\u7d39|")
        lines.append("|---|---|---|---|")
        lines.extend(rows)
        lines.append("\n---\n")

    # Examples section
    examples = g.get("examples", [])
    if examples and not _has_none(examples):
        lines.append("## \u4f8b\u53e5")
        for i, ex in enumerate(examples, start=1):
            lines.append(
                f"{i}. <big>{ex['target_language']}</big>\n<br />\n<small>{ex['user_language']}</small>\n"
            )

    return "\n".join(lines)


def item_to_markdown(entry: WordEntry) -> str:
    """Return a markdown representation of ``entry`` starting at level 1."""

    if entry.is_grammar:
        return grammar_to_markdown(entry.data)
    return vocab_to_markdown(entry.data)


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
            self.vocab_list.addItem(f"{e.word}[{e.pos}], N{e.difficulty}")

        self.grammar_list.clear()
        for e in self._grammar_entries:
            self.grammar_list.addItem(f"{e.word}, N{e.difficulty}")

    def show_detail(self, item: QtWidgets.QListWidgetItem, is_grammar: bool) -> None:
        if is_grammar:
            index = self.grammar_list.row(item)
            entry = self._grammar_entries[index]
        else:
            index = self.vocab_list.row(item)
            entry = self._vocab_entries[index]
        md = item_to_markdown(entry)
        self.text_view.setMarkdown(md)
        
        cursor = self.text_view.textCursor()
        cursor.select(QtGui.QTextCursor.Document) 

        block_format = QtGui.QTextBlockFormat()
        block_format.setLineHeight(100, QtGui.QTextBlockFormat.ProportionalHeight) 

        cursor.mergeBlockFormat(block_format)
        self.text_view.setTextCursor(cursor)

