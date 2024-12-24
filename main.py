import sqlite3
import random
import re
from pyarabic.araby import strip_tashkeel, tokenize, is_tashkeel

source_db = "Quran"
conn_source = sqlite3.connect(source_db)
cursor_source = conn_source.cursor()

destination_db = "Questions"
conn_dest = sqlite3.connect(destination_db)
cursor_dest = conn_dest.cursor()

query = """
CREATE TABLE IF NOT EXISTS Questions (
    id_Aye INTEGER,
    question TEXT NOT NULL,
    option_1 TEXT NOT NULL,
    option_2 TEXT NOT NULL,
    option_3 TEXT NOT NULL,
    option_4 TEXT NOT NULL,
    true_option TEXT NOT NULL,
    PRIMARY KEY (id_Aye, question)
)
"""
cursor_dest.execute(query)
conn_dest.commit()

def get_key_words(words):
    key_words = []
    for word in words:
        if len(word) > 3 and not is_tashkeel(word):
            key_words.append(word)
    return key_words


def find_similar_words(word, all_words):
    base_word = strip_tashkeel(word)
    similar = [w for w in all_words if strip_tashkeel(w).startswith(base_word[:3]) and w != word]
    return similar


def generate_and_store_questions(source_table, source_field, questions_per_verse=3):
    cursor_source.execute(f"SELECT rowid, {source_field} FROM {source_table}")
    rows = cursor_source.fetchall()

    all_words = []
    # آماده‌سازی تمامی کلمات
    for row in rows:
        text = row[1]
        words = re.findall(r'\b[\u0621-\u064A\u064B-\u0652]+\b', text)
        all_words.extend(words)

    all_words = list(set(all_words))  # حذف تکراری‌ها

    for row in rows:
        row_id, text = row
        words = re.findall(r'\b[\u0621-\u064A\u064B-\u0652]+\b', text)

        key_words = get_key_words(words)

        used_words = set()

        # تولید چندین سوال از هر آیه
        for _ in range(questions_per_verse):
            # انتخاب کلمه برای جاخالی
            available_words = [w for w in key_words if w not in used_words]
            if not available_words:
                break

            blank_word = random.choice(available_words)
            used_words.add(blank_word)
            blank_text = text.replace(blank_word, "_____", 1)

            similar_words = find_similar_words(blank_word, all_words)

            while len(similar_words) < 3:
                random_word = random.choice(all_words)
                if random_word not in similar_words and random_word != blank_word:
                    similar_words.append(random_word)

            options = [blank_word] + similar_words[:3]
            random.shuffle(options)

            cursor_dest.execute("""
            INSERT INTO Questions (id_Aye, question, option_1, option_2, option_3, option_4, true_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (row_id, blank_text, options[0], options[1], options[2], options[3], blank_word))

    conn_dest.commit()

generate_and_store_questions("AyeMatn", "Aye", questions_per_verse=5)

conn_source.close()
conn_dest.close()
