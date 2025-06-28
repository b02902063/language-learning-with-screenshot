# Language Learning With Screenshot

This project provides a small PyQt application that captures a screenshot of a user-selected process and sends it to the OpenAI API for vocabulary and grammar analysis. The API response is filtered on the client according to the learner's language level.

## Features
- Select target language and your proficiency level.
- Choose a running process for screenshot capture.
- Capture and analyze the screenshot with OpenAI.
- Filter displayed vocabulary by difficulty without requerying the API.

## Requirements
See `requirements.txt` for the list of Python dependencies. Install them using:

```bash
pip install -r requirements.txt
```

Set the `OPENAI_API_KEY` environment variable before running the application.

## Running

```bash
python main.py
```

The UI will appear with options to choose your language, level and process. After capturing a screenshot, the analysis results are shown in a text box and can be filtered with the slider.
