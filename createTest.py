import sqlite3
import random
import re
from pyarabic.araby import strip_tashkeel, tokenize

db_path = "Quran"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def find_similar_words(word, all_words):
    base_word = strip_tashkeel(word)
    similar = [w for w in all_words if strip_tashkeel(w).startswith(base_word[:3])]
    return random.sample(similar, min(3, len(similar)))

def generate_smart_questions(table_name, field_name, num_questions=10):
    cursor.execute(f"SELECT {field_name} FROM {table_name}")
    rows = cursor.fetchall()
    
    questions = []
    all_words = []
    
    for row in rows:
        text = row[0]
        words = re.findall(r'\b[\u0621-\u064A\u064B-\u0652]+\b', text)
        all_words.extend(words)
    
    all_words = list(set(all_words))
    
    for row in rows:
        text = row[0]
        words = re.findall(r'\b[\u0621-\u064A\u064B-\u0652]+\b', text)
        
        if len(words) > 2:
            blank_word = random.choice(words)
            blank_text = text.replace(blank_word, "_____", 1)
            
            similar_words = find_similar_words(blank_word, all_words)
            options = [blank_word] + similar_words
            random.shuffle(options)
            
            questions.append({
                "question": blank_text,
                "answer": blank_word,
                "options": options
            })
            
        if len(questions) >= num_questions:
            break
    
    return questions

questions = generate_smart_questions("AyeMatn", "Aye", num_questions=5)

for i, q in enumerate(questions, start=1):
    print(f"سوال {i}: {q['question']}")
    for j, option in enumerate(q['options'], start=1):
        print(f"{j}. {option}")
    print(f"پاسخ صحیح: {q['answer']}")
    print("-" * 40)

conn.close()