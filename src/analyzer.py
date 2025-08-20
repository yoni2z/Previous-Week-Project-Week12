import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from transformers import pipeline  
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import logging

nltk.download(['punkt', 'stopwords', 'wordnet', 'punkt_tab'], quiet=True)
nlp = spacy.load('en_core_web_sm')
logging.basicConfig(filename='logs/analyzer.log', level=logging.INFO)

class ReviewAnalyzer:
    def __init__(self, input_path='data/processed/all_banks_reviews_clean.csv'):
        self.df = pd.read_csv(input_path)
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.sentiment_pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

    def preprocess_text(self, text):
        tokens = word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(t) for t in tokens if t.isalpha() and t not in self.stop_words]
        return ' '.join(tokens)

    def analyze_sentiment(self):
        self.df['preprocessed_text'] = self.df['review_text'].apply(self.preprocess_text)
        sentiments = self.sentiment_pipeline(self.df['preprocessed_text'].tolist())
        self.df['sentiment_label'] = [s['label'] for s in sentiments]
        self.df['sentiment_score'] = [s['score'] for s in sentiments]
        logging.info("Sentiment analysis complete.")

    def extract_themes(self):
        vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1,2))
        tfidf_matrix = vectorizer.fit_transform(self.df['preprocessed_text'])
        keywords = vectorizer.get_feature_names_out()
        
        # Rule-based clustering (manual themes)
        theme_map = {
            'Account Access Issues': ['login', 'error', 'password', 'access'],
            'Transaction Performance': ['slow', 'transfer', 'loading', 'crash'],
            'User Interface & Experience': ['ui', 'design', 'easy', 'navigation'],
            'Customer Support': ['support', 'help', 'response'],
            'Feature Requests': ['feature', 'add', 'fingerprint', 'budget']
        }
        self.df['themes'] = self.df['preprocessed_text'].apply(lambda text: [theme for theme, kws in theme_map.items() if any(kw in text for kw in kws)])
        logging.info("Thematic analysis complete.")

    def save_results(self):
        output = 'data/insights/review_analysis.csv'
        self.df.to_csv(output, index=False)
        return output

if __name__ == "__main__":
    analyzer = ReviewAnalyzer()
    analyzer.analyze_sentiment()
    analyzer.extract_themes()
    analyzer.save_results()