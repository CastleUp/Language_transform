import pymorphy2
import pandas as pd
from request import connect_to_db, fetch_data_from_db, create_declined_table, insert_declined_data

# Инициализация морфологического анализатора для русского языка
morph = pymorphy2.MorphAnalyzer()

# Функция для склонения слов на русском языке
def decline_russian(phrase):
    stop_words = ['село', 'район', 'поселок', 'г.', 'город', 'область', 'п.', 'с.']

    def restore_case(word, original_word):
        """Восстановление регистра."""
        if original_word.istitle():
            return word.capitalize()
        elif original_word.isupper():
            return word.upper()
        return word

    def replace_e_with_e(word):
        """Запрет на замену 'е' на 'ё'."""
        return word.replace('ё', 'е')

    def process_word(word, original_word):
        """Склоняем одно слово и восстанавливаем его регистр."""
        if original_word.isupper():  # Если это аббревиатура, не склоняем
            return original_word
        parsed_word = morph.parse(word)[0]
        declined_word = parsed_word.inflect({'gent'})
        if declined_word:
            return restore_case(replace_e_with_e(declined_word.word), original_word)
        else:
            return word

    def process_hyphenated_word(hyphenated_word):
        """Обрабатываем слова через дефис."""
        parts = hyphenated_word.split('-')
        declined_parts = [process_word(part, original_part) for part, original_part in zip(parts, hyphenated_word.split('-'))]
        return '-'.join(declined_parts)

    # Обрабатываем фразы с точками
    if '.' in phrase:
        parts = phrase.split('.')
        first_part = parts[0] + '.'
        last_part = parts[1].strip().capitalize()  # Не склоняем слово после точки
        return first_part + last_part

    words = phrase.split()
    declined_words = []
    
    skip_next = False
    for i, word in enumerate(words):
        if word.lower() in stop_words and i + 1 < len(words):
            # Добавляем слово из стоп-листа, но не склоняем следующее
            declined_words.append(process_word(word, word))  # Склоняем слово из стоп-листа
            declined_words.append(words[i + 1].capitalize())  # Сохраняем следующее слово без изменений, с заглавной буквы
            skip_next = True
        elif skip_next:
            skip_next = False
        elif '-' in word:  # Обрабатываем дефисные слова
            declined_words.append(process_hyphenated_word(word))
        else:
            declined_words.append(process_word(word, word))
    
    return ' '.join(declined_words)



# Функция для склонения слов на казахском языке
def decline_kazakh(phrase):
    """
    Склонение казахских слов в родительный падеж.
    """
    # Проверка на пустую строку
    if not phrase or phrase.strip() == '':
        return phrase
    
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
    insert_declined_data(conn, data)
    
    conn.close()
    print("Данные успешно сохранены в новую таблицу.")
    print(df)



if __name__ == "__main__":
    process_districts()
