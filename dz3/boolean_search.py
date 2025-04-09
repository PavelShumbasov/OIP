import json

def load_inverted_index(input_file):
    """
    Загружает инвертированный индекс из файла JSON.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
    # Преобразуем списки обратно в множества
    inverted_index = {lemma: set(doc_ids) for lemma, doc_ids in inverted_index.items()}
    return inverted_index

def boolean_and(set1, set2):
    return set1.intersection(set2)

def boolean_or(set1, set2):
    return set1.union(set2)

def boolean_not(set1, all_documents):
    return all_documents.difference(set1)

def evaluate_query(query, inverted_index, all_documents):
    """
    Выполняет булев поиск на основе запроса.
    Поддерживаемые операторы: AND, OR, NOT.
    """
    terms = query.split()
    result = set()
    current_operator = None

    for term in terms:
        if term == "AND":
            current_operator = "AND"
        elif term == "OR":
            current_operator = "OR"
        elif term == "NOT":
            current_operator = "NOT"
        else:
            # Ищем лемму в индексе
            term_documents = inverted_index.get(term, set())
            if current_operator == "AND":
                result = boolean_and(result, term_documents)
            elif current_operator == "OR":
                result = boolean_or(result, term_documents)
            elif current_operator == "NOT":
                result = boolean_not(term_documents, all_documents)
            else:
                result = term_documents

    return result

def main():
    input_file = "inverted_index.json"  # Файл с инвертированным индексом
    print("Загружаем инвертированный индекс...")
    inverted_index = load_inverted_index(input_file)
    all_documents = set(range(1, len(inverted_index) + 1))  # Предположим, у нас есть N документов

    while True:
        query = input("Введите запрос (или 'exit' для выхода): ")
        if query.lower() == 'exit':
            break

        print("Выполняем запрос...")
        result = evaluate_query(query, inverted_index, all_documents)
        print(f"Результат: {result}")

if __name__ == "__main__":
    main()