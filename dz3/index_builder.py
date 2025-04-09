import os
import json

def build_inverted_index(lemmas_dir):
    """
    Строит инвертированный индекс на основе файлов с леммами.
    """
    inverted_index = {}
    for filename in os.listdir(lemmas_dir):
        if filename.startswith("lemmas_page_") and filename.endswith(".txt"):
            file_id = int(filename.split("_")[2].split(".")[0])  # Извлекаем ID документа
            with open(os.path.join(lemmas_dir, filename), 'r', encoding='utf-8') as file:
                for line in file:
                    lemma, forms = line.strip().split(" ", 1)
                    if lemma not in inverted_index:
                        inverted_index[lemma] = set()
                    inverted_index[lemma].add(file_id)
    
    # Преобразуем множества в списки для сериализации в JSON
    inverted_index = {lemma: list(doc_ids) for lemma, doc_ids in inverted_index.items()}
    return inverted_index

def save_inverted_index(inverted_index, output_file):
    """
    Сохраняет инвертированный индекс в файл JSON.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, ensure_ascii=False, indent=4)

def main():
    lemmas_directory = "../dz2/lemmas"  
    output_file = "inverted_index.json"  

    print("Строим инвертированный индекс...")
    inverted_index = build_inverted_index(lemmas_directory)
    print("Индекс построен. Сохраняем в файл...")
    save_inverted_index(inverted_index, output_file)
    print(f"Инвертированный индекс сохранен в файл: {output_file}")

if __name__ == "__main__":
    main()