import csv
import time
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from tqdm import tqdm

API_KEY = 'AIzaSyBGgTovf7zQjSj94Ew9tG6LwH_V6yZlUxg'  
VIDEO_URLS = [
    "https://www.youtube.com/watch?v=zE5EY6EirT8"
]

youtube = build('youtube', 'v3', developerKey=API_KEY)

# Функция для извлечения ID видео из ссылки
def extract_video_id(url):
    """Извлекает ID видео из URL YouTube."""
    pattern = r'(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        print(f"Ошибка: Не удалось извлечь ID из {url}")
        return None

# Функция для получения комментариев к видео
def get_comments(video_id, max_comments=10,max_text_length = 50):
    comments = []
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            textFormat='plainText'
        ).execute()

        with tqdm(total=max_comments, desc=f"Сбор комментариев для {video_id}", leave=False) as pbar:
            while response and len(comments) < max_comments:
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    pbar.update(1)  # Обновляем прогресс-бар
                    text = comment['textDisplay']
                    # Пропускаем комментарий, если он длиннее max_text_length
                    if len(text) <= max_text_length:
                        comments.append({
                            'text': text,
                            'published_at': comment['publishedAt'],
                            'author_id': comment['authorChannelId']['value']
                        })
                        pbar.update(1)
                    if len(comments) >= max_comments:
                        break

                if 'nextPageToken' in response and len(comments) < max_comments:
                    time.sleep(1)  # Задержка для предотвращения перегрузки API
                    response = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        pageToken=response['nextPageToken'],
                        maxResults=100,
                        textFormat='plainText'
                    ).execute()
                else:
                    break
    except HttpError as e:
        print(f"Произошла ошибка: {e}")
    return comments

# Функция для получения даты создания канала
def get_channel_creation_date(channel_id):
    try:
        response = youtube.channels().list(
            part='snippet',
            id=channel_id
        ).execute()
        if response['items']:
            return response['items'][0]['snippet']['publishedAt']
    except HttpError as e:
        print(f"Ошибка при получении данных канала: {e}")
    return None
def DataLoad(VIDEO_URLS,filename = 'youtube_comments.csv',max_comments = 10,max_text_length = 50):
    # Основной процесс с прогресс-баром
    all_comments = []
    print("Извлечение ID видео и сбор комментариев...")
    for url in tqdm(VIDEO_URLS, desc="Обработка видео"):
        video_id = extract_video_id(url)
        if video_id:
            comments = get_comments(video_id,max_comments=max_comments,max_text_length= max_text_length)
            all_comments.extend(comments)

    # Получение уникальных авторов
    author_ids = list(set([comment['author_id'] for comment in all_comments]))

    # Получение даты создания канала для каждого автора с прогресс-баром
    author_creation_dates = {}
    print("\nПолучение дат создания каналов...")
    for author_id in tqdm(author_ids, desc="Загрузка данных каналов"):
        creation_date = get_channel_creation_date(author_id)
        if creation_date:
            author_creation_dates[author_id] = creation_date

    # Оценка количества недавних комментариев
    author_comment_counts = {}
    for comment in all_comments:
        author_id = comment['author_id']
        author_comment_counts[author_id] = author_comment_counts.get(author_id, 0) + 1

    # Подготовка данных для CSV
    data = []
    for comment in all_comments:
        author_id = comment['author_id']
        data.append({
            'text': comment['text'],
            'published_at': comment['published_at'],
            'author_id': author_id,
            'creation_date': author_creation_dates.get(author_id, 'Unknown'),
            'recent_comments': author_comment_counts.get(author_id, 0)
        })

    # Сохранение в CSV
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, quoting=csv.QUOTE_ALL)

    print("\nДанные успешно сохранены в " , filename)
DataLoad(VIDEO_URLS,max_comments=500,max_text_length=100)