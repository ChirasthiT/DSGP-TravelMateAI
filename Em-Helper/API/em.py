import pandas as pd
import re
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util


class EmergencyHelper:
    def __init__(self, tfidf_max_features=1000, ngram_range=(1, 2)):
        self.tfidf = TfidfVectorizer(ngram_range=ngram_range, stop_words='english', max_features=tfidf_max_features)
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.feature_names = None
        self.phrases_embeddings = None

    @staticmethod
    def clean_text(text):
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def preprocess_data(self, filepath):
        df = pd.read_csv(filepath)
        df['Phrases'] = df['Phrases'].apply(self.clean_text)
        return df

    def train_tfidf(self, phrases):
        tfidf_matrix = self.tfidf.fit_transform(phrases)
        self.feature_names = self.tfidf.get_feature_names_out()
        return pd.DataFrame(tfidf_matrix.toarray(), columns=self.feature_names)

    def compute_embeddings(self, phrases):
        self.phrases_embeddings = self.model.encode(phrases.tolist(), convert_to_tensor=True)

    def get_top_keywords_tfidf(self, phrase, n=5):
        if self.feature_names is None:
            raise ValueError("TF-IDF model is not trained yet.")
        phrase_tfidf = self.tfidf.transform([phrase])
        tfidf_scores = pd.Series(phrase_tfidf.toarray().flatten(), index=self.feature_names)
        return tfidf_scores.sort_values(ascending=False).head(n).index.tolist()

    def get_top_keywords_bert(self, query_phrase, n=5):
        if self.phrases_embeddings is None:
            raise ValueError("BERT embeddings are not computed yet.")
        query_embedding = self.model.encode(query_phrase, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(query_embedding, self.phrases_embeddings)
        top_matches = torch.topk(cosine_scores[0], k=n)
        return [query_phrase[i.item()] for i in top_matches.indices]