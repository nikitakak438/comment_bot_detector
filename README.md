
# Comment Bot Detector

Система для оценки вероятности того, что комментарий на YouTube написан ботом.  
Проект включает: сбор данных через YouTube API, предобработку текста, обучение модели классификации и пример интеграции (расширение/сервис — опционально).

## Что умеет
- Собирать комментарии YouTube по списку ссылок на видео и сохранять в CSV.
- Делать предобработку текста (очистка, лемматизация, замена emoji).
- Готовить датасет для трансформера (BERT) и обучать классификатор.
- Строить признаки времени публикации и тональности (sentiment) для анализа.

## Технологии
- Python, pandas, nympy, SQL
- transformers / PyTorch (датасет и токенизация)
- NLTK (лемматизация/стоп-слова)
- YouTube Data API (сбор комментариев)

## Структура репозитория
```text
comment_bot_detector/
├─ README.md
├─ backend/                
├─ bert_classifier/
├─ chrome-extension/
├─ notebooks/                 # ноутбуки
│  ├─ Analize.ipynb           
│  └─ Model.ipynb
├─ images/
│  ├─ example.py
│  ├─ metrics.py
├─ src/
│  ├─ data_import.py          # сбор комментариев (YouTube API)
│  ├─ youtube_collect.py      # сбор с возможностью продолжения
│  ├─ dataset.py              # CommentDataset для BERT
│  ├─ preprocessing.py        # TextPreprocessing: очистка/лемматизация/emoji
│  └─ features.py             # фичи времени и тональности
└─ results/
   ├─ metrics.json
```


## Данные и формат
Для обучения удобно использовать CSV с колонками:
- `comment` — текст комментария
- `label` — метка класса (0/1)

Датасет для трансформера реализуется в `src/dataset.py`.

## Результаты 

**Рассчеты F1 и Accuracy: (F1: 0.62 → 0.96)**

![Alt Text](/images/metrics.png)

**Пример собранных данных:**

![Alt Text](/images/example.png)

В ноутбуках описано множество результатов и тестов, там можно их посмотреть `comment_bot_detector/notebooks`


