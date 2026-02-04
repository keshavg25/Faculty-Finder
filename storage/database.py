import sqlite3
from sqlite3 import Error
import os

DB_FILE = "faculty_search.db"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(PROJECT_DIR), DB_FILE)

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def init_db():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

def create_tables(conn):
    create_faculty_table = """
    CREATE TABLE IF NOT EXISTS faculty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT,
        bio TEXT,
        research_interests TEXT,
        education TEXT,
        bio_text_clean TEXT,
        profile_url TEXT UNIQUE,
        image_url TEXT
    );
    """
    try:
        c = conn.cursor()
        c.execute(create_faculty_table)
        print("Tables created successfully.")
    except Error as e:
        print(f"Error creating tables: {e}")

if __name__ == '__main__':
    init_db()
