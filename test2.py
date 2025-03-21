import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://yaswitha:Microtek123%40@cluster0.m06cm.mongodb.net/")
db = client["test"]
collection = db["courses"]

# Function to scrape 'Take Course' link
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

# Function to update 'Take Course Link' in MongoDB
def update_take_course_links():
    # Fetch all courses
    courses = collection.find({})

    for course in courses:
        link = course['Link']  # Assuming 'Link' field has the URL to scrape
        take_course_url = scrape_specific_class_urls(link)

        # Update the course document in MongoDB
        collection.update_one(
            {"Title": course["Title"]},
            {"$set": {"Take Course Link": take_course_url}}
        )
        print(f"Updated 'Take Course Link' for: {course['Title']}")

# Run the update function
update_take_course_links()
print("Updated 'Take Course Link' in MongoDB.")
