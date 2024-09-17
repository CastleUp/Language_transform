import pymorphy2
import pandas as pd
from request import connect_to_db, fetch_data_from_db, create_declined_table, insert_declined_data

# Инициализируем морфологический анализатор для русского языка
morph = pymorphy2.MorphAnalyzer()

# Функция для склонения фраз на русском языке
def decline_russian(phrase):
    """
    Склонение фраз на русском языке в родительный падеж с учетом дефисов и маркеров.
    """
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
        """Склоняем одно слово и восстанавливаем его регистр."""
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
            declined_words.append(process_word(word))
            declined_words.append(words[i + 1].capitalize())
            skip_next = True
        elif skip_next:
            skip_next = False
        else:
            declined_words.append(process_word(word))
    
    return ' '.join(declined_words)

# Функция для склонения и записи данных в базу
def process_districts():
    conn = connect_to_db()

    # Получаем данные из базы данных
    df = fetch_data_from_db(conn)

    # Склоняем названия районов
    df['name_ru_declined'] = [decline_russian(district) for district in df['name_ru'].tolist()]
    print(df)

    # Подготовка данных для вставки в новую таблицу
    data = list(df[['id', 'name_ru', 'name_ru_declined']].itertuples(index=False, name=None))

    # Создаем таблицу для склоненных названий
    create_declined_table(conn)

    # Вставляем данные в таблицу
    insert_declined_data(conn, data)

    conn.close()
    print("Данные успешно сохранены в новую таблицу.")

if __name__ == "__main__":
    process_districts()
