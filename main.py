import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes import recommend, analyze, trends, stylist

app = FastAPI(
    title="StyleSense API",
    description="Generative AI-Powered Fashion Recommendation System",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes — must be registered BEFORE the catch-all static mount
app.include_router(recommend.router, prefix="/api", tags=["Recommend"])
app.include_router(analyze.router, prefix="/api", tags=["Analyze"])
app.include_router(trends.router, prefix="/api", tags=["Trends"])
app.include_router(stylist.router, prefix="/api", tags=["Stylist"])

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "StyleSense API"}

# Serve frontend — html=True means index.html is served at "/" and all
# other files (style.css, app.js) are served at their relative paths automatically
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  StyleSense AI Fashion System")
    print("="*50)
    print("  Backend: http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("  Frontend: http://localhost:8000")
    print("="*50 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
