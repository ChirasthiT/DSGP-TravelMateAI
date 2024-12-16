import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
import re



data = pd.read_csv("product_dataset.csv")

# Preprocessing, converting text to lower case , cleaning
data['Description'] = data['Description'].fillna("").str.lower()

# Normalize Price
scaler = MinMaxScaler()
data['Normalized Price'] = scaler.fit_transform(data[['Price']])

# K-Means Clustering on Price
def kmeans_clustering(data, n_clusters=3):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    data['Price Cluster'] = kmeans.fit_predict(data[['Normalized Price']])
    return kmeans

# Determine Optimal Clusters using Elbow Method assigning each product to a cluster
inertia = []
for k in range(1, 10):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(data[['Normalized Price']])
    inertia.append(kmeans.inertia_)


# optimal number of clusters 3 high, low, moderate budget
optimal_clusters = 3
kmeans_model = kmeans_clustering(data, n_clusters=optimal_clusters)

plt.figure(figsize=(8, 5))
plt.plot(range(1, 10), inertia, marker='o')
plt.title('Elbow Method for Optimal Clusters')
plt.xlabel('Number of Clusters')
plt.ylabel('Inertia')
plt.show()

# TF-IDF for Descriptions finding unique keywords
tfidf = TfidfVectorizer(max_features=100)
tfidf_matrix = tfidf.fit_transform(data['Description'])

# Convert TF-IDF matrix to DataFrame for easier manipulation
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
data = pd.concat([data, tfidf_df], axis=1)

# Recommend Products Based on Budget and Keywords
def recommend_products_by_budget_and_keywords(budget=None, keywords=None, top_n=5):
    if keywords is None:
        keywords = []

    if budget:
              # Products are selected if their prices are within ±20% of the user's budget
        budget_min = budget * 0.8
        budget_max = budget * 1.2
        budget_products = data[(data['Price'] >= budget_min) & (data['Price'] <= budget_max)].copy()
    else:
        # If no budget is provided, consider all products
        budget_products = data.copy()

    # Filter by keywords using TF-IDF matrix
    matching_scores = []
    match_counts = []  # To store how many keywords matched

    for _, row in budget_products.iterrows():
        product_keywords = " ".join(row[tfidf_df.columns].index[row[tfidf_df.columns] > 0])
        matched = [keyword for keyword in keywords if keyword in product_keywords]
        match_counts.append(len(matched))  # Count matched keywords
        score = len(matched)  # The match score is based on the number of matches
        matching_scores.append(score)

    budget_products['Keyword Match Score'] = matching_scores
    budget_products['Matched Keywords Count'] = match_counts

    # Sort by highest match score and then by price
    recommendations = budget_products.sort_values(
        by=['Keyword Match Score', 'Price'], ascending=[False, True]
    ).head(top_n)

    # Calculate Accuracy: Total matched keywords vs. total user keywords
    if len(keywords) > 0:
        total_matched_keywords = recommendations['Matched Keywords Count'].sum()
        accuracy = total_matched_keywords / (len(keywords) * top_n)
    else:
        accuracy = None  # No keywords to match, so accuracy doesn't apply

    return recommendations[['Product Name', 'Category', 'Price', 'Keyword Match Score']], accuracy


#Tokenization and Stopword Removal for user text
def extract_keywords(input_text):
    # Convert to lowercase
    input_text = input_text.lower()

    # Remove special characters and digits using regular expression
    input_text = re.sub(r'[^a-z\s]', '', input_text)

    # Tokenize (split by space) and return list of words
    words = input_text.split()

    # You can expand the stop words list or use a library like NLTK for more advanced stopword removal.
    stopwords = set(['the', 'a', 'an', 'and', 'in', 'on', 'at', 'to', 'of', 'for', 'during', 'is', 'was'])

    # Remove stop words from the list
    keywords = [word for word in words if word not in stopwords]

    return keywords


# Example 1: User provides both budget and keywords

customer_budget = 5000  # Customer's budget
customer_keywords = extract_keywords("waterproof")
recommendations, accuracy = recommend_products_by_budget_and_keywords(customer_budget, customer_keywords)
print("Recommendations with Budget:")
print(recommendations)
print(f"Accuracy: {accuracy:.2%}" if accuracy else "Accuracy: N/A")
print("\n\n\n\n")

# Example 2: User provides only keywords
customer_keywords = extract_keywords("waterproof")
recommendations, accuracy = recommend_products_by_budget_and_keywords(keywords=customer_keywords)
print("\nRecommendations without Budget:")
print(recommendations)
print(f"Accuracy: {accuracy:.2%}" if accuracy else "Accuracy: N/A")
print("\n\n\n\n")



