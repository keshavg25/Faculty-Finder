# Faculty Research Semantic Search

## Overview
This project is a Semantic Search Engine designed to help students and researchers find faculty members at DA-IICT based on their research interests, biography, and publications. It scrapes faculty profiles from the official website, processes the data, and provides a semantic search API using sentence transformers.


## Tech Stack
*   **Language**: Python 3.8+
*   **Web Scraping**: `requests`, `BeautifulSoup4`
*   **API Framework**: `FastAPI`, `Uvicorn`
*   **Data Processing**: `Pandas` (implicit), Regular Expressions
*   **Database**: `SQLite` (Lightweight relational storage)
*   **Machine Learning**: `SentenceTransformers` (Hugging Face), `NumPy`, `FAISS` (for vector operations)

## Features
- **Data Ingestion**: Scrapes faculty profiles from multiple categories (Faculty, Professor of Practice, Adjunct, etc.) on the DA-IICT website.
- **ETL Pipeline**: Cleans and transforms raw scraped data into a structured format.
- **Storage**: Stores faculty data in a SQLite database.
- **Semantic Search**: Uses `all-MiniLM-L6-v2` (SentenceTransformer) to generate embeddings for faculty bios and research interests, enabling natural language search queries.
- **REST API**: fastAPI-based backend to serve faculty data and search results.

## Data Statistics
The cleaned dataset in `faculty_search.db` contains the following statistics:
- **Total Cleaned Records**: 111
- **Total Columns**: 8
- **Columns**: `id`, `name`, `department`, `bio`, `research_interests`, `education`, `bio_text_clean`, `profile_url`
  - **Records with Missing Bio**: 4
  - **Records with Missing research_interests**: 3

## Project Structure
```
Faculty-Finder/
├── api/
│   └── main.py             # FastAPI application entry point
├── data/
│   ├── raw_faculty.json    # Scraped raw data
│   ├── faculty_metadata.pkl # Search index metadata
│   └── faculty_embeddings.pkl # Search index embeddings
├── ingestion/
│   └── scraper.py          # Web scraper for DA-IICT faculty pages
├── semantic_search/
│   └── search_engine.py    # Logic for generating embeddings and searching
├── storage/
│   └── database.py         # SQLite database operations
├── transformation/
│   └── etl.py              # Extract, Transform, Load logic
├── requirements.txt        # Python dependencies
├── main.py                 # (Optional) Alternative entry point
└── faculty_search.db       # SQLite database file
```
## Schema
```
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
```
## Installation

1. **Clone the repository** (if applicable).
2. **Install Dependencies**:
   Ensure you have Python installed. Run the following command to install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Follow these steps to set up and run the system:

### 1. Ingest Data (Scraping)
Run the scraper to fetch the latest faculty profiles from the website.
```bash
python ingestion/scraper.py
```
This will fetch the data and save it to `data/raw_faculty.json`.

### 2. Transform and Load Data (ETL)
Process the raw data and load it into the SQLite database.
```bash
python transformation/etl.py
```
This creates/updates `faculty_search.db`.

### 3. Build Search Index (Optional but Recommended)
The search engine builds the index automatically on the first search, but you can trigger it manually/verify it by running:
```bash
python semantic_search/search_engine.py
```

### 4. Start the API Server
Launch the FastAPI server to expose endpoints.
```bash
python api/main.py
```
The API will be available at `http://localhost:8000`.

## API Endpoints

Once the server is running, access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints:
- `GET /`: Welcome message.
- `GET /health`: Health check for API and Database.
- `GET /faculty/all`: Retrieve all faculty members.
- `GET /faculty/{faculty_id}`: Retrieve details of a specific faculty member.
- `GET /search?q={query}&k={limit}`: Perform a semantic search.
  - Example: `http://localhost:8000/search?q=machine%20learning&k=3`