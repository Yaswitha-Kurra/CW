from pymongo import MongoClient
from langdetect import detect, DetectorFactory, LangDetectException

DetectorFactory.seed = 0  # Ensure consistent language detection

client = MongoClient("mongodb://localhost:27017/")
db = client["test"]
collection = db["courses"]

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return None

def remove_non_english_courses():
    print("[INFO] Checking for non-English courses...")
    removed = 0
    for course in collection.find():
        lang_title = detect_language(course["Title"])
        lang_desc = detect_language(course["Description"])

        if lang_title != 'en' or lang_desc != 'en':
            collection.delete_one({"_id": course["_id"]})
            print(f"🗑️ Removed non-English course: {course['Title']}")
            removed += 1

    print(f"✅ Done. Removed {removed} non-English courses.\n")
    
if __name__ == "__main__":
    remove_non_english_courses()

