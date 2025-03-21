import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time, datetime

# MongoDB setup
client = MongoClient('mongodb+srv://yaswitha:Microtek123%40@cluster0.m06cm.mongodb.net/')  # Connect to MongoDB
db = client['test']  # Database name
collection = db['courses']  # Collection name

# Function to fetch the latest feed data from the RSS feed
def fetch_latest_feed():
    url = "https://www.discudemy.com/feed/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")

    feed_data = []
    for item in items:
        title = item.find("title").text
        description = item.find("description").text
        link = item.find("link").text
        pub_date = item.find("pubDate").text
        category = item.find("category").text if item.find("category") else None

        feed_data.append({
            "Title": title,
            "Description": description,
            "Link": link,
            "Publication Date": pub_date,
            "Category": category,
            "Image URL": None,
            "Take Course Link": None,
            "Timestamp": datetime.datetime.now()
        })

    return feed_data

# Function to scrape the image URL and "Take Course" link
def scrape_course_details(link):
    try:
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        og_image = soup.find('meta', property='og:image')
        image_url = og_image['content'] if og_image and og_image.get('content') else "No image found"

        take_course_button = soup.find('a', class_='ui big inverted green button discbtn')
        take_course_link = take_course_button['href'] if take_course_button else "No Take Course link found"

        return image_url, take_course_link
    except requests.RequestException as e:
        print(f"Error scraping details from {link}: {e}")
        return "Error fetching image", "Error fetching course link"

# Function to update the feed data in MongoDB
def update_feed_data():
    latest_feed = fetch_latest_feed()
    
    # Insert new items into MongoDB
    for item in latest_feed:
        if collection.count_documents({'Title': item['Title']}) == 0:
            collection.insert_one(item)
            print(f"Inserted new item: {item['Title']}")
        else:
            print(f"Item already exists: {item['Title']}")

# Function to update course details in MongoDB
def update_course_details():
    courses = collection.find({"Image URL": None})  # Find courses without image and course link
    
    for course in courses:
        image_url, take_course_link = scrape_course_details(course['Link'])
        collection.update_one(
            {'_id': course['_id']},
            {'$set': {'Image URL': image_url, 'Take Course Link': take_course_link}}
        )
        print(f"Updated course: {course['Title']}")

# Run the update functions
update_feed_data()
update_course_details()
