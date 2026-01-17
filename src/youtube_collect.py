import googleapiclient.discovery
from googleapiclient.errors import HttpError
import pandas as pd
import os

def get_youtube_comments(video_urls, api_key, output_file="comments.csv", 
                        max_results_per_video=1000, start_from_comment=1001):
    """
    Собирает комментарии с YouTube видео с возможностью продолжения
    
    Parameters:
    video_urls (list): Список URL видео
    api_key (str): API ключ от Google
    output_file (str): Файл для сохранения результатов
    max_results_per_video (int): Максимум комментариев на видео
    start_from_comment (int): С какого комментария начинать сбор
    """
    
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)

    if os.path.exists(output_file):
        try:
            existing_df = pd.read_csv(output_file)
            # Проверяем наличие необходимых столбцов
            required_columns = ["video_id", "comment_text", "published_at", "author"]
            if not all(col in existing_df.columns for col in required_columns):
                print(f"Файл {output_file} не содержит всех необходимых столбцов. Создаем новый.")
                existing_df = pd.DataFrame(columns=required_columns)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            print(f"Файл {output_file} пустой или поврежден. Создаем новый.")
            existing_df = pd.DataFrame(columns=required_columns)
    else:
        existing_df = pd.DataFrame(columns=["video_id", "comment_text", "published_at", "author"])
    
    # Список для хранения новых комментариев из всех видео
    all_new_comments = []
    
    for url in video_urls:
        try:
            video_id = url.split('v=')[-1].split('&')[0]
            print(f"Обработка видео: {video_id}")
            
            # Проверяем, сколько комментариев уже собрано для этого видео
            existing_comments = len(existing_df[existing_df['video_id'] == video_id]) if 'video_id' in existing_df.columns else 0
            if existing_comments >= max_results_per_video:
                print(f"Для {video_id} уже собрано максимум комментариев")
                continue
                
            comments_to_skip = max(0, start_from_comment - 1)
            comments_collected = 0
            video_comments = []
            
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                textFormat="plainText"
            )
            
            # Собираем комментарии для текущего видео
            while request and comments_collected < max_results_per_video:
                response = request.execute()
                
                for item in response["items"]:
                    if comments_collected + existing_comments >= comments_to_skip:
                        comment = item["snippet"]["topLevelComment"]["snippet"]
                        comment_data = {
                            "video_id": video_id,
                            "comment_text": comment["textDisplay"],
                            "published_at": comment["publishedAt"],
                            "author": comment["authorDisplayName"]
                        }
                        video_comments.append(comment_data)
                    
                    comments_collected += 1
                    
                    if comments_collected + existing_comments >= max_results_per_video:
                        break
                
                if "nextPageToken" in response and comments_collected < max_results_per_video:
                    request = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=100,
                        textFormat="plainText",
                        pageToken=response["nextPageToken"]
                    )
                else:
                    request = None
            
            if video_comments:
                all_new_comments.extend(video_comments)
                print(f"Собрано {len(video_comments)} новых комментариев для {video_id}")
            else:
                print(f"Нет новых комментариев для добавления для {video_id}")
                
        except HttpError as e:
            print(f"Ошибка при обработке {url}: {str(e)}")
            continue
    
    # Добавляем все новые комментарии в существующий датасет и сохраняем один раз
    if all_new_comments:
        new_df = pd.DataFrame(all_new_comments)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        updated_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Всего добавлено {len(all_new_comments)} новых комментариев в {output_file}")
    else:
        print("Нет новых комментариев для сохранения")



 
    