import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from time import sleep

# ========== MongoDB Configuration ==========
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "test"  # 🔁 Replace with your DB name
COLLECTION_NAME = "courses"  # 🔁 Replace with your collection name

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ========== Expiry Check Function ==========
def is_course_expired(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        red_message = soup.find("div", class_="ui red message")
        if red_message:
            print("[FOUND] Red message detected:", red_message.text.strip())
            if "Sorry guys" in red_message.text or "Sorry Guys" in red_message.text:
                print("✅ Course is EXPIRED.")
                return True

        if "Sorry guys" in soup.get_text() or "Sorry Guys" in soup.get_text():
            print("[FALLBACK] 'Sorry guys' found in page body.")
            print("✅ Course is EXPIRED.")
            return True

        print("[OK] Course is still valid.")
        return False

    except Exception as e:
        print("[ERROR] Failed to fetch page:", e)
        return False

# ========== Main Cleanup Function ==========
def clean_expired_courses():
    print("[INFO] Checking for expired courses...")
    total = 0
    removed = 0

    for course in collection.find():
        total += 1
        url = course.get("Link")
        if not url:
            continue

        print(f"\n🔍 Checking: {url}")
        if is_course_expired(url):
            collection.delete_one({"_id": course["_id"]})
            print(f"🗑️ Removed expired course from DB: {url}")
            removed += 1
        else:
            print("✅ Course is valid.")

    print(f"\n✅ DONE: Checked {total} courses. Removed {removed} expired.\n")

# ========== Run Periodically ==========
if __name__ == "__main__":
    while True:
        clean_expired_courses()
        print("[WAIT] Sleeping for 1 hours...\n")
        sleep(45 * 60)
