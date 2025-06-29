# Language Learning With Screenshot

This project provides a small PyQt application that captures a screenshot of a user-selected window and sends it to the OpenAI API for vocabulary and grammar analysis. The API response is filtered on the client according to the learner's language level.  The response structure is enforced using an OpenAI function with a JSON Schema describing vocabulary and grammar items.

## Features
- Select target language and your proficiency level.
- Choose a window for screenshot capture.
- Capture and analyze the screenshot with OpenAI.
- Filter displayed vocabulary by difficulty without requerying the API.
- Settings dialog stores your API key, interface language and the language used for AI generated reports.
- OpenAI responses contain all level sections (N1–N5) even when empty. Vocabulary items include `word`, `reading`, `definition`, `pos`, `related`, and `examples`, while `conjugation` and `transitivity` may be `null`.

## Requirements
See `requirements.txt` for the list of Python dependencies. Install them using:

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

At startup a settings dialog lets you configure the OpenAI API key and choose interface and report languages. Enable "Remember API Key" if you want it stored locally for the next run.

The main window then appears with options to choose your language, level and window. After capturing a screenshot, the analysis results are shown in a text box and can be filtered with the slider.

### Test Mode

Enable **Test Mode** on the settings dialog to run the application without contacting the OpenAI service. In this mode the identify and detail steps are mocked so fixed vocabulary and grammar items are returned, letting you try the interface without an API key.

The code is organized into small modules: `config.py` for settings and translation utilities, `prompts.py` for prompt factories, `schema.py` with the JSON Schema, `openai_client.py` for communicating with OpenAI, and `ui.py` for the PyQt user interface.

Language names and their level lists are defined in `language_config.json`. Edit this file to customize supported languages.
