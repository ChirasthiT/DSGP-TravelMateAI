from pymongo import MongoClient

client = MongoClient('mongodb+srv://admin:admindsgp66@dsgp.e5yrm.mongodb.net/')
db = client['travelmateai']
user_db_collection = db["user"]

def get_user_details(user_name):

    user = user_db_collection.find_one({"username": user_name}, {"_id": 0})
    return user

def get_user_Budget(user_name):
    user_budget = user_db_collection.find_one({"username": user_name}, {"_id": 0})
    return user_budget['budget']
def get_user_district(user_name):
    user_budget = user_db_collection.find_one({"username": user_name}, {"_id": 0})
    return user_budget['district']


user_name = "vv"
user_details = get_user_district(user_name)

if user_details:
    print(user_details)
else:
    print("User not found.")
