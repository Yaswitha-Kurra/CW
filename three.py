import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["courseworks"]
collection = db["courses"]

# Function to scrape URL from class 'ui segment'
def scrape_ui_segment_url(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the div with class 'ui segment'
            ui_segment = soup.find('div', class_='ui segment')
            
            # Find the anchor tag inside this div and get its href attribute
            if ui_segment:
                anchor_tag = ui_segment.find('a', href=True)
                if anchor_tag:
                    return anchor_tag['href']
                else:
                    print(f"No anchor tag found inside 'ui segment' in {url}")
            else:
                print(f"No 'ui segment' class found in {url}")
        else:
            print(f"Failed to retrieve the webpage: {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error while scraping {url}: {e}")
    
    return None

# Function to update 'Scraped UI Segment URL' in MongoDB
def update_ui_segment_links():
    # Fetch all courses with a 'Take Course Link'
    courses = collection.find({"Take Course Link": {"$exists": True, "$ne": None}})

    for course in courses:
        take_course_link = course["Take Course Link"]
        scraped_url = scrape_ui_segment_url(take_course_link)

        if scraped_url:
            # Update the course document in MongoDB
            collection.update_one(
                {"Title": course["Title"]},
                {"$set": {"Scraped UI Segment URL": scraped_url}}
            )
            print(f"Updated Scraped UI Segment URL for: {course['Title']}")

# Run the update function
update_ui_segment_links()
print("Updated 'Scraped UI Segment URL' in MongoDB.")
