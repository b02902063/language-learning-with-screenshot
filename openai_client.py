import io
import base64
import json
from typing import Dict
from PIL import ImageGrab
import pygetwindow as gw
import openai

from prompts import get_prompt_factory
from schema import RESPONSE_SCHEMA


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


def analyze_image(title: str, target_lang: str, report_lang: str, api_key: str) -> Dict:
    """Send screenshot to OpenAI and return parsed response."""
    img_b64 = grab_window_image(title)
    factory = get_prompt_factory(report_lang)
    prompt = factory.create_prompt(target_lang)

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
        functions=[{"name": "deliver_report", "parameters": RESPONSE_SCHEMA}],
        function_call={"name": "deliver_report"},
        max_tokens=500,
    )
    args = response.choices[0].message.get("function_call", {}).get("arguments", "{}")
    return json.loads(args)
