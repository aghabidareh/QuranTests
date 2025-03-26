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

    def get_root(word):
        word = ar.strip_tashkeel(word)
        word = word.replace("ي", "ی").replace("ك", "ک")
        word = re.sub(r'^(ال|ب|ف|ك|ل|و|س)', '', word)
        word = re.sub(r'(ات|ون|ين|ة|ي|ه|ا)$', '', word)
        return word

    def find_similar_words(word):
        word_root = get_root(word)
        pattern = rf"\b{word[:2]}\w*\b"
        similar_words = [w for w in unique_words if re.match(pattern, w) and w != word]

        root_words = [w for w in unique_words if get_root(w) == word_root and w != word]

        return list(set(similar_words + root_words))

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