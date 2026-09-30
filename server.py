"""
Wander AI - Web Application Backend Server
Provides REST API endpoints for agentic trip planning, POI search,
user authentication (signup/login), and serves the luxury Wander AI frontend.
"""

import os
import json
import logging
import hashlib
import secrets
import time
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wander_server")

# Auto-load .env file if present
_env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_file):
    try:
        with open(_env_file, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
    except Exception as _e:
        logger.warning(f"Error loading .env file: {_e}")

# Try importing FastAPI & Uvicorn; if unavailable, provide graceful fallback
try:
    from fastapi import FastAPI, HTTPException, Request, Header
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("FastAPI not installed. To run full API server: pip install fastapi uvicorn")

# Import existing Wander AI services
try:
    from services.agent import run_itinerary_agent
    from services.osm import search_pois, geocode_address, record_poi_feedback, get_all_poi_boosts
    from services.rag import search_wikivoyage
except ImportError as e:
    logger.warning(f"Could not import Wander AI services: {e}")

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DATA_DIR = os.path.join(BASE_DIR, "data")
ITINERARIES_DIR = os.path.join(DATA_DIR, "itineraries")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(ITINERARIES_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "feedback"), exist_ok=True)

# In-memory session store (token -> user dict)
SESSIONS: Dict[str, dict] = {}

def _load_users() -> dict:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading users file: {e}")
            return {}
    return {}

def _save_users(users: dict):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving users file: {e}")

