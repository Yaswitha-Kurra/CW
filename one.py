import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["test"]
collection = db["courses"]

def fetch_latest_feed():
    url = "https://www.discudemy.com/feed/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")

    new_courses = []
    for item in items:
        title = item.find("title").text
        description = item.find("description").text
        link = item.find("link").text
        pub_date = item.find("pubDate").text
        category = item.find("category").text if item.find("category") else None

        # Check if course already exists
        if not collection.find_one({"Title": title}):
            course = {
                "Title": title,
                "Description": description,
                "Link": link,
                "Publication Date": pub_date,
                "Category": category,
                "Image URL": None,
                "Take Course Link": None
            }
            collection.insert_one(course)
            new_courses.append(course)

    print(f"{len(new_courses)} new courses added.")

# Fetch and update feed data
fetch_latest_feed()
