import json
import shutil
import string
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import pyperclip
import requests
from deep_translator import GoogleTranslator
from pynput import keyboard
from pynput.keyboard import Controller, Key


WORDS_FILE = Path("words.json")
BACKUP_FILE = Path("words_backup.json")

keyboard_controller = Controller()


def load_words():
    """
    Загружает слова из файла words.json.

    Если файла нет, возвращает пустой список.
    Если файл повреждён, возвращает пустой список.
    """
    if not WORDS_FILE.exists():
        return []

    try:
        with open(WORDS_FILE, "r", encoding="utf-8") as file:
            words = json.load(file)

        if not isinstance(words, list):
            return []

        return words

    except json.JSONDecodeError:
        return []


def backup_words_file():
    """
    Создаёт резервную копию words.json.
    """
    if WORDS_FILE.exists():
        shutil.copy(WORDS_FILE, BACKUP_FILE)


def save_words(words):
    """
    Сохраняет слова в файл words.json.
    """
    backup_words_file()

    with open(WORDS_FILE, "w", encoding="utf-8") as file:
        json.dump(words, file, ensure_ascii=False, indent=4)


def normalize_word(word):
    """
    Очищает слово:
    - убирает пробелы;
    - переводит в нижний регистр;
    - убирает знаки препинания по краям.
    """
    word = word.strip().lower()
    word = word.strip(string.punctuation)
    return word


def translate_word(word):
    """
    Переводит английское слово на русский.

    Если перевод не сработал, возвращает пустую строку.
    """
    try:
        translation = GoogleTranslator(source="en", target="ru").translate(word)

        if translation is None:
            return ""

        return translation.strip()

    except Exception:
        return ""


def get_definition(word):
    """
    Получает английское определение через Free Dictionary API.

    Если определение не найдено, возвращает пустую строку.
    """
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return ""

        data = response.json()

        definition = data[0]["meanings"][0]["definitions"][0]["definition"]

        if definition is None:
            return ""

        return definition.strip()

    except Exception:
        return ""


def word_already_exists(words, word):
    """
    Проверяет, есть ли слово уже в словаре.
    """
    for item in words:
        existing_word = item.get("word", "")
        existing_word = normalize_word(existing_word)

        if existing_word == word:
            return True

    return False


