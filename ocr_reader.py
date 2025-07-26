import base64
import io
from typing import List, Optional
from threading import Thread, Event, Lock

from PIL import Image
import pytesseract

from openai_client import grab_window_image


class OcrReader:
    """Read text from a window using Tesseract OCR."""

    def __init__(self, window_title: str, *, lang: str = "eng"):
        self.window_title = window_title
        self.lang = lang

    def read(self) -> List[str]:
        """Capture the window and return recognized text lines."""
        img_b64 = grab_window_image(self.window_title)
        img_bytes = base64.b64decode(img_b64)
        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img, lang=self.lang)
        return [line.strip() for line in text.splitlines() if line.strip()]

    def read_b64(self, img_b64: str) -> List[str]:
        """Return recognized text lines from a base64 image string."""
        img_bytes = base64.b64decode(img_b64)
        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img, lang=self.lang)
        return [line.strip() for line in text.splitlines() if line.strip()]


class PeriodicOcrCollector:
    """Run OCR periodically in a background thread and collect results."""

    def __init__(self, reader: OcrReader):
        self.reader = reader
        self._collected: List[str] = []
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._lock = Lock()

    def _run(self, interval: float) -> None:
        while not self._stop_event.is_set():
            try:
                lines = self.reader.read()
                with self._lock:
                    self._collected.extend(lines)
            except Exception as e:
                print(f"OCR error: {e}")
            self._stop_event.wait(interval)

    def start(self, interval: float) -> None:
        """Start background OCR with the given interval in seconds."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._run, args=(interval,), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            self._thread = None

    def collect(self) -> List[str]:
        """Return collected lines and clear the buffer."""
        with self._lock:
            result = list(self._collected)
            self._collected.clear()
        return result
