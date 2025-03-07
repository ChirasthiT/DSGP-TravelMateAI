from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "travelmateai"

client = MongoClient('mongodb+srv://admin:admindsgp66@dsgp.e5yrm.mongodb.net/')
db = client['travelmateai']
collection = db["sos_alerts"]

def save_sos_alert(alert_data):
    collection.insert_one(alert_data)
