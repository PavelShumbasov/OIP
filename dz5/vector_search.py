import os
import math
import json
from collections import defaultdict
import numpy as np
from typing import List, Tuple, Dict
import time
import re
from bs4 import BeautifulSoup


class VectorSearch:
    def __init__(self, tf_idf_dir: str, inverted_index_path: str):
        """
        Инициализация поисковой системы
        :param tf_idf_dir: директория с TF-IDF значениями
        :param inverted_index_path: путь к файлу с инвертированным индексом
        """
        self.tf_idf_dir = tf_idf_dir
        self.inverted_index_path = inverted_index_path
        self.doc_vectors: Dict[str, np.ndarray] = {}
        self.term_to_id: Dict[str, int] = {}
        self.id_to_term: Dict[int, str] = {}
        self.doc_lengths: Dict[str, float] = {}
        self.pages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dz1", "pages")
        self.load_data()

    def load_data(self) -> None:
        """Загрузка данных из файлов"""
        print("Загрузка инвертированного индекса...")
        with open(self.inverted_index_path, 'r', encoding='utf-8') as f:
            self.inverted_index = json.load(f)

        print("Создание словаря терминов...")
        all_terms = set(self.inverted_index.keys())
        self.term_to_id = {term: i for i, term in enumerate(all_terms)}
        self.id_to_term = {i: term for term, i in self.term_to_id.items()}

        print("Загрузка векторов документов...")
        for filename in os.listdir(self.tf_idf_dir):
            if filename.startswith("terms_page_") and filename.endswith(".txt"):
                doc_id = filename.split("_")[2].split(".")[0]
                self.doc_vectors[doc_id] = self._load_doc_vector(os.path.join(self.tf_idf_dir, filename))
                self.doc_lengths[doc_id] = np.linalg.norm(self.doc_vectors[doc_id])

        print(f"Загружено {len(self.doc_vectors)} документов и {len(self.term_to_id)} уникальных терминов")

    def _load_doc_vector(self, filepath: str) -> np.ndarray:
        """Загрузка вектора документа из файла"""
        vector = np.zeros(len(self.term_to_id))
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                term, idf, tf_idf = line.strip().split()
                if term in self.term_to_id:
                    vector[self.term_to_id[term]] = float(tf_idf)
        return vector

    def _create_query_vector(self, query: str) -> np.ndarray:
        """Создание вектора запроса"""
        query_terms = query.lower().split()
        query_vector = np.zeros(len(self.term_to_id))

        # Подсчет TF для запроса
        term_counts = defaultdict(int)
        for term in query_terms:
            term_counts[term] += 1

        # Создание вектора запроса
        for term, count in term_counts.items():
            if term in self.term_to_id:
                term_id = self.term_to_id[term]
                if term in self.inverted_index:
                    idf = math.log(len(self.doc_vectors) / len(self.inverted_index[term]))
                    query_vector[term_id] = count * idf

        return query_vector

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Вычисление косинусного сходства между векторами"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot_product / (norm1 * norm2)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Поиск документов по запросу
        :param query: поисковый запрос
        :param top_k: количество возвращаемых результатов
        :return: список кортежей (doc_id, score)
        """
        start_time = time.time()

        query_vector = self._create_query_vector(query)
        query_norm = np.linalg.norm(query_vector)

        if query_norm == 0:
            return []

        results = []
        for doc_id, doc_vector in self.doc_vectors.items():
            score = np.dot(query_vector, doc_vector) / (query_norm * self.doc_lengths[doc_id])
            if score > 0:
                results.append((doc_id, score))

        results.sort(key=lambda x: x[1], reverse=True)

        end_time = time.time()
        print(f"Поиск выполнен за {end_time - start_time:.4f} секунд")

        return results[:top_k]

    def _extract_text_from_html(self, html_content: str) -> str:
        """Извлечение текста из HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Удаляем скрипты и стили
        for script in soup(["script", "style"]):
            script.decompose()

        # Получаем текст
        text = soup.get_text()

        # Разбиваем на строки и удаляем пустые
        lines = (line.strip() for line in text.splitlines())
        # Разбиваем многострочные блоки и удаляем пустые
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Удаляем пустые строки
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def get_document_snippet(self, doc_id: str, query: str, snippet_length: int = 200) -> str:
        """
        Получение сниппета документа с выделением релевантных терминов
        :param doc_id: ID документа
        :param query: поисковый запрос
        :param snippet_length: максимальная длина сниппета
        :return: сниппет документа
        """
        # Загрузка текста документа
        doc_path = os.path.join(self.pages_dir, f"page_{doc_id}.html")
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                text = self._extract_text_from_html(html_content)
        except FileNotFoundError:
            return f"Текст документа {doc_id} недоступен (файл не найден)"
        except Exception as e:
            return f"Ошибка при чтении документа {doc_id}: {str(e)}"

        # Поиск позиций терминов запроса
        query_terms = set(query.lower().split())
        positions = []
        for term in query_terms:
            pos = text.lower().find(term)
            if pos != -1:
                positions.append(pos)

        if not positions:
            return text[:snippet_length] + "..."

        # Находим центральную позицию
        center_pos = sorted(positions)[len(positions) // 2]

        # Вырезаем сниппет вокруг центральной позиции
        start = max(0, center_pos - snippet_length // 2)
        end = min(len(text), center_pos + snippet_length // 2)

        snippet = text[start:end]

        # Выделяем термины запроса
        for term in query_terms:
            snippet = snippet.replace(term, f"\033[1;31m{term}\033[0m")
            snippet = snippet.replace(term.capitalize(), f"\033[1;31m{term.capitalize()}\033[0m")

        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet


def main():
    # Инициализация поисковой системы
    print("Инициализация поисковой системы...")
    searcher = VectorSearch(
        tf_idf_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), "dz4", "tf_idf_terms"),
        inverted_index_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "dz3", "inverted_index.json")
    )

    # Пример использования
    while True:
        query = input("\nВведите поисковый запрос (или 'exit' для выхода): ")
        if query.lower() == 'exit':
            break

        results = searcher.search(query)
        print(f"\nНайдено {len(results)} результатов:")

        for i, (doc_id, score) in enumerate(results, 1):
            print(f"\n{i}. Документ {doc_id} (релевантность = {score:.4f}):")
            snippet = searcher.get_document_snippet(doc_id, query)
            print(snippet)


if __name__ == "__main__":
    main() 