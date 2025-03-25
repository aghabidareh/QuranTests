import sqlite3
import random
import re

def create_question(start, end, count):
    conn = sqlite3.connect('Quran')
    cursor = conn.cursor()

    cursor.execute('SELECT Id, Aye FROM AyeMatn WHERE Id BETWEEN ? AND ?', (start, end))
    verses = cursor.fetchall()

    if not verses:
        return "هیچ آیهای در این محدوده یافت نشد."

    all_words = []
    for verse in verses:
        all_words.extend(verse[1].split())

    unique_words = list(set(all_words))
    questions = []

    def find_similar_words(word):
        if len(word) < 3:
            return []

        first_two = word[:2]
        last_two = word[-2:]
        middle_part = word[1:-1] if len(word) > 3 else ''  # قسمت میانی

        pattern = (
            rf"\b({first_two}\w+|\w+{last_two}|\w*{middle_part}\w*)\b"
        )

        return [w for w in unique_words if re.match(pattern, w) and w != word]

    for _ in range(count):
        verse = random.choice(verses)
        verse_id, aye_text = verse
        words = aye_text.split()

        valid_words = [word for word in words if len(word) > 2]
        if not valid_words:
            continue

        correct_word = random.choice(valid_words)
        blank_index = words.index(correct_word)

        distractors = find_similar_words(correct_word)

        if len(distractors) < 3:
            additional_candidates = [
                w for w in unique_words if w != correct_word and abs(len(w) - len(correct_word)) <= 1
            ]
            distractors += random.sample(additional_candidates, min(3 - len(distractors), len(additional_candidates)))

        options = distractors[:3] + [correct_word]
        random.shuffle(options)

        question_text = " ".join(["______" if i == blank_index else word for i, word in enumerate(words)])

        questions.append({
            "verse_id": verse_id,
            "question": question_text,
            "options": options,
            "answer": correct_word
        })

    conn.close()
    return questions