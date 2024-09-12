from TurkLang import KazakhAnalyzer

# Инициализация морфологического анализатора для казахского языка
analyzer = KazakhAnalyzer()

# Слово для анализа
word = 'Алматы'

# Анализируем слово
analysis = analyzer.analyze(word)

# Выводим результат
for a in analysis:
    print(a)