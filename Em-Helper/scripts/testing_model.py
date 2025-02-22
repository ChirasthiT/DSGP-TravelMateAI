import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

vectorizer = joblib.load("../models/tfidf_vectorizer.pkl")
classifier = joblib.load("../models/risk_classifier.pkl")

test_phrases = [
   "I'm lost in a dark alley, I can't find my way!",
   "I just got into an accident, someone please call the ambulance!",
   "There’s a suspicious person following me!",
   "I lost my passport at the airport, what should I do?",
   "Help! My house is on fire, I need assistance immediately!"
]

test_vectors = vectorizer.transform(test_phrases)

predictions = classifier.predict(test_vectors)

for phrase, risk in zip(test_phrases, predictions):
   print(f"Phrase: {phrase}\nPredicted Risk Level: {risk}\n")

input_csv = "../data/keywords_extracted.csv"
df = pd.read_csv(input_csv)
X = df['Phrases']
y = df['Risk_Level']

X_train, X_test, y_train, y_test = train_test_split(X, y,
test_size=0.2, random_state=42)
X_train_vectors = vectorizer.transform(X_train)
X_test_vectors = vectorizer.transform(X_test)

y_pred = classifier.predict(X_test_vectors)

print("\nModel Performance on Test Data:")
print(classification_report(y_test, y_pred))
