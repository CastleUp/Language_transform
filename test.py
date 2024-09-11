import pymorphy2
import pandas as pd

# Инициализируем морфологический анализатор
morph = pymorphy2.MorphAnalyzer()

# Исходный список
rayons = ['Абай', 'Абайский', 'Поселок']

# Переводим каждое слово в родительный падеж
rayons_genitive = [morph.parse(rayon)[0].inflect({'gent'}).word for rayon in rayons]

# Сохраняем результат в DataFrame
df = pd.DataFrame(rayons_genitive, columns=['Родительный падеж'])

# Выводим DataFrame
print(df)