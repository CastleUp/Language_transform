import pymorphy2
import pandas as pd

# Инициализируем морфологический анализатор для русского языка
morph = pymorphy2.MorphAnalyzer()

# Списки районов на русском и казахском языках
districts_ru = ['Абайский район', 'поселок Топар', 'Шилектинский сельский округ', 'Бухар-Жырауский район']
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
    # Склонять нужно только последнее слово (после дефиса слово не изменяется)
    words = phrase.split()
    
    # Обрабатываем последнее слово или группу слов с дефисом
    last_word = words[-1]
    
    if '-' in last_word:  # Если есть дефис, обрабатываем только последнее слово перед дефисом
        parts = last_word.split('-')
        declined_last_part = parts[-1]
        declined_last_word = add_kazakh_genitive(declined_last_part)  # Склоняем только последнюю часть
        # Оставляем первую часть перед дефисом как есть
        declined_last_word_full = '-'.join(parts[:-1] + [declined_last_word])
    else:
        declined_last_word_full = add_kazakh_genitive(last_word)  # Склоняем слово

    # Склонение должно касаться только последнего слова в фразе
    return ' '.join(words[:-1] + [declined_last_word_full])

def add_kazakh_genitive(word):
    """
    Добавление окончания родительного падежа к казахскому слову.
    """
    last_letter = word[-1]
    if is_vowel(last_letter):
        # Выбор окончания для слов, заканчивающихся на гласную
        if is_front_vowel(last_letter):
            return word + 'нің'
        else:
            return word + 'ның'
    else:
        # Определяем гармонию для согласных
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
    Склонение фраз на русском языке в родительный падеж с учетом дефисов.
    """
    words = phrase.split()
    declined_words = []

    for word in words:
        if '-' in word:  # Если есть дефис
            parts = word.split('-')
            declined_parts = []
            for part in parts:
                parsed_word = morph.parse(part)[0]
                declined_word = parsed_word.inflect({'gent'})
                if declined_word:
                    final_word = restore_case(declined_word.word, part)
                else:
                    final_word = part
                declined_parts.append(final_word)
            declined_words.append('-'.join(declined_parts))
        else:
            parsed_word = morph.parse(word)[0]
            declined_word = parsed_word.inflect({'gent'})
            if declined_word:
                final_word = restore_case(declined_word.word, word)
            else:
                final_word = word
            declined_words.append(final_word)
    
    return ' '.join(declined_words)

# Вспомогательная функция для восстановления регистра
def restore_case(word, original_word):
    if original_word.istitle():
        return word.capitalize()
    return word

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
