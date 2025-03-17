import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv("../data/keywords_extracted.csv")

def assign_risk_level(keywords):
   high_risk_keywords = {"attack", "fire", "police", "help", "hospital", "danger"}
   medium_risk_keywords = {"lost", "stuck", "alone", "scared", "thief"}

   keyword_list = str(keywords).lower().split(" ")

   if any(word in high_risk_keywords for word in keyword_list):
       return "High"
   elif any(word in medium_risk_keywords for word in keyword_list):
       return "Medium"
   else:
       return "Low"

df['Risk_Level'] = df['KeyBERT'].apply(assign_risk_level)

X = df['KeyBERT'].astype(str)
y = df['Risk_Level']

vectorizer = TfidfVectorizer()
X_tfidf = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y,
test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

joblib.dump(vectorizer, "../models/tfidf_vectorizer.pkl")
joblib.dump(clf, "../models/risk_classifier.pkl")

print(" Model training complete! Saved vectorizer and classifier.")