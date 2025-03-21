import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["courseworks"]
collection = db["courses"]

# Function to scrape URLs with the specific class
def scrape_specific_class_urls(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the anchor tag with the specific class for 'Take Course'
            specific_class = 'ui big inverted green button discBtn'
            specific_class_urls = [a['href'] for a in soup.find_all('a', class_=specific_class, href=True)]
            
            # If any URLs found, return the first one (assuming there's one primary link)
            if specific_class_urls:
                return specific_class_urls[0]
        else:
            print(f"Failed to retrieve the webpage: {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error while scraping {url}: {e}")
    
    return "No 'Take Course' link found"

# Function to load existing data from MongoDB
def load_existing_data():
    return list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default `_id` field

# Function to update 'Take Course' links in MongoDB
def update_take_course_links():
    # Load existing data from MongoDB
    existing_data = load_existing_data()

    # Update existing entries with 'Take Course' links
    for item in existing_data:
        link = item['Link']
        take_course_url = scrape_specific_class_urls(link)  # Scrape the 'Take Course' link
        
        # Update the course in MongoDB
        collection.update_one(
            {"Title": item["Title"]},
            {"$set": {"Take Course Link": take_course_url}}
        )

        print(f"Updated 'Take Course Link' for: {item['Title']}")

# Run the update function
update_take_course_links()
print("Updated 'Take Course' links in MongoDB.")
