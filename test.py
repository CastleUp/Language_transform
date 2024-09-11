import pymorphy2
import pandas as pd

# Инициализируем морфологический анализатор
morph = pymorphy2.MorphAnalyzer()

# Исходный список животных
animals = ['лошадь', 'собака', 'кошка', 'жаба', 'комар', 'тигр', 'слон', 'обезьяна', 'мышь', 'рысь']

# Переводим каждое слово в родительный падеж
animals_genitive = [morph.parse(animal)[0].inflect({'gent'}).word for animal in animals]

# Сохраняем результат в DataFrame
df = pd.DataFrame(animals_genitive, columns=['Родительный падеж'])

# Выводим DataFrame
print(df)