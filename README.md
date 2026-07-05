# Language Helper

Language Helper is a small desktop application for collecting and storing English words while reading.

The main idea is simple:

1. Select an English word in any application.
2. Press a global hotkey.
3. The word is automatically added to your personal dictionary.
4. Later, open the app and review your saved words.

The app automatically tries to get a Russian translation and an English definition for each word.

---

## Features

- Add words manually through the app window.
- Add selected words using a global hotkey.
- Automatically translate English words into Russian.
- Automatically fetch English definitions.
- Store words locally in a JSON file.
- Search saved words.
- View word details.
- Delete words from the dictionary.
- Hide and show the app window with a hotkey.

---

## Hotkeys

| Hotkey | Action |
|---|---|
| `Ctrl + Alt + W` | Add the currently selected word |
| `Ctrl + Alt + L` | Show or hide the app window |

The application must be running for the hotkeys to work.

---

## Project Structure

```text
language_helper/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── words.example.json
└── words.json
```

### Main files

- `main.py` — main application code.
- `requirements.txt` — project dependencies.
- `README.md` — project description.
- `.gitignore` — files ignored by Git.
- `words.example.json` — example dictionary structure.
- `words.json` — local personal dictionary file.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/robotchikarno2000-hash/language-helper
cd language-helper
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the App

Run:

```bash
python main.py
```

After launch, the app window will open.

You can also hide the window and continue using the hotkey in the background.

---

## How to Use

### Add a word manually

1. Open the app.
2. Type an English word into the input field.
3. Click **Add manually**.
4. The app will try to get a translation and definition automatically.
5. The word will be saved to `words.json`.

### Add a selected word with a hotkey

1. Open any text, website, PDF, or document.
2. Select one English word.
3. Press `Ctrl + Alt + W`.
4. The word will be copied, translated, defined, and saved automatically.

### Show or hide the app

Press:

```text
Ctrl + Alt + L
```

---

## Data Format

Words are stored locally in `words.json`.

Example word card:

```json
[
    {
        "word": "apple",
        "translation": "яблоко",
        "definition": "A common, round fruit produced by the tree Malus domestica.",
        "example": "",
        "added_at": "2026-07-05 19:30:00"
    }
]
```

---

## Dependencies

This project uses:

- `deep-translator` — for automatic translation.
- `requests` — for fetching word definitions from an online dictionary API.
- `pynput` — for global hotkeys.
- `pyperclip` — for clipboard access.
- `tkinter` — for the graphical interface.

`tkinter` is usually included with Python by default.

---

## Notes

The app currently works best with English words.

Definitions are fetched from an online dictionary API, so an internet connection is required for automatic definitions.

Translations also require an internet connection.

If automatic translation or definition fails, the word can still be saved with empty fields.

---

## Privacy

The dictionary is stored locally on your computer in `words.json`.

If you publish this project on GitHub, it is recommended to add `words.json` to `.gitignore` and use `words.example.json` as a public example file.

Recommended `.gitignore` entries:

```gitignore
__pycache__/
*.pyc
.venv/
venv/
env/
.idea/
.vscode/
words.json
words_backup.json
```

---

## Current Version

```text
Version 0.2 — GUI + Hotkey Word Collector
```

---

## Future Ideas

Possible future improvements:

- Add spaced repetition.
- Add word learning mode.
- Add export to Anki.
- Add support for multiple languages.
- Add system tray mode.
- Add startup on Windows.
- Add SQLite storage.
- Add better UI design.
- Add editing for saved words.

---

## Author

Created as a first Python project for learning programming through a real personal-use application.