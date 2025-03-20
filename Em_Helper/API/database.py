from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://admin:admindsgp66@dsgp.e5yrm.mongodb.net/')
DB_NAME = os.getenv('DB_NAME', 'travelmateai')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'sos_alerts')

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"Connected to MongoDB database: {DB_NAME}")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None
    db = None
    collection = None


def save_sos_alert(alert_data):
    if collection is None:
        print("Warning: MongoDB connection not available. Alert not saved.")
        return None

    if 'timestamp' not in alert_data:
        alert_data['timestamp'] = datetime.now().isoformat()

    try:
        result = collection.insert_one(alert_data)
        print(f"SOS Alert saved with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving SOS alert to MongoDB: {e}")
        return None


def get_all_alerts():
    if collection is None:
        print("Warning: MongoDB connection not available.")
        return []

    try:
        alerts = list(collection.find({}, {'_id': 0}))
        return alerts
    except Exception as e:
        print(f"Error retrieving SOS alerts from MongoDB: {e}")
        return []