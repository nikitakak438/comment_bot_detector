import emoji
import re
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import nltk


class TextPreprocessing():
    def __init__(self):
 
        self.lemmatizer = WordNetLemmatizer()
    def text_cleaner(self,text):
        tmp =  re.sub(r'http\S+|@\w+|#\w+', '', text)
        tmp = re.sub(r'[^a-zA-Z0-9\s]','',tmp)
        tmp = re.sub(r'\b(a|the)\b','',tmp,flags=re.IGNORECASE)
        tmp = re.sub(r'\s+',' ',tmp).strip()
        return tmp
    def text_beuty(self,text):
        
        
        text = text.lower()
        words = word_tokenize(text)
        tagged_words = pos_tag(words)
        lemmatized_words = [
            self.lemmatizer.lemmatize(word, pos='v' if tag.startswith('V') else 'n') 
            for word, tag in tagged_words
        ]
        return ' '.join(lemmatized_words)
    def replace_emoji(self,text):
        return emoji.demojize(text)