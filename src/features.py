from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
class DataExec:
    def __init__(self,data):
            self.data = data
            self.analyzer = SentimentIntensityAnalyzer()
    def TimeExecutor(self,text):
        dt = datetime.fromisoformat(text.replace('Z','+00:00'))
        date = dt.date()
        time = dt.time()
        return date, time
    def TimeDistrub(self,video_url):
        data = self.data[self.data['video_id'] == video_url]
        Temp= data['published_at'].apply(self.TimeExecutor).apply(pd.Series)
        Temp = Temp.rename(columns={0:'data',1:'time'})
        Temp['data'] = pd.to_datetime(Temp['data'])
        Temp['time'] = Temp['time'] = pd.to_datetime(Temp['time'], format='%H:%M:%S').dt.time
        Temp['total_seconds'] = Temp['time'].apply(lambda t: t.hour * 3600 + t.minute * 60 + t.second) + (Temp['data'] - Temp['data'].min()).dt.total_seconds()
        return pd.DataFrame({'total_seconds' :Temp['total_seconds']})
    def categorize_sentiment(self,score):
        if score <= -0.5:
            return 'Very Negative'
        elif -0.5 < score <= -0.05:
            return 'Negative'
        elif -0.05 < score < 0.05:
            return 'Neutral'
        elif 0.05 <= score < 0.5:
            return 'Positive'
        else:
            return 'Very Positive'
    def SentimentExecutor(self,video_url):
        data = self.data[self.data['video_id'] == video_url]
        analyzer = SentimentIntensityAnalyzer()
        data['comment_text'] = data['comment_text'].fillna('').astype(str)
        Tmp = pd.DataFrame({'sentiment' : data['comment_text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])})
        Tmp['sentiment_category'] = Tmp['sentiment'].apply(self.categorize_sentiment)
        return Tmp[['sentiment','sentiment_category']]
    def SentAndTimeExec(self,video_url):
        data = self.data[self.data['video_id'] == video_url]
        TempData = self.TimeDistrub(video_url)
        TempData['comment_text'] = data['comment_text']
        TempData['sentiment_category'] = self.SentimentExecutor(video_url)['sentiment_category']
        return TempData
