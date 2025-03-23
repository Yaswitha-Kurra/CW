import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from PIL import Image
from io import BytesIO
import time, datetime, os
import re

# MongoDB setup
client = MongoClient('mongodb://localhost:27017')
db = client['test']
collection = db['courses']

# Folder for compressed images
compressed_image_folder = '/Users/yaswithakurra/Documents/CW UI/static/compressed_images'
os.makedirs(compressed_image_folder, exist_ok=True)

# === Fetch latest feed data ===
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

# === Scrape image and "Take Course" link, compress image ===
def scrape_course_details(link, title):
    try:
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        og_image = soup.find('meta', property='og:image')
        image_url = og_image['content'] if og_image and og_image.get('content') else None
        compressed_image_path = None

        if image_url:
            try:
                img_response = requests.get(image_url, stream=True, timeout=10)
                if img_response.status_code == 200:
                    img = Image.open(BytesIO(img_response.content))
                    img = img.resize((400, 225))  # Resize image
                    # Clean filename
                    safe_title = re.sub(r'[^\w\-_.]', '_', title)  # Replace unsafe chars with underscores
                    filename = f"{safe_title}.jpg"
                    filepath = os.path.join(compressed_image_folder, filename)
                    img.save(filepath, format="JPEG", quality=60, optimize=True)
                    compressed_image_path = filepath.replace("/Users/yaswithakurra/Documents/CW UI/static/", "")  # relative path
                else:
                    print(f"Could not download image for {title}")
            except Exception as e:
                print(f"Image compression failed for {title}: {e}")
        else:
            print(f"No image found for {title}")

        take_course_button = soup.find('a', class_='ui big inverted green button discbtn')
        take_course_link = take_course_button['href'] if take_course_button else "No Take Course link found"

        return compressed_image_path or image_url, take_course_link

    except requests.RequestException as e:
        print(f"Error scraping details from {link}: {e}")
        return "Error fetching image", "Error fetching course link"

# === Insert new feed items ===
def update_feed_data():
    latest_feed = fetch_latest_feed()

    for item in latest_feed:
        if collection.count_documents({'Title': item['Title']}) == 0:
            collection.insert_one(item)
            print(f"Inserted new item: {item['Title']}")
        else:
            print(f"Item already exists: {item['Title']}")

# === Update image + course link ===
def update_course_details():
    courses = collection.find({"Image URL": None})  # Only those missing image

    for course in courses:
        image_url, take_course_link = scrape_course_details(course['Link'], course['Title'])
        collection.update_one(
            {'_id': course['_id']},
            {'$set': {
                'Image URL': image_url,
                'Take Course Link': take_course_link
            }}
        )
        print(f"Updated course: {course['Title']}")

# === Run ===
update_feed_data()
update_course_details()
