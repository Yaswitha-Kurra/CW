import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["courseworks"]
collection = db["courses"]

# Function to fetch the latest feed data from the RSS feed
def fetch_latest_feed():
    url = "https://www.discudemy.com/feed/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")

    # Create a list of dictionaries for each item
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
            "Image URL": None,  # Placeholder for the image URL
            "Take Course Link": None  # Placeholder for the take course link
        })

    return feed_data

# Function to scrape the image URL and "Take Course" link from the specified link
def scrape_course_details(link):
    try:
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Try to find the Open Graph image first
        og_image = soup.find('meta', property='og:image')
        image_url = og_image['content'] if og_image and og_image.get('content') else "No image found"

        # Scrape the "Take Course" link
        take_course_button = soup.find('a', class_='ui big inverted green button discbtn')
        take_course_link = take_course_button['href'] if take_course_button and 'href' in take_course_button.attrs else "No Take Course link found"

        return image_url, take_course_link
    except requests.RequestException as e:
        print(f"Error scraping details from {link}: {e}")
        return "Error fetching image", "Error fetching course link"

# Function to load existing data from MongoDB
def load_existing_data():
    return list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default `_id` field

# Function to save data to MongoDB
def save_to_mongodb(data):
    if data:
        collection.insert_many(data)

# Function to update the feed data
def update_feed_data():
    # Fetch the latest feed
    latest_feed = fetch_latest_feed()

    # Load existing data from MongoDB
    existing_data = load_existing_data()
    existing_titles = {item['Title'] for item in existing_data}

    # Find new items by comparing with existing data
    new_items = [item for item in latest_feed if item['Title'] not in existing_titles]

    # If new items are found, update MongoDB
    if new_items:
        save_to_mongodb(new_items)
        print(f"{len(new_items)} new items added to MongoDB.")
    else:
        print("No new items found.")

# Function to update image URLs and "Take Course" links in MongoDB
def update_course_details():
    # Fetch courses that need updating (Image URL or Take Course Link is None)
    courses = collection.find({"$or": [{"Image URL": None}, {"Take Course Link": None}]})

    for course in courses:
        link = course['Link']
        image_url, take_course_link = scrape_course_details(link)

        # Update the course in MongoDB
        collection.update_one(
            {"Title": course["Title"]},
            {"$set": {"Image URL": image_url, "Take Course Link": take_course_link}}
        )

        print(f"Updated details for: {course['Title']}")

# Run the update functions once
update_feed_data()
update_course_details()
