import requests
import logging
import streamlit as st
import time
import os
import json
import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard User-Agent header for OpenStreetMap API compliance
USER_AGENT = "TripPlannerAgentCapstone/1.0 (contact@example.com)"
HEADERS = {"User-Agent": USER_AGENT}

# Map high-level interest groups to Overpass QL tag selectors
INTEREST_MAP = {
    "food": [
        'node["amenity"~"restaurant|cafe|pub|bar|food_court|ice_cream"]',
        'way["amenity"~"restaurant|cafe|pub|bar|food_court|ice_cream"]'
    ],
    "history": [
        'node["historic"]',
        'way["historic"]',
        'node["heritage"]',
        'way["heritage"]'
    ],
    "art": [
        'node["tourism"~"museum|gallery|artwork"]',
        'way["tourism"~"museum|gallery|artwork"]',
        'node["amenity"~"theatre|cinema"]',
        'way["amenity"~"theatre|cinema"]'
    ],
    "culture": [
        'node["tourism"~"museum|gallery|artwork"]',
        'way["tourism"~"museum|gallery|artwork"]',
        'node["amenity"~"theatre|cinema|library|cultural_centre"]',
        'way["amenity"~"theatre|cinema|library|cultural_centre"]'
    ],
    "outdoors": [
        'node["leisure"~"park|garden|nature_reserve|playground"]',
        'way["leisure"~"park|garden|nature_reserve|playground"]',
        'node["tourism"="viewpoint"]',
        'way["tourism"="viewpoint"]'
    ],
    "shopping": [
        'node["shop"~"mall|supermarket|clothes|souvenir|gift"]',
        'way["shop"~"mall|supermarket|clothes|souvenir|gift"]',
        'node["amenity"="marketplace"]',
        'way["amenity"="marketplace"]'
    ],
    "entertainment": [
        'node["tourism"~"theme_park|zoo|aquarium"]',
        'way["tourism"~"theme_park|zoo|aquarium"]',
        'node["amenity"~"nightclub|casino|cinema"]',
        'way["amenity"~"nightclub|casino|cinema"]'
    ]
}

@st.cache_data(show_spinner=False, ttl=86400)
def geocode_address(address: str) -> Optional[Dict[str, Any]]:
    """
    Geocodes an address or location name using Nominatim API.
    Uses caching and retry logic with exponential backoff.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Geocoding address: '{address}' (attempt {attempt + 1})")
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            
            # Handle rate limiting (HTTP 429)
            if response.status_code == 429:
                sleep_time = 2 * (attempt + 1)
                logger.warning(f"Nominatim rate limit hit. Waiting {sleep_time}s...")
                time.sleep(sleep_time)
                continue
                
            response.raise_for_status()
            results = response.json()
            
            if not results:
                logger.warning(f"No geocoding results found for address: '{address}'")
                return None
                
            result = results[0]
            geocoded = {
                "lat": float(result["lat"]),
                "lon": float(result["lon"]),
                "display_name": result["display_name"],
                "boundingbox": result.get("boundingbox", [])
            }
            logger.info(f"Successfully geocoded '{address}' to ({geocoded['lat']}, {geocoded['lon']})")
            return geocoded
            
        except requests.RequestException as e:
            logger.warning(f"Request attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Error during geocoding request after {max_retries} attempts: {e}")
                return None
            time.sleep(2 * (attempt + 1))
            
    return None

@st.cache_data(show_spinner=False, ttl=3600)
def _execute_overpass_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Executes a raw Overpass QL query with retries and caching.
    """
    url = "https://overpass-api.de/api/interpreter"
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Executing Overpass Query (attempt {attempt + 1})")
            response = requests.post(url, data={"data": query}, headers=HEADERS, timeout=30)
            
            if response.status_code == 429:
                sleep_time = 3 * (attempt + 1)
                logger.warning(f"Overpass rate limit hit. Waiting {sleep_time}s...")
                time.sleep(sleep_time)
                continue
                
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.warning(f"Overpass request attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Overpass API error after {max_retries} attempts: {e}")
                return None
            time.sleep(3 * (attempt + 1))
            
    return None

def categorize_poi(tags: Dict[str, str]) -> str:
    """
    Utility to map raw tags back to clean user interest categories.
    """
    if "amenity" in tags and tags["amenity"] in ["restaurant", "cafe", "pub", "bar", "food_court", "ice_cream"]:
        return "food"
    if "historic" in tags or "heritage" in tags:
        return "history"
    if "tourism" in tags and tags["tourism"] in ["museum", "gallery", "artwork"]:
        return "art"
    if "amenity" in tags and tags["amenity"] in ["theatre", "cinema", "library", "cultural_centre"]:
        return "culture"
    if "leisure" in tags and tags["leisure"] in ["park", "garden", "nature_reserve", "playground"]:
        return "outdoors"
    if "tourism" in tags and tags["tourism"] == "viewpoint":
        return "outdoors"
    if "shop" in tags or ("amenity" in tags and tags["amenity"] == "marketplace"):
        return "shopping"
    if "tourism" in tags and tags["tourism"] in ["theme_park", "zoo", "aquarium"]:
        return "entertainment"
    if "amenity" in tags and tags["amenity"] in ["nightclub", "casino"]:
        return "entertainment"
    
    # Generic categories if no direct interest group matches
    if "tourism" in tags:
        return tags["tourism"]
    if "amenity" in tags:
        return tags["amenity"]
    return "general"

