# Development Logs - Faculty Finder

Tracking technical issues and questions for LLM assistance.

---

1. Scraping 403 Forbidden Errors

Issue: Getting 403 Forbidden after the first few pages of scraping. User-Agent is set.

Prompt: "I'm getting a 403 Forbidden error when requesting the DA-IICT faculty page in scraper.py. How do I solve this?"

2. Dirty Data & Regex Cleaning

Issue: Text extraction contains newlines, extra spaces, and HTML entities.

Prompt: "I'm extracting the 'Research Interests' section, but the text is super messy. It's full of newlines, extra spaces, and sometimes hidden HTML entities. My current cleanup function just strips whitespace, but it's not enough. Can you help me write a robust Python function to clean this up into a nice comma-separated string? I have attached the photo of the sample text"

3. FastAPI Performance (Blocking the Event Loop)

Issue: Search endpoint blocks the entire API during model inference.

Prompt: "I built the search API with FastAPI. It works, but when I send a search query that triggers the SentenceTransformer model, the entire API freezes. Other users can't even hit the health endpoint until the search finishes. I'm defining the endpoint as async def search(...). how do i fix this?"

4. SQLite Database Locking

Issue: Concurrent read/write errors with SQLite.

Prompt: "I'm running a background script to update the faculty data every hour, but sometimes it crashes with a database locked error when I try to read from the API at the same time, is there a way to handle concurrent reads/writes better without rewriting everything to use?"

5. Dependency Conflicts (Numpy/Torch)

Issue: Version incompatibility between numpy and torch/sentence-transformers.

Prompt:"pip install -r requirements.txt is failing because of a conflict with torch versions required by sentence-transformers. How do I resolve this issue?
