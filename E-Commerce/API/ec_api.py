from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from ec import ProductRecommender

app = FastAPI()

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


@app.on_event("startup")
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


@app.post("/recommend/")
def recommend_products(request: RecommendationRequest):
    if data is None:
        raise HTTPException(status_code=500, detail="Dataset is not loaded")

    if request.user_interaction_data and request.user_interaction_data.prices:
        user_data = pd.DataFrame({"Price": request.user_interaction_data.prices})
        user_cluster = recommender.infer_user_cluster(user_data)
    else:
        user_cluster = None

    keywords = recommender.extract_keywords(request.keywords or "")

    recommendations = recommender.recommend_products(
        data, user_cluster=user_cluster, keywords=keywords
    )

    if recommendations.empty:
        raise HTTPException(status_code=404, detail="No recommendations found")

    return recommendations.to_dict(orient="records")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Product Recommendation API!"}

#python -m uvicorn ec_api:app --reload