def search_pois(city_name: str, interests: List[str], radius: int = 2000, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Unified tool to search for Points of Interest (POIs) based on a city name and interest filters.
    Geocodes the city name first, then fetches data from Overpass API.
    
    Args:
        city_name: Name of the target city (e.g. "Rome")
        interests: List of interest strings (e.g. ["food", "history"])
        radius: Search radius in meters
        limit: Max results to return
        
    Returns:
        A list of parsed POI dicts with:
        'poi_id', 'name', 'category', 'lat', 'lon', 'url'
    """
    # 1. Geocode location name
    location = geocode_address(city_name)
    if not location:
        logger.warning(f"Could not geocode location: '{city_name}'")
        return []
        
    lat = location["lat"]
    lon = location["lon"]
    
    # 2. Build Overpass QL query clauses
    query_clauses = []
    for interest in interests:
        interest_lower = interest.lower()
        if interest_lower in INTEREST_MAP:
            for clause in INTEREST_MAP[interest_lower]:
                query_clauses.append(f"{clause}(around:{radius}, {lat}, {lon});")
                
    # If no valid interests matched or list was empty, build a generic set of clauses
    if not query_clauses:
        logger.info("No categories specified or matched, falling back to default clauses.")
        query_clauses = [
            f'node["tourism"](around:{radius}, {lat}, {lon});',
            f'way["tourism"](around:{radius}, {lat}, {lon});',
            f'node["historic"](around:{radius}, {lat}, {lon});',
            f'way["historic"](around:{radius}, {lat}, {lon});',
            f'node["amenity"~"restaurant|cafe|pub"](around:{radius}, {lat}, {lon});',
            f'way["amenity"~"restaurant|cafe|pub"](around:{radius}, {lat}, {lon});'
        ]
        
    # Combine query statements
    combined_clauses = "\n      ".join(query_clauses)
    query = f"""
    [out:json][timeout:30];
    (
      {combined_clauses}
    );
    out center {limit};
    """
    
    # 3. Execute Overpass query with caching
    response_data = _execute_overpass_query(query)
    elements = response_data.get("elements", []) if response_data else []
    
    # Fallback search if no specific interest POIs found
    if not elements:
        logger.info(f"No specific POIs found for interests in '{city_name}'. Running broad fallback search.")
        fallback_clauses = [
            f'node["tourism"](around:{radius + 1000}, {lat}, {lon});',
            f'way["tourism"](around:{radius + 1000}, {lat}, {lon});',
            f'node["historic"](around:{radius + 1000}, {lat}, {lon});',
            f'way["historic"](around:{radius + 1000}, {lat}, {lon});'
        ]
        fallback_query = f"""
        [out:json][timeout:30];
        (
          {"\n      ".join(fallback_clauses)}
        );
        out center {limit};
        """
        fallback_response = _execute_overpass_query(fallback_query)
        if fallback_response:
            elements = fallback_response.get("elements", [])
            
    pois = []
    
    # 4. Parse elements
    for elem in elements:
        tags = elem.get("tags", {})
        name = tags.get("name")
        
        # We need a name to display
        if not name:
            continue
            
        # Get coordinates (ways returned by center will have center node coordinates)
        poi_lat = elem.get("lat")
        poi_lon = elem.get("lon")
        if not poi_lat or not poi_lon:
            center = elem.get("center", {})
            poi_lat = center.get("lat")
            poi_lon = center.get("lon")
            
        if not poi_lat or not poi_lon:
            continue
            
        # Determine category based on tags
        category = categorize_poi(tags)
        
        # Identify websites / URLs
        url = tags.get("website") or tags.get("contact:website") or tags.get("url")
        if not url:
            elem_id = elem.get("id")
            elem_type = elem.get("type", "node")
            url = f"https://www.openstreetmap.org/{elem_type}/{elem_id}"
            
        pois.append({
            "poi_id": f"{elem.get('type')}/{elem.get('id')}",
            "name": name,
            "category": category,
            "lat": float(poi_lat),
            "lon": float(poi_lon),
            "url": url
        })
        
    # Rank POIs based on feedback boost scores
    boosts = get_all_poi_boosts(city_name)
    pois.sort(key=lambda x: boosts.get(x["name"].lower(), 0.0), reverse=True)
        
    logger.info(f"Successfully processed and ranked {len(pois)} POIs for '{city_name}'")
    return pois[:limit]

def get_all_poi_boosts(city_name: str) -> Dict[str, float]:
    """
    Reads the feedback file and aggregates boost scores for a city.
    Upvote: +0.25, Downvote: -0.35
    """
    boosts = {}
    feedback_file = "data/feedback/poi_feedback.jsonl"
    if not os.path.exists(feedback_file):
        return boosts
        
    try:
        with open(feedback_file, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    if event.get("city", "").lower() == city_name.lower():
                        poi_name = event.get("poi_name", "").lower()
                        fb_type = event.get("feedback_type")
                        val = 0.25 if fb_type == "upvote" else -0.35
                        boosts[poi_name] = boosts.get(poi_name, 0.0) + val
                except Exception:
                    continue
    except Exception as e:
        logger.error(f"Error reading feedback file: {e}")
        
    return boosts

def record_poi_feedback(city: str, poi_name: str, poi_id: str, feedback_type: str):
    """
    Records a feedback event (upvote/downvote) in the JSONL database.
    """
    os.makedirs("data/feedback", exist_ok=True)
    feedback_file = "data/feedback/poi_feedback.jsonl"
    event = {
        "timestamp": datetime.datetime.now().isoformat(),
        "city": city.lower(),
        "poi_name": poi_name,
        "poi_id": poi_id,
        "feedback_type": feedback_type
    }
    try:
        with open(feedback_file, "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
