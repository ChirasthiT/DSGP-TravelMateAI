from flask import Flask, request, jsonify, render_template, abort
from werkzeug.utils import secure_filename
import os
from API.product_recommender import ProductRecommender
from API.Product import Product
from flask_pymongo import PyMongo
from pydantic import BaseModel
import pandas as pd

app = Flask(__name__)

# MongoDB configuration (if you want to use it)
app.config['MONGO_URI'] = 'mongodb+srv://admin:admindsgp66@dsgp.e5yrm.mongodb.net/Products_info?retryWrites=true&w=majority&appName=DSGP'
app.config['MONGO_DBNAME'] = 'locationsDB'

db = PyMongo(app)

# Initialize the ProductRecommender
recommender = ProductRecommender(n_clusters=3, max_features=100)

# Preprocessed dataset
data = None  # Initialize globally to be set during startup

# Request models
class UserInteractionData(BaseModel):
    prices: list[float]  # List of past purchase prices

class RecommendationRequest(BaseModel):
    user_interaction_data: UserInteractionData = None
    keywords: str = None  # Keywords input by the user

def load_dataset():
    """Load and preprocess the dataset on application startup."""
    global data
    try:
        data = recommender.load_data("product_dataset.csv")
        data = recommender.preprocess_data(data)
        data = recommender.train_kmeans(data)
        data = recommender.generate_tfidf(data)
        print("Dataset successfully loaded and preprocessed.")
    except FileNotFoundError:
        print("Dataset file not found. Please ensure 'product_dataset.csv' is available.")
        raise RuntimeError("Dataset file missing, cannot start the API.")

@app.route("/recommend/", methods=["POST"])
def recommend_products():
    # Parse the JSON request body
    request_data = request.get_json()

    # Validate the input data
    try:
        validated_data = RecommendationRequest(**request_data)
    except ValueError as e:
        abort(400, description="Invalid input data")

    if data is None:
        abort(500, description="Dataset is not loaded")

    # Handle user interaction data (prices) if provided
    if validated_data.user_interaction_data and validated_data.user_interaction_data.prices:
        user_data = pd.DataFrame({"Price": validated_data.user_interaction_data.prices})
        user_cluster = recommender.infer_user_cluster(user_data)
    else:
        user_cluster = None

    # Extract keywords
    keywords = recommender.extract_keywords(validated_data.keywords or "")

    # Get product recommendations
    recommendations = recommender.recommend_products(
        data, user_cluster=user_cluster, keywords=keywords
    )

    if recommendations.empty:
        abort(404, description="No recommendations found")

    return jsonify(recommendations.to_dict(orient="records"))

# Home Route
@app.route('/')
def home():
    return render_template('EC.html')

# Recommend Route (GET request for search-based recommendations)
@app.route('/recommend', methods=['GET'])
def recommend():
    load_dataset()


    if data is None:
        abort(500, description="Dataset is not loaded")

    keywords = request.args.get('keywords', '')

    if not keywords:
        return jsonify({'error': 'No search keywords provided'}), 400

    # Use recommender to get product recommendations based on the provided keywords
    recommendations = recommender.recommend_products(
        data, keywords=keywords
    )

    if not recommendations:
        return jsonify({'error': 'No recommendations found for the given keywords'}), 404

    return jsonify({'recommendations': recommendations})

if __name__ == "__main__":
    app.run(debug=True)
#python -m uvicorn ec:app --reload
#python ec.py
