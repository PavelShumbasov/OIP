import re
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Скачиваем необходимые ресурсы NLTK
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

# Инициализация инструментов
lemmatizer = WordNetLemmatizer()
english_stopwords = set(stopwords.words('english'))

def clean_text(input_text):
    """
    Очищает текст от HTML-разметки, специальных символов, чисел и других нежелательных элементов.
    """
    clean_text = re.sub(r'<[^>]+>', '', input_text)
    clean_text = re.sub(r'(window\.\w+|function\s*\w*\([^)]*\)|document\.\w+)', '', clean_text)
    clean_text = re.sub(r'http\S+', '', clean_text)
    clean_text = re.sub(r'[^a-zA-Z\s]', '', clean_text)
    clean_text = clean_text.lower()
    return clean_text

def tokenize_and_clean(text):
    """
    Выполняет токенизацию текста и удаляет стоп-слова и короткие слова.
    """
    # Токенизация текста с явным указанием языка
    tokens = word_tokenize(text, language='english')
    
    # Фильтрация токенов: удаляем стоп-слова, короткие слова и числа
    filtered_tokens = [
        token for token in tokens 
        if token not in english_stopwords and len(token) > 2 and token.isalpha()
    ]
    return filtered_tokens

def lemmatize_tokens(tokens):
    """
    Лемматизирует токены и группирует их по леммам.
    """
    lemmatized_groups = {}
    for token in tokens:
        lemma = lemmatizer.lemmatize(token)
        if lemma not in lemmatized_groups:
            lemmatized_groups[lemma] = set()
        lemmatized_groups[lemma].add(token)
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