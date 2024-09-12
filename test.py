import pymorphy2
import pandas as pd

# Инициализируем морфологический анализатор
morph = pymorphy2.MorphAnalyzer()

# Исходный список районов
districts = ['Абайский район', 'поселок Топар', 'Шилектинский сельский округ', '']

def restore_case(word, original_word):
    """
    Функция для восстановления регистра слова.
    Если исходное слово начиналось с заглавной буквы, результат тоже должен быть с заглавной.
    """
    if original_word.istitle():
        return word.capitalize()  # Восстанавливаем заглавную букву
    return word

def decline_phrase(phrase):
    """
    Функция для склонения фразы, состоящей из нескольких слов, в родительный падеж.
    """
    words = phrase.split()  # Разбиваем фразу на отдельные слова
    declined_words = []
    
    for word in words:
        parsed_word = morph.parse(word)[0]  # Парсим слово
        # Пытаемся склонить слово в родительный падеж
        declined_word = parsed_word.inflect({'gent'})
        
        # Проверка, удалось ли просклонять слово
        if declined_word:
            # Восстанавливаем регистр исходного слова
            final_word = restore_case(declined_word.word, word)
        else:
            final_word = word  # Если склонить не удалось, оставляем как есть
        
        declined_words.append(final_word)
    
    return ' '.join(declined_words)

# Применяем склонение к каждой фразе
districts_genitive = [decline_phrase(district) for district in districts]

# Сохраняем результат в DataFrame
df = pd.DataFrame(districts_genitive, columns=['Родительный падеж'])

# Выводим DataFrame
print(df)