def create_word_card(word, example=""):
    """
    Создаёт карточку слова:
    - получает перевод;
    - получает definition;
    - добавляет дату.
    """
    translation = translate_word(word)
    definition = get_definition(word)

    new_word = {
        "word": word,
        "translation": translation,
        "definition": definition,
        "example": example,
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return new_word


def add_word_to_storage(word, example=""):
    """
    Добавляет слово в words.json.

    Возвращает:
    - success: True или False
    - message: сообщение для пользователя
    """
    word = normalize_word(word)

    if word == "":
        return False, "Пустое слово нельзя добавить."

    words = load_words()

    if word_already_exists(words, word):
        return False, f"Слово '{word}' уже есть в словаре."

    new_word = create_word_card(word, example)

    words.append(new_word)
    save_words(words)

    return True, f"Слово '{word}' добавлено."


def copy_selected_text():
    """
    Копирует выделенный текст через Ctrl+C и возвращает его.

    Важно:
    перед копированием очищает буфер обмена,
    чтобы случайно не взять старый текст.
    """
    try:
        pyperclip.copy("")
    except Exception:
        return ""

    time.sleep(0.1)

    with keyboard_controller.pressed(Key.ctrl):
        keyboard_controller.press("c")
        keyboard_controller.release("c")

    time.sleep(0.5)

    try:
        selected_text = pyperclip.paste()
    except Exception:
        return ""

    return selected_text.strip()


class LanguageHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Helper")
        self.root.geometry("900x700")

        self.words = []

        self.create_widgets()
        self.refresh_word_list()

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="Language Helper",
            font=("Arial", 22, "bold")
        )
        title_label.pack(pady=10)

        hotkey_label = tk.Label(
            self.root,
            text="F8 — добавить выделенное слово | F9 — показать/скрыть окно",
            font=("Arial", 11)
        )
        hotkey_label.pack(pady=5)

        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        self.word_entry = tk.Entry(input_frame, width=35, font=("Arial", 12))
        self.word_entry.grid(row=0, column=0, padx=5)

        add_button = tk.Button(
            input_frame,
            text="Добавить вручную",
            command=self.add_word_from_entry
        )
        add_button.grid(row=0, column=1, padx=5)

        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)

        self.search_entry = tk.Entry(search_frame, width=35, font=("Arial", 12))
        self.search_entry.grid(row=0, column=0, padx=5)

        search_button = tk.Button(
            search_frame,
            text="Найти",
            command=self.search_words
        )
        search_button.grid(row=0, column=1, padx=5)

        reset_button = tk.Button(
            search_frame,
            text="Показать всё",
            command=self.refresh_word_list
        )
        reset_button.grid(row=0, column=2, padx=5)

        self.words_listbox = tk.Listbox(
            self.root,
            width=70,
            height=14,
            font=("Arial", 12)
        )
        self.words_listbox.pack(pady=10)

        self.words_listbox.bind("<<ListboxSelect>>", self.show_selected_word_details)

        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=5)

        delete_button = tk.Button(
            buttons_frame,
            text="Удалить выбранное слово",
            command=self.delete_selected_word
        )
        delete_button.grid(row=0, column=0, padx=5)

        refresh_button = tk.Button(
            buttons_frame,
            text="Обновить список",
            command=self.refresh_word_list
        )
        refresh_button.grid(row=0, column=1, padx=5)

        hide_button = tk.Button(
            buttons_frame,
            text="Скрыть окно",
            command=self.hide_window
        )
        hide_button.grid(row=0, column=2, padx=5)

        self.details_text = tk.Text(
            self.root,
            width=95,
            height=13,
            font=("Arial", 11),
            wrap="word"
        )
        self.details_text.pack(pady=10)

    def refresh_word_list(self):
        """
        Обновляет список слов в интерфейсе.
        """
        self.words = load_words()

        self.words_listbox.delete(0, tk.END)

        for item in self.words:
            word = item.get("word", "")
            translation = item.get("translation", "")
            self.words_listbox.insert(tk.END, f"{word} — {translation}")

        self.details_text.delete("1.0", tk.END)

    def add_word_from_entry(self):
        """
        Добавляет слово из поля ввода.
        """
        word = self.word_entry.get()
        word = normalize_word(word)

        success, message = add_word_to_storage(word)

        if success:
            self.word_entry.delete(0, tk.END)
            self.refresh_word_list()
            messagebox.showinfo("Готово", message)
        else:
            messagebox.showwarning("Внимание", message)

    def add_word_from_hotkey(self):
        """
        Добавляет слово, выделенное в другой программе.

        Это отладочная версия:
        она печатает в терминал, что происходит.
        """
        print("HOTKEY WORKS: F8 was pressed")

        selected_text = copy_selected_text()
        print(f"Copied text: '{selected_text}'")

        word = normalize_word(selected_text)
        print(f"Normalized word: '{word}'")

        if word == "":
            messagebox.showwarning(
                "Ничего не выделено",
                "Выдели одно английское слово и нажми F8."
            )
            return

        if " " in word or "\n" in word or "\t" in word:
            messagebox.showwarning(
                "Слишком много текста",
                f"Выделено не одно слово:\n\n{word}"
            )
            return

        print("Adding word to storage...")

        success, message = add_word_to_storage(word)

        self.refresh_word_list()

        print(message)

        if success:
            messagebox.showinfo("Слово добавлено", message)
        else:
            messagebox.showwarning("Внимание", message)

    def search_words(self):
        """
        Ищет слова по:
        - слову;
        - переводу;
        - definition;
        - example.
        """
        query = normalize_word(self.search_entry.get())

        if query == "":
            self.refresh_word_list()
            return

        words = load_words()
        found_words = []

        for item in words:
            word = item.get("word", "").lower()
            translation = item.get("translation", "").lower()
            definition = item.get("definition", "").lower()
            example = item.get("example", "").lower()

            if (
                query in word
                or query in translation
                or query in definition
                or query in example
            ):
                found_words.append(item)

        self.words = found_words
        self.words_listbox.delete(0, tk.END)

        for item in found_words:
            word = item.get("word", "")
            translation = item.get("translation", "")
            self.words_listbox.insert(tk.END, f"{word} — {translation}")

        self.details_text.delete("1.0", tk.END)

    def show_selected_word_details(self, event=None):
        """
        Показывает подробную информацию о выбранном слове.
        """
        selection = self.words_listbox.curselection()

        if not selection:
            return

        index = selection[0]
        item = self.words[index]

        word = item.get("word", "")
        translation = item.get("translation", "")
        definition = item.get("definition", "")
        example = item.get("example", "")
        added_at = item.get("added_at", "")

        text = (
            f"Word: {word}\n"
            f"Translation: {translation}\n\n"
            f"Definition:\n{definition if definition else '—'}\n\n"
            f"Example:\n{example if example else '—'}\n\n"
            f"Added at: {added_at}"
        )

        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, text)

    def delete_selected_word(self):
        """
        Удаляет выбранное слово.
        """
        selection = self.words_listbox.curselection()

        if not selection:
            messagebox.showwarning("Внимание", "Сначала выбери слово.")
            return

        index = selection[0]
        selected_item = self.words[index]
        selected_word = selected_item.get("word", "")

        confirmation = messagebox.askyesno(
            "Подтверждение",
            f"Точно удалить слово '{selected_word}'?"
        )

        if not confirmation:
            return

        all_words = load_words()
        new_words = []

        for item in all_words:
            if item.get("word", "") != selected_word:
                new_words.append(item)

        save_words(new_words)

        self.refresh_word_list()
        messagebox.showinfo("Готово", f"Слово '{selected_word}' удалено.")

    def hide_window(self):
        """
        Скрывает окно программы.
        """
        self.root.withdraw()

    def show_window(self):
        """
        Показывает окно программы.
        """
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.refresh_word_list()

    def toggle_window(self):
        """
        Показывает или скрывает окно программы.
        """
        if self.root.state() == "withdrawn":
            self.show_window()
        else:
            self.hide_window()


def start_hotkey_listener(app):
    """
    Запускает глобальные горячие клавиши.

    F8 — добавить выделенное слово.
    F9 — показать или скрыть окно.
    """

    def add_selected_word():
        app.root.after(0, app.add_word_from_hotkey)

    def toggle_window():
        app.root.after(0, app.toggle_window)

    hotkeys = keyboard.GlobalHotKeys({
        "<f8>": add_selected_word,
        "<f9>": toggle_window
    })

    hotkeys.start()

    return hotkeys


def main():
    root = tk.Tk()
    app = LanguageHelperApp(root)

    hotkey_listener = start_hotkey_listener(app)

    # Пока отлаживаем программу, окно лучше оставлять видимым.
    # Когда всё заработает, можно раскомментировать строку ниже:
    # root.withdraw()

    try:
        root.mainloop()
    finally:
        hotkey_listener.stop()


if __name__ == "__main__":
    main()