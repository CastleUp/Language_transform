import pymorphy2
import pandas as pd
from request import connect_to_db, fetch_data_from_db, create_declined_table, insert_declined_data

# Инициализация морфологического анализатора для русского языка
morph = pymorphy2.MorphAnalyzer()

# Функция для склонения слов на русском языке
def decline_russian(phrase):
    stop_words = ['село', 'район', 'поселок', 'г.', 'город']

    def restore_case(word, original_word):
        """Восстановление регистра."""
        if original_word.istitle():
            return word.capitalize()
        return word

    def replace_e_with_e(word):
        """Запрет на замену 'е' на 'ё'."""
        return word.replace('ё', 'е')

    def process_word(word):
        parsed_word = morph.parse(word)[0]
        declined_word = parsed_word.inflect({'gent'})
        if declined_word:
            return restore_case(replace_e_with_e(declined_word.word), word)
        else:
            return word

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
            declined_words.append(process_word(word))
            declined_words.append(words[i + 1].capitalize())
            skip_next = True
        elif skip_next:
            skip_next = False
        else:
            declined_words.append(process_word(word))
    
    return ' '.join(declined_words)

# Функция для склонения слов на казахском языке
def decline_kazakh(phrase):
    words = phrase.split()
    
    # Обрабатываем последнее слово или группу слов с дефисом
    last_word = words[-1]
    
    if '-' in last_word:  # Если есть дефис
        parts = last_word.split('-')
        declined_last_part = add_kazakh_genitive(parts[-1])  # Склоняем только последнюю часть
        declined_last_word_full = '-'.join(parts[:-1] + [declined_last_part])
    else:
        declined_last_word_full = add_kazakh_genitive(last_word)

    return ' '.join(words[:-1] + [declined_last_word_full])

# Функция для добавления окончания родительного падежа на казахском
def add_kazakh_genitive(word):
    def is_vowel(char):
        return char in 'аеёиоуыэюяіүұө'

    def is_front_vowel(char):
        return char in 'еіүө'

    def is_back_vowel(char):
        return char in 'аоұы'

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
                return word + 'тің' if last_letter in 'қкптсшч' else word + 'нің'
            elif is_back_vowel(last_vowel):
                return word + 'тың' if last_letter in 'қкптсшч' else word + 'ның'
        return word

# Основная функция для обработки данных
def process_districts():
    conn = connect_to_db()

    # Получаем данные из базы данных
    df = fetch_data_from_db(conn)

    # Склоняем названия районов на русском и казахском
    df['name_ru_declined'] = [decline_russian(district) for district in df['name_ru'].tolist()]
    df['name_kk_declined'] = [decline_kazakh(district) for district in df['name_kk'].tolist()]
    
    # Подготовка данных для вставки в новую таблицу
    data = list(df[['id', 'code', 'name_ru', 'name_ru_declined', 'name_kk', 'name_kk_declined']].itertuples(index=False, name=None))

    # Создаем таблицу для склоненных названий
    #create_declined_table(conn)

    # Вставляем данные в таблицу
    #insert_declined_data(conn, data)

    conn.close()
    print("Данные успешно сохранены в новую таблицу.")
    print(df)

if __name__ == "__main__":
    process_districts()
