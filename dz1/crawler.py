import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "https://en.wikipedia.org/wiki/Special:Random"  
NUM_PAGES = 100  
SAVE_DIR = "pages"
MIN_TEXT_LENGTH = 10000  

os.makedirs(SAVE_DIR, exist_ok=True)

def download_pages():
    index_entries = []
    pages_downloaded = 0

    while pages_downloaded < NUM_PAGES:
        url = BASE_URL  
        res = requests.get(url)
        if res.status_code != 200:
            print(f"Ошибка при загрузке страницы {pages_downloaded + 1}")
            continue

        soup = BeautifulSoup(res.text, 'html.parser')

        content = soup.find('div', {'class': 'mw-parser-output'})
        if not content:
            print(f"Не удалось найти основной контент на странице {pages_downloaded + 1}")
            continue

        text_length = len(content.get_text())
        if text_length < MIN_TEXT_LENGTH:
            print(f"Пропуск страницы {pages_downloaded + 1}, так как текста меньше {MIN_TEXT_LENGTH} символов")
            continue

        real_url = res.url
        filename = os.path.join(SAVE_DIR, f"page_{pages_downloaded + 1}.html")
        
        with open(filename, "w", encoding="utf-8") as file:
            file.write(res.text)

        index_entries.append(f"page_{pages_downloaded + 1}.html {real_url}")

        pages_downloaded += 1  
        print(f"Скачано: {real_url} с текстом длиной {text_length} символов")

    with open("index.txt", "w", encoding="utf-8") as index_file:
        index_file.write("\n".join(index_entries))

if __name__ == "__main__":
    download_pages()
    print("Готово! Все страницы сохранены.")
