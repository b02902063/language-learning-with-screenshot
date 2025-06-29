import io
import base64
import json
from typing import Dict, List, Callable, Any, Optional

from PIL import ImageGrab
import pygetwindow as gw
import openai

from prompts import get_prompt_factory
from schema import ITEM_SCHEMA, IDENTIFY_RESPONSE_SCHEMA
from cache import load_cache, save_cache


def grab_window_image(title: str) -> str:
    """Capture the selected window and return base64 string."""
    rect = None
    for w in gw.getWindowsWithTitle(title):
        if w.title.strip() == title:
            rect = (w.left, w.top, w.left + w.width, w.top + w.height)
            break
    if rect:
        img = ImageGrab.grab(bbox=rect)
    else:
        img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _identify_terms(img_b64: str, factory, target_lang: str, api_key: str) -> Dict:
    """Ask OpenAI to identify vocabulary and grammar in the image."""
    prompt = factory.create_identify_prompt(target_lang)
    openai.api_key = api_key
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
        functions=[{"name": "identify_terms", "parameters": IDENTIFY_RESPONSE_SCHEMA}],
        function_call={"name": "identify_terms"},
        max_tokens=400,
    )
    args = response.choices[0].message.get("function_call", {}).get("arguments", "{}")
    return json.loads(args)


def _fetch_details(vocab: List[str], grammar: List[str], factory, target_lang: str, api_key: str) -> Dict:
    """Ask OpenAI for detailed explanations of given terms."""
    prompt = factory.create_prompt(target_lang)
    message = prompt
    if vocab:
        message += "\nVocabulary:\n" + "\n".join(vocab)
    if grammar:
        message += "\nGrammar:\n" + "\n".join(grammar)

    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message}],
        functions=[{"name": "deliver_report", "parameters": ITEM_SCHEMA}],
        function_call={"name": "deliver_report"},
        max_tokens=500,
    )
    args = response.choices[0].message.get("function_call", {}).get("arguments", "{}")
    return json.loads(args)


def analyze_image(
    title: str,
    target_lang: str,
    report_lang: str,
    api_key: str,
    identify_func: Optional[Callable[[str, Any, str, str], Dict]] = None,
    fetch_func: Optional[Callable[[List[str], List[str], Any, str, str], Dict]] = None,
) -> Dict:
    """Process screenshot through OpenAI with optional custom steps.

    ``identify_func`` and ``fetch_func`` allow callers to inject mock
    implementations of :func:`_identify_terms` and :func:`_fetch_details`.
    """
    img_b64 = grab_window_image(title)
    factory = get_prompt_factory(report_lang)

    identify = identify_func or _identify_terms
    terms = identify(img_b64, factory, target_lang, api_key)

    cache = load_cache()
    vocab_cache = cache.get("vocabulary", {})
    grammar_cache = cache.get("grammar", {})

    new_vocab: List[str] = []
    new_grammar: List[str] = []
    for level_info in terms.values():
        if not level_info:
            continue
        for w in level_info.get("vocabulary", []):
            if w not in vocab_cache:
                new_vocab.append(w)
        for g in level_info.get("grammar", []):
            if g not in grammar_cache:
                new_grammar.append(g)

    details = {"vocabulary": [], "grammar": []}
    fetch = fetch_func or _fetch_details
    if new_vocab or new_grammar:
        details = fetch(new_vocab, new_grammar, factory, target_lang, api_key)
        for item in details.get("vocabulary", []):
            word = item.get("word")
            if word:
                vocab_cache[word] = item
        for item in details.get("grammar", []):
            point = item.get("grammar_point")
            if point:
                grammar_cache[point] = item
        cache["vocabulary"] = vocab_cache
        cache["grammar"] = grammar_cache
        save_cache(cache)

    result = {}
    for level, info in terms.items():
        if not info:
            result[level] = {"vocabulary": [], "grammar": []}
            continue
        vocab_list = [vocab_cache.get(w) for w in info.get("vocabulary", []) if w in vocab_cache]
        grammar_list = [grammar_cache.get(g) for g in info.get("grammar", []) if g in grammar_cache]
        result[level] = {"vocabulary": vocab_list, "grammar": grammar_list}

    return result
