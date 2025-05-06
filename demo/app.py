from flask import Flask, render_template, request, jsonify
import os
import sys
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта
sys.path.append(str(Path(__file__).parent.parent))
from dz5.vector_search import VectorSearch

app = Flask(__name__)

# Инициализация поисковой системы
print("Инициализация поисковой системы...")
searcher = VectorSearch(
    tf_idf_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), "dz4", "tf_idf_terms"),
    inverted_index_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "dz3", "inverted_index.json")
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '')
    if not query:
        return jsonify({'error': 'Пустой запрос'})
    
    results = searcher.search(query, top_k=10)
    
    formatted_results = []
    for doc_id, score in results:
        snippet = searcher.get_document_snippet(doc_id, query)
        formatted_results.append({
            'doc_id': doc_id,
            'score': f"{score:.4f}",
            'snippet': snippet
        })
    
    return jsonify({
        'query': query,
        'results': formatted_results
    })

if __name__ == '__main__':
    app.run(debug=True) 