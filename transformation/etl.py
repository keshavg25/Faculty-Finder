import json
import sqlite3
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database import create_connection, init_db

RAW_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw_faculty.json")

def clean_text(text):
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def parse_education(edu_text):
    return clean_text(edu_text)

def transform_data(raw_data):
    name = clean_text(raw_data.get("name", "Unknown"))
    url = raw_data.get("url", "")
    full_text = raw_data.get("full_text", "")
    sections = raw_data.get("sections", {})
    bio = clean_text(sections.get("biography", ""))
    research = clean_text(sections.get("specialization", "") or sections.get("research interests", ""))
    education = clean_text(sections.get("education", ""))
    bio_text_clean = f"{name}. {research}. {bio}. {education}"
    bio_text_clean = clean_text(bio_text_clean)
    return (name, "DA-IICT", bio, research, education, bio_text_clean, url, None)

def load_to_db(transformed_data):
    conn = create_connection()
    if not conn:
        print("Failed to connect to DB")
        return
    sql = ''' INSERT INTO faculty(name, department, bio, research_interests, education, bio_text_clean, profile_url, image_url)
              VALUES(?,?,?,?,?,?,?,?)
              ON CONFLICT(profile_url) DO UPDATE SET
              name=excluded.name,
              bio=excluded.bio,
              research_interests=excluded.research_interests,
              education=excluded.education,
              bio_text_clean=excluded.bio_text_clean; '''
    cur = conn.cursor()
    try:
        cur.executemany(sql, transformed_data)
        conn.commit()
        print(f"Successfully loaded {len(transformed_data)} records into database.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def main():
    if not os.path.exists(RAW_DATA_FILE):
        print(f"Raw data file not found at {RAW_DATA_FILE}")
        return
    init_db()
    with open(RAW_DATA_FILE, "r", encoding="utf-8") as f:
        raw_list = json.load(f)
    clean_records = []
    for record in raw_list:
        clean_records.append(transform_data(record))
    load_to_db(clean_records)

if __name__ == "__main__":
    main()
