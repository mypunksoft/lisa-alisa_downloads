import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

def rot13(s):
    return s.translate(str.maketrans(
        'ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz',
        'NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm'))

base_url = input("Введите URL страницы с файлами: ").strip()

download_folder = 'downloaded_files'
os.makedirs(download_folder, exist_ok=True)

def download_file(url, file_name):
    if os.path.exists(file_name):
        print(f"Файл {file_name} уже существует, пропускаем.")
        return

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        with open(file_name, 'wb') as f, tqdm(
            desc=file_name,
            total=total_size,
            unit='B',
            unit_scale=True
        ) as bar:
            for chunk in response.iter_content(1024):
                f.write(chunk)
                bar.update(len(chunk))
        print(f'Файл {file_name} успешно скачан.')
    else:
        print(f'Ошибка при скачивании файла {file_name}.')

def extract_tracks_from_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    playlist_items = soup.select(".playlist .item")
    tracks = []

    for item in playlist_items:
        data_f = item.get("data-f")

        file_path = rot13(data_f)
        file_url = f"https://stat2.lisa-alisa.club/s/{file_path}.mp3"

        name_elem = item.select_one(".name")
        title = name_elem.text.strip() if name_elem else "Без названия"
        extra = name_elem.get("data-extra") if name_elem else None

        tracks.append({
            "title": title,
            "extra": extra,
            "url": file_url
        })

    return tracks

def main():
    tracks = extract_tracks_from_page(base_url)
    for track in tracks:
        print(f'Найден файл: {track["title"]}, ссылка: {track["url"]}')
        
        file_name = f"{track['title']}.mp3"
        file_path = os.path.join(download_folder, file_name)
        
        download_file(track['url'], file_path)

if __name__ == '__main__':
    main()
