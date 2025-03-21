import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

class TourismRecommender:
    def __init__(self):
        self.mlb_interests = None
        self.le_budget = None
        self.le_companion = None
        self.models = {}
        self.location_activities_dict = {}

    def load_and_preprocess_data(self, dataset_path, location_activities_path):
        # Load datasets
        df = pd.read_csv("Itenary/data/Itinerary Builder Dataset (FINAL).csv", encoding='latin-1')
        location_activities_df = pd.read_csv("Itenary/data/Location_and_Activities (FINAL).csv", encoding='latin-1')

        # Create location-activities dictionary
        for _, row in location_activities_df.iterrows():
            activities = [act.strip() for act in row['Activity'].split(',')]
            self.location_activities_dict[row['Location'].lower()] = activities

        # Preprocess interest categories
        df['Interest Categories'] = df['Interest Categories'].str.lower()
        df['Interest Categories'] = df['Interest Categories'].apply(lambda x: [cat.strip() for cat in x.split(',')])

        # Encode interest categories
        self.mlb_interests = MultiLabelBinarizer()
        interest_encoded = self.mlb_interests.fit_transform(df['Interest Categories'])
        interest_df = pd.DataFrame(interest_encoded, columns=self.mlb_interests.classes_)

        # Encode budget and companion
        df['Budget Level'] = df['Budget Level'].str.lower()
        df['Travelling with whom'] = df['Travelling with whom'].str.lower()

        self.le_budget = LabelEncoder()
        self.le_companion = LabelEncoder()

        df['Budget Level'] = self.le_budget.fit_transform(df['Budget Level'])
        df['Travelling with whom'] = self.le_companion.fit_transform(df['Travelling with whom'])

        # Train separate model for each location
        unique_locations = df['Location'].unique()

        for location in unique_locations:
            location_data = df[df['Location'] == location].copy()

            if len(location_data) > 0:
                # Get interest features for this location's data
                location_interests = interest_df.iloc[location_data.index]

                # Combine features
                X = pd.concat([
                    location_data[['Budget Level', 'Travelling with whom']].reset_index(drop=True),
                    location_interests.reset_index(drop=True)
                ], axis=1)

                # Get activities for this location
                y = location_data['Activity'].reset_index(drop=True)

                # Train model
                model = RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    class_weight='balanced'
                )
                model.fit(X, y)
                self.models[location.lower()] = model

    def recommend_activities(self, location, interests, budget, companion, max_recommendations=5):
        """Recommend activities for a specific location based on user preferences"""
        location = location.lower()

        # Verify location exists
        if location not in self.location_activities_dict:
            return []

        # Get valid activities for this location
        valid_activities = self.location_activities_dict[location]

        if location not in self.models:
            # If no model for location, return some default activities
            return valid_activities[:max_recommendations]

        try:
            # Encode budget and companion
            budget_encoded = self.le_budget.transform([budget.lower()])[0]
            companion_encoded = self.le_companion.transform([companion.lower()])[0]

            # Encode interests
            interest_vector = np.zeros(len(self.mlb_interests.classes_))
            for interest in interests:
                interest = interest.lower().strip()
                if interest in [c.lower() for c in self.mlb_interests.classes_]:
                    idx = [c.lower() for c in self.mlb_interests.classes_].index(interest)
                    interest_vector[idx] = 1

            # Combine features
            input_vector = np.concatenate(([budget_encoded, companion_encoded], interest_vector))
            input_vector = input_vector.reshape(1, -1)

            # Get predictions
            model = self.models[location]
            predictions = model.predict_proba(input_vector)[0]
            activities = model.classes_

            # Sort activities by prediction probability
            activity_scores = list(zip(activities, predictions))
            activity_scores.sort(key=lambda x: x[1], reverse=True)

            # Filter valid activities
            recommended_activities = []
            for activity, _ in activity_scores:
                activity = activity.strip()
                if activity in valid_activities and len(recommended_activities) < max_recommendations:
                    recommended_activities.append(activity)

            return recommended_activities

        except Exception as e:
            print(f"Error processing recommendations for {location}: {e}")
            return valid_activities[:max_recommendations]

def format_extracted_info(extracted_info):
    """Format the extracted information from string output to dictionary"""
    # Initialize default values
    locations = []
    companion = "solo"
    interests = []
    budget = "medium"

    # Extract information from the string
    lines = extracted_info.split('\n')
    for line in lines:
        if "Destinations:" in line:
            locations = [loc.strip() for loc in line.split('Destinations:')[1].strip().split(',')]
        elif "Traveling with:" in line:
            companion = line.split('Traveling with:')[1].strip()
            if companion == "Not specified":
                companion = "solo"
        elif "Interest Categories:" in line:
            interests = [interest.strip().lower() for interest in line.split('Interest Categories:')[1].strip().split(',')]
        elif "Budget level:" in line:
            budget = line.split('Budget level:')[1].strip()
            if budget == "Not specified":
                budget = "medium"

    return {
        'locations': locations,
        'companion': companion,
        'interests': interests,
        'budget': budget
    }

def create_integrated_recommender(extracted_info_str):
    """Create recommendations based on keyword extraction results"""
    # Format the extracted information
    extracted_info = format_extracted_info(extracted_info_str)

    # Initialize recommender
    recommender = TourismRecommender()

    # Load and preprocess data
    recommender.load_and_preprocess_data(
        "Itenary/data/Itinerary Builder Dataset (FINAL).csv",
        "Itenary/data/Location_and_Activities (FINAL).csv"
    )

    # Generate recommendations for each location
    recommendations = {}
    for location in extracted_info['locations']:
        activities = recommender.recommend_activities(
            location=location,
            interests=extracted_info['interests'],
            budget=extracted_info['budget'],
            companion=extracted_info['companion'],
            max_recommendations=5
        )
        recommendations[location] = activities

    return recommendations