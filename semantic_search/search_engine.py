import os
import sys
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer, util

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database import create_connection

MODEL_NAME = 'all-MiniLM-L6-v2'
EMBEDDINGS_FILE = "faculty_embeddings.pkl"
METADATA_FILE = "faculty_metadata.pkl"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
EMBEDDINGS_PATH = os.path.join(DATA_DIR, EMBEDDINGS_FILE)
METADATA_PATH = os.path.join(DATA_DIR, METADATA_FILE)

class SemanticSearchEngine:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.embeddings = None
        self.faculty_ids = []
        self.loaded = False
        if os.path.exists(EMBEDDINGS_PATH) and os.path.exists(METADATA_PATH):
            self.load_index()

    def build_index(self):
        conn = create_connection()
        if not conn:
            print("DB Connection failed")
            return
        cursor = conn.cursor()
        cursor.execute("SELECT id, bio_text_clean FROM faculty WHERE bio_text_clean IS NOT NULL AND bio_text_clean != ''")
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            print("No data to index.")
            return
        self.faculty_ids = [r[0] for r in rows]
        texts = [r[1] for r in rows]
        print(f"Generating embeddings for {len(texts)} records...")
        self.embeddings = self.model.encode(texts, convert_to_tensor=True)
        self.save_index()
        self.loaded = True
        print("Index built and saved.")

    def save_index(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        with open(EMBEDDINGS_PATH, "wb") as f:
            pickle.dump(self.embeddings, f)
        with open(METADATA_PATH, "wb") as f:
            pickle.dump(self.faculty_ids, f)

    def load_index(self):
        with open(EMBEDDINGS_PATH, "rb") as f:
            self.embeddings = pickle.load(f)
        with open(METADATA_PATH, "rb") as f:
            self.faculty_ids = pickle.load(f)
        self.loaded = True
        print("Index loaded.")

    def search(self, query, top_k=5, threshold=0.3):
        if not self.loaded:
            print("Index not loaded. Building now...")
            self.build_index()
            if not self.loaded:
                return []
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        cosine_scores = util.cos_sim(query_embedding, self.embeddings)[0]
        top_results = np.argpartition(-cosine_scores, range(top_k))[:top_k]
        results = []
        for idx in top_results:
            idx = int(idx)
            score = float(cosine_scores[idx])
            if score < threshold:
                continue
            faculty_id = self.faculty_ids[idx]
            results.append({"id": faculty_id, "score": score})
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def get_faculty_details(self, faculty_ids):
        conn = create_connection()
        if not conn:
            return []
        
        placeholders = ','.join('?' for _ in faculty_ids)
        sql = f"SELECT id, name, department, bio, research_interests, education, profile_url, image_url FROM faculty WHERE id IN ({placeholders})"
        
        cursor = conn.cursor()
        cursor.execute(sql, faculty_ids)
        rows = cursor.fetchall()
        conn.close()
        
        details_map = {}
        for r in rows:
            details_map[r[0]] = {
                "id": r[0],
                "name": r[1],
                "department": r[2],
                "bio": r[3],
                "research_interests": r[4],
                "education": r[5],
                "profile_url": r[6],
                "image_url": r[7]
            }
        
        # Return in the order of requested IDs
        ordered_details = []
        for fid in faculty_ids:
            if fid in details_map:
                ordered_details.append(details_map[fid])
        return ordered_details

if __name__ == "__main__":
    engine = SemanticSearchEngine()
    engine.build_index()
    res = engine.search("sustainable energy")
    print("Test Search Results:", res)
