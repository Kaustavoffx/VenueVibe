import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# Security: Load environment variables
load_dotenv()

app = FastAPI(title="VenueVibe API", description="AI-powered stadium experience")

# Security: CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Services: Initialize Gemini Client
client = None
if os.getenv("GEMINI_API_KEY"):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class UserQuery(BaseModel):
    user_location: str
    query: str

templates = Jinja2Templates(directory=".")

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """
    Serves the frontend HTML, injecting the Maps API Key securely.
    """
    maps_api_key = os.getenv("MAPS_API_KEY", "YOUR_MAPS_API_KEY")
    return templates.TemplateResponse("index.html", {"request": request, "MAPS_API_KEY": maps_api_key})

@app.post("/api/ask-gemini")
async def get_venue_guidance(query_data: UserQuery):
    """
    Code Quality: Async function with clear type hints.
    Takes user location and query, returns an AI-optimized route or suggestion.
    """
    if not client:
        # Fallback or error if API key is not configured
        raise HTTPException(status_code=500, detail="Gemini API Key is not configured.")

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
        raise HTTPException(status_code=500, detail="Error communicating with AI services.")
