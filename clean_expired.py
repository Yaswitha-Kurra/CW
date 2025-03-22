import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# ========== MongoDB Configuration ==========
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "test"  # Replace with your DB name
COLLECTION_NAME = "courses"  # Replace with your collection name

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ========== Check if Course is Expired ==========
def is_course_expired(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        red_message = soup.find("div", class_="ui red message")
        if red_message and ("Sorry guys" in red_message.text or "Sorry Guys" in red_message.text):
            print(f"🟥 Course expired (red message): {url}")
            return True

        if "Sorry guys" in soup.get_text() or "Sorry Guys" in soup.get_text():
            print(f"🟥 Course expired (fallback text): {url}")
            return True

        print(f"✅ Course still valid: {url}")
        return False

    except Exception as e:
        print(f"[ERROR] Could not fetch {url}: {e}")
        return False

# ========== Mark Expired Courses in DB ==========
def clean_expired_courses():
    print("🔎 Starting expired course check...")
    total = 0
    expired_count = 0

    for course in collection.find():
        total += 1
        url = course.get("Link")
        if not url:
            continue

        print(f"\n→ Checking course: {url}")
        if is_course_expired(url):
            collection.update_one(
                {"_id": course["_id"]},
                {"$set": {"expired": True}}
            )
            print("🗑️ Marked as expired in database.")
            expired_count += 1

    print(f"\n✅ Finished: {total} courses checked, {expired_count} marked as expired.")

# ========== Entry Point ==========
if __name__ == "__main__":
    clean_expired_courses()
