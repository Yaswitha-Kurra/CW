from pymongo import MongoClient
from langdetect import detect, DetectorFactory, LangDetectException

DetectorFactory.seed = 0  # Ensure consistent language detection

client = MongoClient("mongodb://localhost:27017/")
db = client["courseworks"]
collection = db["courses"]

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return None

def remove_non_english_courses():
    courses = collection.find({})
    for course in courses:
        lang_title = detect_language(course["Title"])
        lang_desc = detect_language(course["Description"])

        if lang_title != 'en' or lang_desc != 'en':
            collection.delete_one({"Title": course["Title"]})
            print(f"Removed non-English course: {course['Title']}")

remove_non_english_courses()
