import pandas as pd
from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import seaborn as sns
import matplotlib.pyplot as plt

file_path = "../data/cleanedEmPhrasesf.csv"
df = pd.read_csv(file_path)

#Extracting
kw_model = KeyBERT()
df["Keywords"] = df["Phrases"].apply(lambda x: kw_model.extract_keywords(x, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=2))
df["Keywords"] = df["Keywords"].apply(lambda x: " ".join([kw[0] for kw in x]))
keywords_csv_path = "../data/keywords.csv"
df.to_csv(keywords_csv_path, index=False)
print(f"Extracted keywords saved as {keywords_csv_path}")

#Vectorization
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["Keywords"])
y = df["Risk Level"]

#Model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X_train, y_train)

y_pred = rf_classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")
print(classification_report(y_test, y_pred))

joblib.dump(rf_classifier, "../models/risk_classifier.pkl")
joblib.dump(vectorizer, "../models/tfidf_vectorizer.pkl")
print("Model and vectorizer saved successfully!")
