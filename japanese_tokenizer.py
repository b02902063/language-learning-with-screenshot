"""Japanese word segmentation helpers using Konoha."""

from konoha import WordTokenizer

_tokenizer: WordTokenizer | None = None


def _get_tokenizer() -> WordTokenizer:
    """Return a singleton ``WordTokenizer`` instance."""
    global _tokenizer
    if _tokenizer is None:
        # ``MeCab`` is a common backend and usually provides the best results
        _tokenizer = WordTokenizer("MeCab")
    return _tokenizer


def segment_japanese(text: str) -> list[str]:
    """Return a list of tokens for ``text`` using ``konoha``."""
    if not text:
        return []
    tokenizer = _get_tokenizer()
    return [t.surface for t in tokenizer.tokenize(text)]
