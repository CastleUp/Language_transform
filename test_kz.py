import pymorphy2
import pandas as pd
import re
from request import connect_to_db, fetch_data_from_db  # Импортируем функции из request.py

# Инициализируем морфологический анализатор для русского языка
morph = pymorphy2.MorphAnalyzer()

# Подключаемся к базе данных и загружаем районы
conn = connect_to_db()
districts_ru = fetch_data_from_db(conn)  # Получаем список районов из БД
districts_kk = ['Абай ауданы', 'Топар ауылы', 'Шілде ауылдық округі', 'Бұқар-Жырау ауданы']

# Функция для выбора языка
def select_language():
    print("Выберите язык:")
    print("1: Русский")
    print("2: Казахский")
    choice = input("Введите номер (1 или 2): ")
    return 'ru' if choice == '1' else 'kk'

# Вспомогательная функция для определения гармонии гласных
def is_vowel(char):
    return char in 'аеёиоуыэюяіүұө'

def is_front_vowel(char):
    """Определяет, является ли гласный переднего ряда."""
    return char in 'еіүө'

def is_back_vowel(char):
    """Определяет, является ли гласный заднего ряда."""
    return char in 'аоұы'

# Функция для склонения слов на казахском языке
def decline_kazakh(phrase):
    """
    Склонение казахских слов в родительный падеж.
    """
    words = phrase.split()
    
    # Обрабатываем последнее слово или группу слов с дефисом
    last_word = words[-1]
    
    if '-' in last_word:  # Если есть дефис, обрабатываем только последнее слово перед дефисом
        parts = last_word.split('-')
        declined_last_part = parts[-1]
        declined_last_word = add_kazakh_genitive(declined_last_part)  # Склоняем только последнюю часть
        declined_last_word_full = '-'.join(parts[:-1] + [declined_last_word])
    else:
        declined_last_word_full = add_kazakh_genitive(last_word)  # Склоняем слово

    return ' '.join(words[:-1] + [declined_last_word_full])

def add_kazakh_genitive(word):
    """
    Добавление окончания родительного падежа к казахскому слову.
    """
    last_letter = word[-1]
    if is_vowel(last_letter):
        if is_front_vowel(last_letter):
            return word + 'нің'
        else:
            return word + 'ның'
    else:
        root_vowels = [char for char in word if is_vowel(char)]
        if root_vowels:
            last_vowel = root_vowels[-1]
            if is_front_vowel(last_vowel):
                if last_letter in 'қкптсшч':
                    return word + 'тің'
                else:
                    return word + 'нің'
            elif is_back_vowel(last_vowel):
                if last_letter in 'қкптсшч':
                    return word + 'тың'
                else:
                    return word + 'ның'
        return word  # Если не можем определить, возвращаем слово без изменений

# Функция для склонения фраз на русском языке
def decline_russian(phrase):
    """
    Склонение фраз на русском языке в родительный падеж с учетом дефисов, точек и маркеров "село", "район", "поселок", "г.", "город".
    """
    stop_words = ['село', 'район', 'поселок', 'округ', 'город']

    def restore_case(word, original_word):
        if original_word.istitle():
            return word.capitalize()
        return word

    def replace_e_with_e(word):
        return re.sub(r'ё', 'е', word)

    def process_word(word):
        parsed_word = morph.parse(word)[0]
        declined_word = parsed_word.inflect({'gent'})
        if declined_word:
            return restore_case(replace_e_with_e(declined_word.word), word)
        else:
            return word
    
# Обрабатываем фразы с точками
    if '.' in phrase:
        parts = phrase.split('.')
        first_part = parts[0] + '.'
        last_part = process_word(parts[1].strip())
        return first_part + last_part

    words = phrase.split()
    declined_words = []
    
    skip_next = False
    for i, word in enumerate(words):
        if word.lower() in stop_words and i + 1 < len(words):
            declined_words.append(process_word(word))  # Склоняем слово из списка stop_words
            declined_words.append(words[i + 1])  # Не склоняем следующее слово
            skip_next = True  # Пропускаем следующее слово
        elif skip_next:
            skip_next = False  # Пропускаем это слово, т.к. оно не должно склоняться
        else:
            declined_words.append(process_word(word))
    
    return ' '.join(declined_words)

# Основная функция для склонения фраз в зависимости от языка
def decline_districts(districts, language):
    if language == 'ru':
        return [decline_russian(district) for district in districts]
    elif language == 'kk':
        return [decline_kazakh(district) for district in districts]

# Выбор языка пользователем
language = select_language()

# Выбираем соответствующий список районов
districts = districts_ru if language == 'ru' else districts_kk

# Склоняем районы в выбранном языке
declined_districts = decline_districts(districts, language)

# Сохраняем результат в DataFrame и выводим
df = pd.DataFrame(declined_districts, columns=['Родительный падеж'])
print(df)

# Сохранение в CSV файл
df.to_csv('declined_districts.csv', index=False, encoding='utf-8-sig')
