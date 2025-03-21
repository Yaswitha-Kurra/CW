import time
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["courseworks"]
collection = db["courses"]

def insert_new_courses():
    print("Checking for new courses...")
    count = collection.count_documents({})
    print(f"Total courses in DB: {count}")

while True:
    insert_new_courses()
    time.sleep(180)  # Wait for 3 minutes before checking again
