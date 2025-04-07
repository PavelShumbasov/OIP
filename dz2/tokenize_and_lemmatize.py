import re
import os
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Скачиваем необходимые ресурсы NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('words')

# Инициализация инструментов
lemmatizer = WordNetLemmatizer()
english_stopwords = set(stopwords.words('english'))
english_words = set(words.words())

def split_camel_case(text):
    """
    Разделяет слова, написанные в стиле CamelCase.
    """
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

def split_long_tokens(token, min_length=3):
    """
    Разделяет длинные токены на подслова, используя словарь английских слов.
    """
    result = []
    current_word = ""
    for i in range(len(token)):
        current_word += token[i]
        if len(current_word) >= min_length and current_word.lower() in english_words:
            result.append(current_word)
            current_word = ""
    if current_word:  # Если остался неразделенный остаток
        result.append(current_word)
    return result

def clean_text(input_text):
    """
    Очищает текст от HTML-разметки, специальных символов, чисел и других нежелательных элементов.
    Также удаляет склеенные токены без использования хардкода.
    """

    # Удаляем HTML-теги, JavaScript-код и ссылки
    clean_text = re.sub(r'<[^>]+>', '', input_text)
    clean_text = re.sub(r'(window\.\w+|function\s*\w*\([^)]*\)|document\.\w+)', '', clean_text)
    clean_text = re.sub(r'http\S+', '', clean_text)

    # Удаляем все символы, кроме букв и пробелов
    clean_text = re.sub(r'[^a-zA-Z\s]', '', clean_text)

    # Удаляем технические токены с помощью регулярного выражения
    technical_patterns = r'\b\w*(wg|mwparseroutput|true|false|edit|url|class|output|config|schema|token|namespace)\w*\b'
    clean_text = re.sub(technical_patterns, '', clean_text)

    # Разделяем CamelCase
    clean_text = split_camel_case(clean_text)

    # Приводим текст к нижнему регистру
    clean_text = clean_text.lower()

    # Разделяем длинные токены и удаляем склеенные
    tokens = clean_text.split()
    new_tokens = []
    for token in tokens:
        if len(token) > 20: 
            continue

        real_word_count = sum(
            1 for i in range(len(token)) 
            for min_length in [3, 4, 5] 
            if token[i:i + min_length].lower() in english_words
        )
        word_density = real_word_count / max(1, len(token)) 

        if word_density < 0.3: 
            continue

        new_tokens.append(token)

    return ' '.join(new_tokens)

def tokenize_and_clean(text):
    """
    Выполняет токенизацию текста и удаляет стоп-слова и короткие слова.
    """
    tokens = word_tokenize(text, language='english')
    
    filtered_tokens = [
        token for token in tokens 
        if token not in english_stopwords and len(token) > 2 and token.isalpha()
    ]
    
    return filtered_tokens

def lemmatize_tokens(tokens):
    """
    Лемматизирует токены и группирует их по леммам.
    Разделяет склеенные токены перед лемматизацией.
    """
    lemmatized_groups = {}
    
    technical_patterns = r'\b\w*(wg|mwparseroutput|true|false|edit|url|class|output|config|schema|token|namespace)\w*\b'

    for token in tokens:
        if re.search(technical_patterns, token):
            continue

        if len(token) > 20:
            continue

        split_tokens = split_camel_case(token).split()

        valid_parts = []
        for part in split_tokens:
            real_word_count = sum(
                1 for i in range(len(part)) 
                for min_length in [3, 4, 5] 
                if part[i:i + min_length].lower() in english_words
            )
            word_density = real_word_count / max(1, len(part))

            if word_density >= 0.3:
                valid_parts.append(part)

        if not valid_parts:
            continue

        for part in valid_parts:
            lemma = lemmatizer.lemmatize(part)
            if lemma not in lemmatized_groups:
                lemmatized_groups[lemma] = set()
            lemmatized_groups[lemma].add(part)

    return lemmatized_groups

def process_files(input_dir, tokens_dir, lemmas_dir):
    """
    Обрабатывает все файлы в указанной директории, выполняет токенизацию,
    лемматизацию и сохраняет результаты в соответствующие файлы.
    """
    os.makedirs(tokens_dir, exist_ok=True)
    os.makedirs(lemmas_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".html"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                raw_text = file.read()
                cleaned_text = clean_text(raw_text)
                tokens = tokenize_and_clean(cleaned_text)
                lemmatized_groups = lemmatize_tokens(tokens)

                # Сохраняем токены
                tokens_file = os.path.join(tokens_dir, f"tokens_{filename}.txt")
                with open(tokens_file, 'w', encoding='utf-8') as f_tokens:
                    for lemma in sorted(lemmatized_groups.keys()):
                        f_tokens.write(f"{lemma}\n")

                # Сохраняем леммы
                lemmas_file = os.path.join(lemmas_dir, f"lemmas_{filename}.txt")
                with open(lemmas_file, 'w', encoding='utf-8') as f_lemmas:
                    for lemma, forms in sorted(lemmatized_groups.items()):
                        f_lemmas.write(f"{lemma} {' '.join(sorted(forms))}\n")

def main():
    input_directory = os.path.join("..", "dz1", "pages")
    tokens_directory = "tokens"
    lemmas_directory = "lemmas"

    process_files(input_directory, tokens_directory, lemmas_directory)
    print("Обработка завершена!")

if __name__ == "__main__":
    main()