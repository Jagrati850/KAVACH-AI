import uvicorn
from app.main import app

if __name__ == "__main__":
    print("[KAVACH AI] Starting server on http://localhost:8000")
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
