import pymorphy2
import pandas as pd

# Инициализируем морфологический анализатор
morph = pymorphy2.MorphAnalyzer()

# Исходный список районов
districts = ['Абайский район', 'поселок Топар', 'Шилектинский сельский округ', 'Бухар-Жырауский район']

def restore_case(word, original_word):
    """
    Функция для восстановления регистра слова.
    Если исходное слово начиналось с заглавной буквы, результат тоже должен быть с заглавной.
    """
    if original_word.istitle():
        return word.capitalize()  # Восстанавливаем заглавную букву
    return word

def decline_word(word):
    """
    Функция для склонения одного слова.
    Обрабатывает случаи с дефисом, чтобы склонить каждую часть слова.
    """
    if '-' in word:  # Если в слове есть дефис
        parts = word.split('-')  # Разделяем слово на части
        declined_parts = []
        for part in parts:
            parsed_word = morph.parse(part)[0]  # Парсим часть слова
            declined_word = parsed_word.inflect({'gent'})  # Склоняем в родительный падеж
            if declined_word:
                final_word = restore_case(declined_word.word, part)
            else:
                final_word = part  # Если склонение не удалось, оставляем как есть
            declined_parts.append(final_word)
        return '-'.join(declined_parts)  # Склеиваем части обратно через дефис
    else:
        parsed_word = morph.parse(word)[0]  # Парсим слово
        declined_word = parsed_word.inflect({'gent'})  # Склоняем в родительный падеж
        if declined_word:
            return restore_case(declined_word.word, word)
        return word  # Если склонение не удалось, возвращаем исходное слово

def decline_phrase(phrase):
    """
    Функция для склонения фразы, состоящей из нескольких слов, в родительный падеж.
    """
    words = phrase.split()  # Разбиваем фразу на отдельные слова
    declined_words = [decline_word(word) for word in words]  # Склоняем каждое слово
    return ' '.join(declined_words)

# Применяем склонение к каждой фразе
districts_genitive = [decline_phrase(district) for district in districts]

# Сохраняем результат в DataFrame
df = pd.DataFrame(districts_genitive, columns=['Родительный падеж'])

# Выводим DataFrame
print(df)
