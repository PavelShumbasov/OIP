import os
import math
from collections import defaultdict

def load_documents(tokens_dir, lemmas_dir):
    """
    Загружает токены и леммы из файлов.
    """
    documents_tokens = {}
    documents_lemmas = {}

    # Загрузка токенов
    for filename in os.listdir(tokens_dir):
        if filename.startswith("tokens_page_") and filename.endswith(".txt"):
            file_id = filename.split("_")[2].split(".")[0]  # Извлекаем ID документа
            with open(os.path.join(tokens_dir, filename), 'r', encoding='utf-8') as f:
                documents_tokens[file_id] = f.read().split()

    # Загрузка лемм
    for filename in os.listdir(lemmas_dir):
        if filename.startswith("lemmas_page_") and filename.endswith(".txt"):
            file_id = filename.split("_")[2].split(".")[0]  # Извлекаем ID документа
            documents_lemmas[file_id] = []
            with open(os.path.join(lemmas_dir, filename), 'r', encoding='utf-8') as f:
                for line in f:
                    lemma, forms = line.strip().split(" ", 1)
                    documents_lemmas[file_id].append((lemma, forms.split()))

    return documents_tokens, documents_lemmas

def calculate_tf(documents, documents_tokens=None, is_lemmas=False):
    """
    Вычисляет TF (сырое количество вхождений) для каждого термина или леммы в каждом документе.
    Если is_lemmas=True, то учитывает все формы слова для каждой леммы.
    """
    tf = {}
    for doc_id, data in documents.items():
        term_counts = defaultdict(int)
        if is_lemmas:
            # Для лемм суммируем вхождения всех форм
            for lemma, forms in data:
                for form in forms:
                    term_counts[lemma] += documents_tokens[doc_id].count(form)
        else:
            # Для токенов просто считаем вхождения
            for term in data:
                term_counts[term] += 1
        tf[doc_id] = term_counts
    return tf

def calculate_idf(documents, is_lemmas=False):
    """
    Вычисляет IDF для каждого термина.
    Формула: IDF(t) = log(N / df(t))
    """
    idf = defaultdict(lambda: 0)
    num_docs = len(documents)
    term_doc_count = defaultdict(int)

    for data in documents.values():
        if is_lemmas:
            # Уникальные леммы
            unique_terms = set(lemma for lemma, forms in data)
        else:
            # Уникальные термины
            unique_terms = set(data)

        for term in unique_terms:
            term_doc_count[term] += 1

    for term, doc_count in term_doc_count.items():
        if doc_count > 0:  # Защита от деления на ноль
            idf[term] = math.log(num_docs / doc_count)
        else:
            idf[term] = 0  # Если термин не встречается, IDF = 0

    return idf

def calculate_tf_idf(tf, idf):
    """
    Вычисляет TF-IDF для каждого термина в каждом документе.
    """
    tf_idf = {}
    for doc_id, term_tf in tf.items():
        tf_idf[doc_id] = {term: term_tf[term] * idf[term] for term in term_tf}
    return tf_idf

def save_results(tf, idf, tf_idf, output_dir, prefix):
    """
    Сохраняет результаты в файлы в формате <термин><пробел><tf><пробел><idf><пробел><tf-idf><\n>.
    """
    os.makedirs(output_dir, exist_ok=True)
    for doc_id, term_scores in tf_idf.items():
        output_file = os.path.join(output_dir, f"{prefix}_page_{doc_id}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            for term in term_scores.keys():
                raw_tf = tf[doc_id][term]  # Сырая частота термина
                f.write(f"{term} {raw_tf} {idf[term]} {tf_idf[doc_id][term]}\n")

def main():
    tokens_dir = "../dz2/tokens"  # Путь к папке с токенами
    lemmas_dir = "../dz2/lemmas"  # Путь к папке с леммами
    output_terms_dir = "tf_idf_terms"  # Папка для сохранения TF-IDF для токенов
    output_lemmas_dir = "tf_idf_lemmas"  # Папка для сохранения TF-IDF для лемм

    print("Загружаем документы...")
    documents_tokens, documents_lemmas = load_documents(tokens_dir, lemmas_dir)

    print("Вычисляем TF, IDF и TF-IDF для токенов...")
    tf_tokens = calculate_tf(documents_tokens)
    idf_tokens = calculate_idf(documents_tokens)
    tf_idf_tokens = calculate_tf_idf(tf_tokens, idf_tokens)

    print("Вычисляем TF, IDF и TF-IDF для лемм...")
    tf_lemmas = calculate_tf(documents_lemmas, documents_tokens=documents_tokens, is_lemmas=True)
    idf_lemmas = calculate_idf(documents_lemmas, is_lemmas=True)
    tf_idf_lemmas = calculate_tf_idf(tf_lemmas, idf_lemmas)

    print("Сохраняем результаты...")
    save_results(tf_tokens, idf_tokens, tf_idf_tokens, output_terms_dir, "terms")
    save_results(tf_lemmas, idf_lemmas, tf_idf_lemmas, output_lemmas_dir, "lemmas")

    print("Готово!")

if __name__ == "__main__":
    main()