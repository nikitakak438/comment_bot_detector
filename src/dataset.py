import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


nltk.download('wordnet')
nltk.download('stopwords')

class CommentDataset(Dataset):
    def __init__(self, csv_file, model_name="bert-base-uncased", max_length=128):
        """
        Инициализация датасета для английского текста.
        
        Args:
            csv_file (str): Путь к CSV-файлу с колонками 'comment' и 'label'.
            model_name (str): Название модели для токенизатора (по умолчанию BERT).
            max_length (int): Максимальная длина последовательности после токенизации.
        """
        self.data = pd.read_csv(csv_file)
        if not {'comment', 'label'}.issubset(self.data.columns):
            raise ValueError("CSV must contain 'comment' and 'label' columns")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_length = max_length
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.texts = [self._preprocess_text(text) for text in self.data['comment']]
        self.labels = self.data['label'].astype(int).tolist()

    def _preprocess_text(self, text):
        """
        Предобработка текста: очистка, лемматизация, удаление стоп-слов.
        
        Args:
            text (str): Входной текст.
        
        Returns:
            str: Обработанный текст.
        """

        text = re.sub(r'[^\w\s]', '', text.lower()) 
        text = re.sub(r'\s+', ' ', text).strip()
        tokens = text.split()
        lemmatized_tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]
        
        return ' '.join(lemmatized_tokens)

    def __getitem__(self, index):
        """
        Получение элемента датасета.
        
        Args:
            index (int): Индекс элемента.
        
        Returns:
            dict: Словарь с токенизированным текстом и меткой.
        """
        text = self.texts[index]
        label = self.labels[index]
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

    def __len__(self):
        """
        Возвращает размер датасета.
        
        Returns:
            int: Количество элементов в датасете.
        """
        return len(self.data)
