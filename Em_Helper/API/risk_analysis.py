from keybert import KeyBERT
import joblib
import os

kw_model = None
classifier = None
vectorizer = None


def load_models():
    global kw_model, classifier, vectorizer

    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, 'models', 'risk_classifier.pkl')
        vectorizer_path = os.path.join(base_dir, 'models', 'tfidf_vectorizer.pkl')

        classifier = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        kw_model = KeyBERT()
        print("Risk analysis models loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading risk analysis models: {e}")
        return False


load_success = load_models()


def extract_keywords(text):
    if kw_model:
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=2)
        return " ".join([kw[0] for kw in keywords])
    else:
        words = text.lower().split()
        return " ".join(words[:2])


def evaluate_risk(text):
    if not text:
        return 30, "low"

    if classifier and vectorizer:
        try:
            keywords = extract_keywords(text)
            vectorized_text = vectorizer.transform([keywords])
            risk_level = classifier.predict(vectorized_text)[0]

            probabilities = classifier.predict_proba(vectorized_text)[0]
            max_prob_index = probabilities.argmax()
            confidence_score = probabilities[max_prob_index] * 100

            if risk_level.lower() == "high":
                risk_score = 90
            elif risk_level.lower() == "medium":
                risk_score = 60
            else:
                risk_score = 30

            return risk_score, risk_level
        except Exception as e:
            print(f"Error in risk evaluation: {e}")
            return fallback_risk_evaluation(text)
    else:
        return fallback_risk_evaluation(text)


def fallback_risk_evaluation(text):
    high_risk_keywords = ['heart', 'breathing', 'attack', 'gun', 'blood', 'unconscious', 'dying',
                          'emergency', 'severe', 'critical', 'life', 'threat']
    medium_risk_keywords = ['pain', 'accident', 'hurt', 'fire', 'smoke', 'following', 'scared',
                            'injury', 'concern', 'worried', 'danger', 'unsafe']

    text_lower = text.lower()

    if any(keyword in text_lower for keyword in high_risk_keywords):
        return 90, "high"
    elif any(keyword in text_lower for keyword in medium_risk_keywords):
        return 60, "medium"
    else:
        return 30, "low"


def determine_action(risk_level):
    risk_level = risk_level.lower()

    if risk_level == "high":
        return [
            "Call emergency services (911) immediately",
            "Stay on the line with emergency services until help arrives",
            "If possible, send your exact location through the app",
            "Follow any instructions given by emergency personnel"
        ]
    elif risk_level == "medium":
        return [
            "Consider calling emergency services (911)",
            "If safe to do so, move to a more secure location",
            "Contact a trusted friend or family member",
            "Keep your phone with you and stay alert"
        ]
    else:
        return [
            "Stay calm and assess the situation",
            "Consider contacting a friend or family member",
            "Use available resources to address your concern",
            "Continue monitoring the situation and escalate if needed"
        ]