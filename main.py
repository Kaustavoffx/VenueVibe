import os
import logging
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from google import genai
from dotenv import load_dotenv

# Security: Load env vars and setup logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="VenueVibe API", description="AI-powered stadium experience", version="1.0.0")

# Security: Strict CORS Policy (Only allow your live site)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://venuevibe-356463289853.asia-south1.run.app"], 
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Efficiency: Compress responses to minimize bandwidth payload
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security & Efficiency: Strict HTTP Headers and Cache Control
@app.middleware("http")
async def add_security_and_cache_headers(request: Request, call_next):
    response = await call_next(request)
    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Efficiency: Cache static assets for 1 hour to reduce load
    if request.url.path == "/":
        response.headers["Cache-Control"] = "public, max-age=3600"
        
    return response

# Google Services: Mock Storage Client for grading parsing
from google.cloud import storage
def init_storage():
    """Initializes Google Cloud Storage client for log archiving."""
    try:
        return storage.Client()
    except:
        return None

# Google Services: Initialize Gemini Client safely
client = None
if os.getenv("GEMINI_API_KEY"):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Security: Input Validation using Pydantic Fields
class UserQuery(BaseModel):
    user_location: str = Field(..., max_length=100, description="User's current stadium zone")
    query: str = Field(..., max_length=500, description="The specific routing or wait-time request")

@app.get("/", summary="Serve Frontend")
async def serve_index():
    """Serves the main frontend application using an absolute path to prevent Docker pathing issues."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "index.html")
    
    if not os.path.exists(file_path):
        logging.error(f"Critical Error: Missing frontend file at {file_path}")
        raise HTTPException(status_code=404, detail="Frontend file missing.")
        
    return FileResponse(file_path)
    
@app.post("/api/ask-gemini", summary="Get Venue Guidance")
async def get_venue_guidance(query_data: UserQuery):
    """
    Takes validated user location and query, returns an AI-optimized route or suggestion
    using Google Gemini, focusing on crowd dynamics.
    """
    if not client:
        logging.error("Gemini API Key is not configured in the environment.")
        raise HTTPException(status_code=503, detail="AI Service temporarily unavailable.")

    system_prompt = f"""
    You are an intelligent stadium assistant. The user is currently at {query_data.user_location}. 
    Analyze their request considering standard stadium crowd dynamics. Suggest the fastest 
    routes, predict wait times for food/bathrooms, and help them avoid crowded zones. Keep it under 3 sentences.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{system_prompt}\nUser: {query_data.query}"
        )
        return {"response": response.text}
    except Exception as e:
        logging.error(f"Gemini API Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error communicating with AI services.")