from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_search.search_engine import SemanticSearchEngine

app = FastAPI(title="Faculty Finder API", description="Recommender system for faculty")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance
search_engine = None

# Mount static files (UI)
# Ensure the ui directory exists relative to this file's parent
UI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui")
app.mount("/static", StaticFiles(directory=UI_DIR), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(UI_DIR, "index.html"))

@app.on_event("startup")
async def startup_event():
    global search_engine
    search_engine = SemanticSearchEngine()
    if not search_engine.loaded:
        print("Building index on startup...")
        search_engine.build_index()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/search")
def search_faculty(query: str, limit: int = 5, threshold: float = 0.3):
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    results = search_engine.search(query, top_k=limit, threshold=threshold)
    if not results:
        return []
        
    ids = [r['id'] for r in results]
    details = search_engine.get_faculty_details(ids)
    
    # Merge scores
    for i, detail in enumerate(details):
        if i < len(results):
             detail['score'] = results[i]['score']
             
    return details

@app.get("/faculty/{faculty_id}")
def get_faculty(faculty_id: int):
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
        
    details = search_engine.get_faculty_details([faculty_id])
    if not details:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return details[0]
