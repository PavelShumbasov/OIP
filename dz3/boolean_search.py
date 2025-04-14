import json
from pyparsing import infixNotation, opAssoc, Keyword, Word, alphas, ParseException

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

class BooleanSearchParser:
    def __init__(self, inverted_index, all_documents):
        self.inverted_index = inverted_index
        self.all_documents = all_documents

    def parse_term(self, term):
        """
        Возвращает множество документов для заданного термина.
        """
        if term.startswith("NOT "):
            term = term[4:]  # Убираем "NOT "
            return boolean_not(self.inverted_index.get(term, set()), self.all_documents)
        return self.inverted_index.get(term, set())

    def evaluate_expression(self, expression):
        """
        Вычисляет результат для сложного запроса.
        """
        term = Word(alphas + "_").setParseAction(lambda t: self.parse_term(t[0]))

        AND = Keyword("AND")
        OR = Keyword("OR")
        NOT = Keyword("NOT")

        expr = infixNotation(
            term,
            [
                ("NOT", 1, opAssoc.RIGHT, lambda t: boolean_not(t[0][1], self.all_documents)),
                ("AND", 2, opAssoc.LEFT, lambda t: boolean_and(t[0][0], t[0][2])),
                ("OR", 2, opAssoc.LEFT, lambda t: boolean_or(t[0][0], t[0][2])),
            ],
        )

        try:
            result = expr.parseString(expression, parseAll=True)[0]
            return result
        except ParseException as e:
            print(f"Ошибка парсинга запроса: {e}")
            return set()

def main():
    input_file = "inverted_index.json" 
    print("Загружаем инвертированный индекс...")
    inverted_index = load_inverted_index(input_file)
    all_documents = set(range(1, len(inverted_index) + 1)) 

    parser = BooleanSearchParser(inverted_index, all_documents)

    while True:
        query = input("Введите запрос (или 'exit' для выхода): ")
        if query.lower() == 'exit':
            break

        print("Выполняем запрос...")
        result = parser.evaluate_expression(query)
        print(f"Результат: {result}")

if __name__ == "__main__":
    main()