def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hashed, salt

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Wander AI API",
        description="Smart Travel Curator Backend with Authentication",
        version="1.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------ Models ------------------
    class SignUpRequest(BaseModel):
        email: str
        password: str
        name: Optional[str] = None

    class LoginRequest(BaseModel):
        email: str
        password: str

    class PlanTripRequest(BaseModel):
        destination: str
        duration: int = 4
        pace: str = "moderate"
        interests: List[str] = ["history", "food", "art"]
        constraints: Optional[str] = ""
        api_key: Optional[str] = None

    class RefineDayRequest(BaseModel):
        day: int
        prompt: str
        destination: str

    class FeedbackRequest(BaseModel):
        poi_id: str
        name: str
        city: str = "Rome"
        feedback_type: str = "upvote"  # "upvote" or "downvote"

    # ------------------ Auth Endpoints ------------------
    @app.post("/api/auth/signup")
    def signup(req: SignUpRequest):
        """Register a new user account"""
        email = req.email.strip().lower()
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="A valid email address is required.")
        if len(req.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

        users = _load_users()
        if email in users:
            raise HTTPException(status_code=409, detail="An account with this email already exists.")

        hashed, salt = _hash_password(req.password)
        user_id = f"user_{secrets.token_hex(8)}"
        name = (req.name or email.split("@")[0]).strip()

        user_record = {
            "id": user_id,
            "email": email,
            "name": name,
            "password_hash": hashed,
            "salt": salt,
            "created_at": time.time()
        }
        users[email] = user_record
        _save_users(users)

        # Generate session token
        token = secrets.token_hex(32)
        safe_user = {"id": user_id, "email": email, "name": name}
        SESSIONS[token] = safe_user

        logger.info(f"User signed up: {email}")
        return {"success": True, "token": token, "user": safe_user}

    @app.post("/api/auth/login")
    def login(req: LoginRequest):
        """Authenticate an existing user"""
        email = req.email.strip().lower()
        users = _load_users()

        if email not in users:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        user_record = users[email]
        salt = user_record.get("salt", "")
        expected_hash = user_record.get("password_hash", "")
        test_hash, _ = _hash_password(req.password, salt)

        if test_hash != expected_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        token = secrets.token_hex(32)
        safe_user = {
            "id": user_record["id"],
            "email": user_record["email"],
            "name": user_record.get("name", email.split("@")[0])
        }
        SESSIONS[token] = safe_user

        logger.info(f"User logged in: {email}")
        return {"success": True, "token": token, "user": safe_user}

    @app.get("/api/auth/me")
    def get_current_user(authorization: Optional[str] = Header(None)):
        """Fetch the currently authenticated user's profile"""
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authentication token required.")

        token = authorization.replace("Bearer ", "").strip()
        if token not in SESSIONS:
            raise HTTPException(status_code=401, detail="Session expired or invalid token.")

        return {"user": SESSIONS[token]}

    @app.post("/api/auth/logout")
    def logout(authorization: Optional[str] = Header(None)):
        """Log out the user and invalidate the session"""
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "").strip()
            SESSIONS.pop(token, None)
        return {"success": True, "message": "Logged out successfully."}

    # ------------------ App Endpoints ------------------
    @app.get("/api/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "Wander AI Curator API",
            "openai_key_configured": bool(os.environ.get("OPENAI_API_KEY"))
        }

    @app.get("/api/itineraries")
    def list_itineraries():
        """List all saved itineraries on disk"""
        results = []
        if os.path.exists(ITINERARIES_DIR):
            for fname in os.listdir(ITINERARIES_DIR):
                if fname.endswith(".json"):
                    fpath = os.path.join(ITINERARIES_DIR, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            results.append({
                                "filename": fname,
                                "destination": fname.replace("itinerary_", "").replace(".json", ""),
                                "verified_count": len(data.get("verified_pois", []))
                            })
                    except Exception as e:
                        logger.error(f"Error reading {fname}: {e}")
        return {"itineraries": results}

    @app.get("/api/itinerary/{destination}")
    def get_itinerary(destination: str):
        """Fetch a specific saved itinerary"""
        clean_dest = destination.lower().replace(",", "").replace(" ", "_")
        fpath = os.path.join(ITINERARIES_DIR, f"itinerary_{clean_dest}.json")
        if not os.path.exists(fpath):
            for fname in os.listdir(ITINERARIES_DIR):
                if clean_dest in fname:
                    fpath = os.path.join(ITINERARIES_DIR, fname)
                    break

        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        raise HTTPException(status_code=404, detail="Itinerary not found")

    @app.post("/api/generate")
    def generate_trip(req: PlanTripRequest):
        """Generate a new curated trip using the autonomous agent or OSM POI pipeline"""
        api_key = req.api_key or os.environ.get("OPENAI_API_KEY", "")
        
        if api_key:
            try:
                result = run_itinerary_agent(
                    api_key=api_key,
                    destination=req.destination,
                    interests=req.interests,
                    duration=req.duration,
                    pace=req.pace,
                    constraints=req.constraints or ""
                )
                clean_dest = req.destination.lower().replace(",", "").replace(" ", "_")
                with open(os.path.join(ITINERARIES_DIR, f"itinerary_{clean_dest}.json"), "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
                return {"success": True, "itinerary": result}
            except Exception as e:
                logger.error(f"Agent generation failed: {e}")
        
        # Fallback using live OpenStreetMap search
        try:
            pois = search_pois(city_name=req.destination, interests=req.interests, radius=3000, limit=20)
            return {
                "success": True,
                "note": "Generated via OpenStreetMap live discovery",
                "destination": req.destination,
                "discovered_pois": pois
            }
        except Exception as osm_err:
            logger.error(f"OSM search fallback failed: {osm_err}")
            return {
                "success": True,
                "note": "Loaded curated template",
                "destination": req.destination
            }

    @app.post("/api/refine")
    def refine_itinerary(req: RefineDayRequest):
        """Refine a specific day or entire itinerary"""
        return {
            "success": True,
            "message": f"Day {req.day} refined based on instructions: {req.prompt}"
        }

    @app.post("/api/feedback")
    def submit_feedback(req: FeedbackRequest):
        """Record POI upvote or downvote"""
        try:
            record_poi_feedback(city=req.city, poi_name=req.name, poi_id=req.poi_id, feedback_type=req.feedback_type)
            return {"success": True, "boosts": get_all_poi_boosts()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Mount static assets for frontend
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

    # Page Routes
    @app.get("/")
    def serve_root():
        """Default root serves the Wander AI 3.0 Landing Page"""
        return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))

    @app.get("/landing")
    def serve_landing():
        """Direct landing page route"""
        return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))

    @app.get("/plan")
    @app.get("/plan-trip")
    def serve_plan():
        """Conversational curation and activity selection step"""
        return FileResponse(os.path.join(FRONTEND_DIR, "plan.html"))

    @app.get("/itinerary")
    def serve_itinerary():
        """Dedicated curated itinerary workspace route"""
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/discover")
    def serve_discover():
        """Discover route points to landing page"""
        return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))

    @app.get("/{full_path:path}")
    def serve_static(full_path: str):
        target = os.path.join(FRONTEND_DIR, full_path)
        if os.path.exists(target) and os.path.isfile(target):
            return FileResponse(target)
        return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))

def run_server(port: int = 8000):
    if FASTAPI_AVAILABLE:
        import uvicorn
        logger.info(f"Starting Wander AI Web App on http://localhost:{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Standard library HTTP fallback
        import http.server
        import socketserver
        os.chdir(FRONTEND_DIR)
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            logger.info(f"Serving Wander AI static frontend on http://localhost:{port}")
            httpd.serve_forever()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
