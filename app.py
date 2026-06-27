import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import streamlit as st
import pandas as pd
import pydeck as pdk
from typing import Dict, List, Any, Optional
from openai import OpenAI
from services.osm import geocode_address, search_pois, get_all_poi_boosts, record_poi_feedback
from services.rag import search_wikivoyage, get_rag_index
from services.agent import run_itinerary_agent

def get_day_color(day: int) -> list:
    # Distinct RGB colors for up to 14 days
    colors = [
        [74, 144, 226],   # Blue
        [46, 204, 113],   # Green
        [231, 76, 60],    # Red
        [241, 196, 15],   # Yellow
        [155, 89, 182],   # Purple
        [230, 126, 34],   # Orange
        [26, 188, 156],   # Teal
        [52, 73, 94],     # Dark Blue
        [243, 156, 18],   # Amber
        [192, 57, 43],    # Crimson
        [39, 174, 96],    # Emerald
        [142, 68, 173],   # Amethyst
        [22, 160, 133],   # Turquoise
        [127, 140, 141]   # Gray
    ]
    return colors[(day - 1) % len(colors)]

def map_pois_to_days(itinerary_text: str, verified_pois: list, discovered_pois: list) -> list:
    """
    Parses the itinerary text to assign days and order of appearance to verified POIs.
    """
    mapped_pois = []
    
    # Split text by '### Day'
    if "### Day" in itinerary_text:
        day_blocks = itinerary_text.split("### Day")
        
        for day_idx, day_content in enumerate(day_blocks[1:]):
            day_num = day_idx + 1
            # Search for all verified POIs in this day's text
            day_pois_found = []
            for v_name in verified_pois:
                # Find the full POI dict
                poi_dict = next((p for p in discovered_pois if p["name"].lower() == v_name.lower()), None)
                if poi_dict:
                    # Find index of appearance in this day's content
                    pos = day_content.lower().find(v_name.lower())
                    if pos != -1:
                        day_pois_found.append((pos, poi_dict))
            
            # Sort by position of appearance to get chronological order
            day_pois_found.sort(key=lambda x: x[0])
            
            for order_idx, (_, poi) in enumerate(day_pois_found):
                mapped_pois.append({
                    "name": poi["name"],
                    "category": poi["category"],
                    "lat": poi["lat"],
                    "lon": poi["lon"],
                    "url": poi["url"],
                    "poi_id": poi["poi_id"],
                    "day": day_num,
                    "order": order_idx + 1,
                    "color": get_day_color(day_num)
                })
    else:
        # Fallback if no day headers are found: assign all to day 1 in order of appearance
        found = []
        for v_name in verified_pois:
            poi_dict = next((p for p in discovered_pois if p["name"].lower() == v_name.lower()), None)
            if poi_dict:
                pos = itinerary_text.lower().find(v_name.lower())
                if pos != -1:
                    found.append((pos, poi_dict))
        found.sort(key=lambda x: x[0])
        for idx, (_, poi) in enumerate(found):
            mapped_pois.append({
                "name": poi["name"],
                "category": poi["category"],
                "lat": poi["lat"],
                "lon": poi["lon"],
                "url": poi["url"],
                "poi_id": poi["poi_id"],
                "day": 1,
                "order": idx + 1,
                "color": get_day_color(1)
            })
            
    return mapped_pois

def save_itinerary_to_disk(destination: str, data: dict):
    clean_dest = destination.lower().replace(",", "").replace(" ", "_")
    filepath = f"data/itineraries/itinerary_{clean_dest}.json"
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving to disk: {e}")

def load_itinerary_from_disk(destination: str) -> Optional[dict]:
    clean_dest = destination.lower().replace(",", "").replace(" ", "_")
    filepath = f"data/itineraries/itinerary_{clean_dest}.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading from disk: {e}")
            try:
                os.remove(filepath)
                logger.info(f"Deleted corrupted itinerary file: {filepath}")
            except Exception as rm_err:
                logger.error(f"Could not delete corrupted file {filepath}: {rm_err}")
    return None

# Create data directories programmatically
os.makedirs("data/feedback", exist_ok=True)
os.makedirs("data/itineraries", exist_ok=True)

# Set up page configurations
st.set_page_config(
    page_title="Wander AI - Capstone Project",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium UI CSS Injection
st.markdown(
    """
    <style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Global Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1e2640 100%);
        color: #ffffff;
    }
    
    /* Modern Glassmorphic Cards */
    .card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Header Styling */
    .header-container {
        text-align: center;
        padding: 35px 24px;
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    
    .header-subtitle {
        font-size: 1.25rem;
        color: #ffffff;
        font-weight: 300;
        opacity: 0.9;
    }
    
    /* Custom buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #4A90E2 0%, #357ABD 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(90deg, #357ABD 0%, #2A6296 100%);
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.5);
        transform: scale(1.02);
    }
    
    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: #0d111d !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Success, Info, Warning boxes */
    .stAlert {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# Header Section
st.markdown(
    """
    <div class="header-container">
        <div class="header-title">Wander AI</div>
        <div class="header-subtitle">Next-Generation Autonomous Trip & Itinerary Planner</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Session State Initialization
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = os.environ.get("OPENAI_API_KEY", "")
if "osm_test_location" not in st.session_state:
    st.session_state["osm_test_location"] = "Paris, France"

# Sidebar for API Key Management and Configuration
with st.sidebar:
    st.markdown("### Authentication")
    
    # Secure text input for API Key
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=st.session_state["openai_api_key"],
        type="password",
        placeholder="sk-proj-...",
        help="Input your OpenAI API key. It is stored securely in the app session state."
    )
    
    if api_key_input:
        st.session_state["openai_api_key"] = api_key_input
        
    # Validation Indicator
    if st.session_state["openai_api_key"]:
        st.success("API Key Provided")
        
        # Test validation on the fly
        if st.button("Validate Key"):
            with st.spinner("Checking OpenAI API connection..."):
                try:
                    client = OpenAI(api_key=st.session_state["openai_api_key"])
                    client.models.list()
                    st.toast("OpenAI Key validation successful!")
                    st.success("Key is valid!")
                except Exception as e:
                    st.error("Invalid API Key or connection error.")
                    st.exception(e)
                    
        # Option to clear the key
        if st.button("Clear Key"):
            st.session_state["openai_api_key"] = ""
            st.rerun()
    else:
        st.warning("Please provide an OpenAI API key to enable agentic workflows.")
        
    st.markdown("---")
    st.markdown("### Model & Agent Settings")
    
    model_selected = st.selectbox(
        "OpenAI Model",
        options=["gpt-4o-mini", "gpt-4o"],
        index=0,
        key="model_selectbox",
        help="Select the OpenAI Chat Completions model to use."
    )
    
    max_steps_val = st.slider(
        "Max Agent Loops",
        min_value=1,
        max_value=10,
        value=5,
        key="max_steps_slider",
        help="Maximum number of reasoning and tool calling steps allowed."
    )
    
    fast_mode_enabled = st.checkbox(
        "Fast Mode",
        value=False,
        key="fast_mode_checkbox",
        help="Limits agent loops to 2 steps for quicker compile times."
    )
        
    st.markdown("---")
    st.markdown("### System Status")
    st.info("OSM Nominatim Geocoder: Active\n\nOverpass POI Search: Active\n\nWikivoyage RAG: Active")
    st.caption("EmpowHER Capstone Project")

# Main Content Layout (using tabs)
tab_planner, tab_diag, tab_rag, tab_about = st.tabs(["Itinerary Planner", "API Diagnostics & Connection Tests", "Wikivoyage RAG Search", "About the Project"])

with tab_planner:
    st.markdown(
        """
        <div class="card">
            <h3>Itinerary Planner</h3>
            <p>Generate a customized, day-by-day travel plan using our autonomous agent. The agent will run OSM searches and read Wikivoyage articles to ensure all places are real and verified.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Check if API Key is set
    api_key = st.session_state.get("openai_api_key", "")
    
    if not api_key:
        st.warning("Please enter your OpenAI API key in the sidebar to use the Itinerary Planner.")
    else:
        # Initialize inputs in session state for persistence
        if "plan_dest" not in st.session_state:
            st.session_state["plan_dest"] = "Rome, Italy"
            
        # Try to pre-load from disk if available
        saved_data = load_itinerary_from_disk(st.session_state["plan_dest"])
        
        if "plan_duration" not in st.session_state:
            st.session_state["plan_duration"] = saved_data.get("duration_days", 3) if saved_data else 3
        if "plan_pace" not in st.session_state:
            st.session_state["plan_pace"] = saved_data.get("pace", "moderate") if saved_data else "moderate"
        if "plan_interests" not in st.session_state:
            st.session_state["plan_interests"] = saved_data.get("interests", ["food", "history"]) if saved_data else ["food", "history"]
        if "plan_constraints" not in st.session_state:
            st.session_state["plan_constraints"] = saved_data.get("constraints", "") if saved_data else ""
        if "plan_notes" not in st.session_state:
            st.session_state["plan_notes"] = saved_data.get("additional_notes", "") if saved_data else ""
        if "agent_result" not in st.session_state:
            st.session_state["agent_result"] = saved_data
        if "previous_itinerary" not in st.session_state:
            st.session_state["previous_itinerary"] = None

        col_plan_1, col_plan_2 = st.columns([1, 2])
        
        with col_plan_1:
            st.subheader("Trip Configuration")
            
            # Inputs linked to session state
            plan_dest = st.text_input(
                "Destination City Name", 
                value=st.session_state["plan_dest"],
                key="plan_dest_input"
            )
            st.session_state["plan_dest"] = plan_dest

            plan_duration = st.slider(
                "Trip Duration (Days)", 
                min_value=1, 
                max_value=14, 
                value=int(st.session_state["plan_duration"]),
                key="plan_duration_input"
            )
            st.session_state["plan_duration"] = plan_duration

            plan_pace = st.selectbox(
                "Travel Pace",
                options=["relaxed", "moderate", "active"],
                index=["relaxed", "moderate", "active"].index(st.session_state["plan_pace"]),
                key="plan_pace_input"
            )
            st.session_state["plan_pace"] = plan_pace

            plan_interests = st.multiselect(
                "Travel Interests",
                options=["food", "history", "art", "culture", "outdoors", "shopping", "entertainment"],
                default=st.session_state["plan_interests"],
                key="plan_interests_input"
            )
            st.session_state["plan_interests"] = plan_interests

            plan_constraints = st.text_input(
                "Constraints (Dietary / Accessibility)",
                value=st.session_state["plan_constraints"],
                placeholder="e.g. Vegetarian, wheelchair accessible",
                key="plan_constraints_input"
            )
            st.session_state["plan_constraints"] = plan_constraints

            plan_notes = st.text_area(
                "Additional Custom Requests / Style",
                value=st.session_state["plan_notes"],
                placeholder="e.g. Fine dining, slow travel, prioritize museum passes",
                key="plan_notes_input"
            )
            st.session_state["plan_notes"] = plan_notes
            
            # Trigger generation
            generate_btn = st.button("Generate Travel Itinerary", key="plan_btn")
            
            if generate_btn:
                clean_dest_input = plan_dest.strip()
                if not clean_dest_input:
                    st.error("Please enter a destination city name.")
                elif len(clean_dest_input) < 3:
                    st.error("Destination city name must be at least 3 characters long.")
                elif clean_dest_input.replace(" ", "").isdigit():
                    st.error("Destination city name cannot be numeric.")
                elif not plan_interests:
                    st.error("Please select at least one travel interest category.")
                elif api_key != "mock" and not api_key.startswith("sk-"):
                    st.error("Invalid API Key format. OpenAI API keys must start with 'sk-'.")
                else:
                    if api_key == "mock":
                        with st.spinner("Mocking agent execution..."):
                            agent_res = {
                                "itinerary": "### Day 1: Historic Rome\nMorning: Visit the Colosseum, the iconic amphitheater.\nAfternoon: Walk through the Roman Forum.\n\n### Day 2: Vatican & Dining\nMorning: Explore the Vatican Museums.\nAfternoon: Enjoy lunch at Da Enzo Al 29.",
                                "trace": [
                                    "Mocking geocoding for Rome",
                                    "Mocking POI search for Rome (history, food)",
                                    "Mocking Wikivoyage retrieval",
                                    "Compiling mock itinerary"
                                ],
                                "tool_state": {
                                    "discovered_pois": [
                                        {"poi_id": "node/1", "name": "Colosseum", "category": "history", "subtype": "attraction", "lat": 41.8902, "lon": 12.4922, "url": "https://www.openstreetmap.org/node/1"},
                                        {"poi_id": "node/2", "name": "Roman Forum", "category": "history", "subtype": "ruins", "lat": 41.8925, "lon": 12.4853, "url": "https://www.openstreetmap.org/node/2"},
                                        {"poi_id": "node/3", "name": "Vatican Museums", "category": "art", "subtype": "museum", "lat": 41.9072, "lon": 12.4539, "url": "https://www.openstreetmap.org/node/3"},
                                        {"poi_id": "node/4", "name": "Da Enzo Al 29", "category": "food", "subtype": "restaurant", "lat": 41.8881, "lon": 12.4786, "url": "https://www.openstreetmap.org/node/4"}
                                    ],
                                    "retrieved_chunks": [
                                        {"chunk_id": "wikivoyage_rome_1", "source": "Wikivoyage: Rome", "text": "Rome is the capital city of Italy...", "score": 0.8}
                                    ]
                                },
                                "verified_pois": ["Colosseum", "Roman Forum", "Vatican Museums", "Da Enzo Al 29"],
                                "unused_pois": []
                            }
                            st.session_state["agent_result"] = agent_res
                            st.session_state["previous_itinerary"] = None
                            save_itinerary_to_disk(plan_dest, agent_res)
                            st.rerun()
                    else:
                        with st.spinner("Agent running tool calls..."):
                            agent_res = run_itinerary_agent(
                                api_key=api_key,
                                destination=plan_dest,
                                interests=plan_interests,
                                duration=plan_duration,
                                pace=plan_pace,
                                constraints=plan_constraints,
                                additional_notes=plan_notes,
                                model=model_selected,
                                max_steps=2 if fast_mode_enabled else max_steps_val
                            )
                            st.session_state["agent_result"] = agent_res
                            st.session_state["previous_itinerary"] = None
                            save_itinerary_to_disk(plan_dest, agent_res)
                            st.rerun()
            
        with col_plan_2:
            st.subheader("Agent Output & Results")
            agent_res = st.session_state["agent_result"]
            
            if agent_res:
                if "error" in agent_res:
                    st.error(f"Error during agent execution: {agent_res['error']}")
                else:
                    # Display trace steps
                    with st.expander("Agent Execution Trace Log", expanded=False):
                        for trace_step in agent_res["trace"]:
                            st.write(f"- {trace_step}")
                            
                    # Display before/after comparisons if a previous version exists
                    if st.session_state.get("previous_itinerary"):
                        with st.expander("Compare with Version Before Refinement", expanded=True):
                            comp_col1, comp_col2 = st.columns(2)
                            with comp_col1:
                                st.markdown("**Previous Itinerary:**")
                                st.markdown(st.session_state["previous_itinerary"])
                            with comp_col2:
                                st.markdown("**Refined Itinerary:**")
                                st.markdown(agent_res["itinerary"])
                            
                    # Display generated itinerary
                    st.markdown("### Generated Itinerary")
                    
                    # Custom split rendering to format day blocks in cards
                    itinerary_text = agent_res["itinerary"]
                    if "### Day" in itinerary_text:
                        day_blocks = itinerary_text.split("### Day")
                        intro = day_blocks[0].strip()
                        if intro:
                            st.markdown(intro)
                        
                        for day in day_blocks[1:]:
                            st.markdown('<div class="card" style="border-left: 4px solid #4A90E2; padding: 20px; margin-bottom: 20px;">', unsafe_allow_html=True)
                            st.markdown("### Day" + day)
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(itinerary_text)
                    
                    # Interactive Map Visualization Section
                    st.markdown("---")
                    st.markdown("### Interactive Itinerary Map")
                    
                    mapped_pois = map_pois_to_days(
                        itinerary_text=itinerary_text,
                        verified_pois=agent_res["verified_pois"],
                        discovered_pois=agent_res["tool_state"]["discovered_pois"]
                    )
                    
                    if mapped_pois:
                        map_pois_df = pd.DataFrame(mapped_pois)
                        
                        map_col1, map_col2 = st.columns(2)
                        with map_col1:
                            days_available = ["Entire Trip"] + [f"Day {d}" for d in sorted(map_pois_df["day"].unique())]
                            selected_day_filter = st.selectbox(
                                "Select Day to Visualize",
                                options=days_available,
                                key="map_day_filter"
                            )
                        with map_col2:
                            selected_style = st.selectbox(
                                "Map Style Theme",
                                options=["Dark", "Light"],
                                key="map_style_theme"
                            )
                        
                        if selected_day_filter == "Entire Trip":
                            filtered_df = map_pois_df
                        else:
                            day_val = int(selected_day_filter.split(" ")[1])
                            filtered_df = map_pois_df[map_pois_df["day"] == day_val]
                        
                        layers = []
                        
                        # 1. Scatterplot Layer for markers
                        scatterplot_layer = pdk.Layer(
                            "ScatterplotLayer",
                            data=filtered_df,
                            get_position="[lon, lat]",
                            get_color="color",
                            get_radius=70,
                            pickable=True,
                            radius_scale=1.5,
                            radius_min_pixels=6,
                            radius_max_pixels=15,
                        )
                        layers.append(scatterplot_layer)
                        
                        # 2. Path Layer for connecting routes
                        path_data = []
                        if selected_day_filter == "Entire Trip":
                            for d in sorted(map_pois_df["day"].unique()):
                                day_df = map_pois_df[map_pois_df["day"] == d].sort_values("order")
                                if len(day_df) >= 2:
                                    coords = day_df[["lon", "lat"]].values.tolist()
                                    color = day_df["color"].iloc[0]
                                    path_data.append({
                                        "path": coords,
                                        "color": color
                                    })
                        else:
                            day_df = filtered_df.sort_values("order")
                            if len(day_df) >= 2:
                                coords = day_df[["lon", "lat"]].values.tolist()
                                color = day_df["color"].iloc[0]
                                path_data.append({
                                    "path": coords,
                                    "color": color
                                })
                                
                        if path_data:
                            path_layer = pdk.Layer(
                                "PathLayer",
                                data=path_data,
                                get_path="path",
                                get_color="color",
                                width_min_pixels=3,
                                pickable=True
                            )
                            layers.append(path_layer)
                            
                        # Centroid & Zoom Calculation
                        if not filtered_df.empty:
                            center_lat = filtered_df["lat"].mean()
                            center_lon = filtered_df["lon"].mean()
                            
                            lat_span = filtered_df["lat"].max() - filtered_df["lat"].min()
                            lon_span = filtered_df["lon"].max() - filtered_df["lon"].min()
                            max_span = max(lat_span, lon_span)
                            
                            if max_span < 0.005:
                                zoom_level = 15
                            elif max_span < 0.02:
                                zoom_level = 13.5
                            elif max_span < 0.06:
                                zoom_level = 12
                            elif max_span < 0.2:
                                zoom_level = 10.5
                            else:
                                zoom_level = 8.5
                        else:
                            center_lat, center_lon, zoom_level = 0.0, 0.0, 1
                            
                        map_style_value = pdk.map_styles.CARTO_DARK if selected_style == "Dark" else pdk.map_styles.CARTO_LIGHT
                        
                        view_state = pdk.ViewState(
                            latitude=center_lat,
                            longitude=center_lon,
                            zoom=zoom_level,
                            pitch=30
                        )
                        
                        r = pdk.Deck(
                            layers=layers,
                            initial_view_state=view_state,
                            map_style=map_style_value,
                            tooltip={
                                "html": "<b>{name}</b><br/>Category: {category}<br/>Day {day}, Stop {order}",
                                "style": {
                                    "backgroundColor": "#1e293b",
                                    "color": "white",
                                    "borderRadius": "8px",
                                    "padding": "8px",
                                    "border": "1px solid rgba(255,255,255,0.1)"
                                }
                            }
                        )
                        
                        st.pydeck_chart(r)
                    else:
                        st.info("No POI markers could be resolved from the final itinerary text.")
                    
                    # Display verified POIs from OSM details
                    st.markdown("---")
                    st.markdown("### Discovered Places & POI References")
                    
                    poi_boosts = get_all_poi_boosts(plan_dest)
                    
                    # Find full details of verified POIs
                    verified_details = []
                    for name in agent_res["verified_pois"]:
                        for poi in agent_res["tool_state"]["discovered_pois"]:
                            if poi["name"].lower() == name.lower() and poi not in verified_details:
                                verified_details.append(poi)
                                break
                                
                    v_col, u_col = st.columns(2)
                    
                    with v_col:
                        st.markdown("**Verified POIs (Found by tools and used):**")
                        if verified_details:
                            for p in verified_details:
                                details_url = p.get("url", f"https://www.openstreetmap.org/{p['poi_id']}")
                                net_score = poi_boosts.get(p["name"].lower(), 0.0)
                                score_str = f"{net_score:+.2f}"
                                st.markdown(
                                    f"""
                                    <div class="card" style="padding: 12px; margin-bottom: 8px;">
                                        <strong><a href="{details_url}" target="_blank" style="color: #4A90E2; text-decoration: none;">{p['name']}</a></strong><br/>
                                        <small style="color: #a0aec0;">Category: {p['category']} | Type: {p.get('subtype', 'POI')}</small><br/>
                                        <small style="color: #718096; font-weight: bold;">Feedback Score: {score_str}</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                vote_col1, vote_col2 = st.columns(2)
                                with vote_col1:
                                    if st.button("Upvote", key=f"up_v_{p['poi_id']}_{p['name'].replace(' ', '_')}"):
                                        record_poi_feedback(plan_dest, p['name'], p['poi_id'], "upvote")
                                        st.rerun()
                                with vote_col2:
                                    if st.button("Downvote", key=f"down_v_{p['poi_id']}_{p['name'].replace(' ', '_')}"):
                                        record_poi_feedback(plan_dest, p['name'], p['poi_id'], "downvote")
                                        st.rerun()
                        else:
                            st.info("No discovered POIs were directly matched in the itinerary text.")
                            
                    with u_col:
                        st.markdown("**Other Discovered POIs (Unused in final text):**")
                        unused_names = agent_res.get("unused_pois", [])
                        unused_details = [p for p in agent_res["tool_state"]["discovered_pois"] if p["name"] in unused_names]
                        
                        if unused_details:
                            for p in unused_details[:6]: # Show top 6 to keep it clean
                                details_url = p.get("url", f"https://www.openstreetmap.org/{p['poi_id']}")
                                net_score = poi_boosts.get(p["name"].lower(), 0.0)
                                score_str = f"{net_score:+.2f}"
                                st.markdown(
                                    f"""
                                    <div class="card" style="padding: 12px; margin-bottom: 8px; opacity: 0.75;">
                                        <strong><a href="{details_url}" target="_blank" style="color: #a0aec0; text-decoration: none;">{p['name']}</a></strong><br/>
                                        <small style="color: #718096;">Category: {p['category']} | Type: {p.get('subtype', 'POI')}</small><br/>
                                        <small style="color: #718096; font-weight: bold;">Feedback Score: {score_str}</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                vote_col1, vote_col2 = st.columns(2)
                                with vote_col1:
                                    if st.button("Upvote", key=f"up_u_{p['poi_id']}_{p['name'].replace(' ', '_')}"):
                                        record_poi_feedback(plan_dest, p['name'], p['poi_id'], "upvote")
                                        st.rerun()
                                with vote_col2:
                                    if st.button("Downvote", key=f"down_u_{p['poi_id']}_{p['name'].replace(' ', '_')}"):
                                        record_poi_feedback(plan_dest, p['name'], p['poi_id'], "downvote")
                                        st.rerun()
                            if len(unused_details) > 6:
                                st.caption(f"... and {len(unused_details) - 6} more discovered places")
                        else:
                            st.info("All discovered POIs were referenced in the text!")
                            
                    # Display source citations if RAG was used
                    st.markdown("---")
                    st.markdown("### Sources & Citations")
                    sources = set()
                    for chunk in agent_res["tool_state"]["retrieved_chunks"]:
                        sources.add(chunk["source"])
                    if sources:
                        for src in sorted(list(sources)):
                            st.write(f"- {src}")
                    else:
                        st.write("No external travel guide context retrieved for this itinerary.")
                        
                    # Feedback Trends & Statistics expander
                    st.markdown("---")
                    with st.expander("Feedback Trends & Statistics", expanded=False):
                        feedback_file = "data/feedback/poi_feedback.jsonl"
                        if os.path.exists(feedback_file):
                            stats = {}
                            try:
                                with open(feedback_file, "r") as f:
                                    for line in f:
                                        if not line.strip():
                                            continue
                                        event = json.loads(line)
                                        city_key = event.get("city", "").title()
                                        poi = event.get("poi_name")
                                        fb_type = event.get("feedback_type")
                                        
                                        key = (city_key, poi)
                                        if key not in stats:
                                            stats[key] = {"upvotes": 0, "downvotes": 0}
                                        
                                        if fb_type == "upvote":
                                            stats[key]["upvotes"] += 1
                                        elif fb_type == "downvote":
                                            stats[key]["downvotes"] += 1
                            except Exception as e:
                                st.error(f"Error loading stats: {e}")
                                
                            if stats:
                                stats_list = []
                                for (city_key, poi), counts in stats.items():
                                    net_score = (counts["upvotes"] * 0.25) - (counts["downvotes"] * 0.35)
                                    stats_list.append({
                                        "City": city_key,
                                        "POI Name": poi,
                                        "Upvotes": counts["upvotes"],
                                        "Downvotes": counts["downvotes"],
                                        "Net Boost Score": f"{net_score:+.2f}"
                                    })
                                    
                                stats_df = pd.DataFrame(stats_list)
                                st.dataframe(stats_df, use_container_width=True)
                            else:
                                st.info("No feedback has been recorded yet.")
                        else:
                            st.info("No feedback has been recorded yet.")
                        
                    # Add Download Button for JSON Export
                    st.markdown("---")
                    export_data = {
                        "destination": plan_dest,
                        "duration_days": plan_duration,
                        "pace": plan_pace,
                        "interests": plan_interests,
                        "constraints": plan_constraints,
                        "additional_notes": plan_notes,
                        "itinerary_text": itinerary_text,
                        "verified_pois": [
                            {
                                "poi_id": p["poi_id"],
                                "name": p["name"],
                                "category": p["category"],
                                "coordinates": {"lat": p["lat"], "lon": p["lon"]},
                                "url": p["url"]
                            } for p in verified_details
                        ],
                        "citations": sorted(list(sources))
                    }
                    
                    json_string = json.dumps(export_data, indent=2)
                    st.download_button(
                        label="Download Itinerary (JSON)",
                        data=json_string,
                        file_name=f"itinerary_{plan_dest.lower().replace(', ', '_').replace(' ', '_')}.json",
                        mime="application/json",
                        key="download_btn"
                    )
                    
                    # Refinement panel
                    st.markdown("---")
                    st.markdown("### Refine Itinerary")
                    
                    refine_col1, refine_col2 = st.columns([1, 2])
                    with refine_col1:
                        refine_scope = st.radio(
                            "Refinement Scope",
                            options=["Entire Itinerary", "Specific Day"],
                            key="refine_scope_radio"
                        )
                        
                        target_day = None
                        if refine_scope == "Specific Day":
                            days_count = int(st.session_state.get("plan_duration", 3))
                            target_day = st.selectbox(
                                "Select Day to Regenerate",
                                options=list(range(1, days_count + 1)),
                                key="refine_target_day"
                            )
                            
                    with refine_col2:
                        refine_req = st.text_input(
                            "What would you like to change?",
                            placeholder="e.g. Make it more relaxed, prioritize outdoor sights",
                            key="refine_req_input"
                        )
                        refine_btn = st.button("Apply Refinement Plan", key="refine_submit_btn")
                        
                    if refine_btn:
                        if not refine_req.strip():
                            st.error("Please enter a refinement request.")
                        else:
                            with st.spinner("Applying refinement changes..."):
                                if api_key == "mock":
                                    # Mock refinement return
                                    if refine_scope == "Specific Day" and target_day == 2:
                                        refined_itinerary = (
                                            "### Day 1: Historic Rome\nMorning: Visit the Colosseum, the iconic amphitheater.\nAfternoon: Walk through the Roman Forum.\n\n"
                                            "### Day 2: Vatican & Dining\nMorning: Explore the Vatican Museums.\nAfternoon: Enjoy a pasta tasting tour at local Trastevere taverns (featuring Cacio e Pepe and Carbonara)."
                                        )
                                    else:
                                        refined_itinerary = (
                                            "### Day 1: Historic Rome (Refined)\nMorning: Relaxed walk to the Colosseum.\nAfternoon: Roman Forum.\n\n"
                                            "### Day 2: Vatican & Dining\nMorning: Vatican Museums.\nAfternoon: Enjoy lunch at Da Enzo Al 29."
                                        )
                                        
                                    from services.agent import splice_day_itinerary
                                    
                                    refined_res = {
                                        "itinerary": refined_itinerary,
                                        "trace": agent_res["trace"] + [f"Mocked refinement for {refine_scope}"],
                                        "tool_state": agent_res["tool_state"],
                                        "verified_pois": agent_res["verified_pois"],
                                        "unused_pois": []
                                    }
                                    
                                    if refine_scope == "Specific Day" and target_day is not None:
                                        refined_res["itinerary"] = splice_day_itinerary(
                                            old_itinerary=agent_res["itinerary"],
                                            new_itinerary=refined_res["itinerary"],
                                            target_day=target_day
                                        )
                                else:
                                    from services.agent import refine_itinerary_agent
                                    
                                    refined_res = refine_itinerary_agent(
                                        api_key=api_key,
                                        current_itinerary_data=agent_res,
                                        refinement_request=refine_req,
                                        scope="day" if refine_scope == "Specific Day" else "full",
                                        target_day=target_day,
                                        model=model_selected,
                                        max_steps=2 if fast_mode_enabled else max_steps_val
                                    )
                                    
                            if "error" in refined_res:
                                st.error(f"Error during refinement: {refined_res['error']}")
                            else:
                                st.session_state["previous_itinerary"] = agent_res["itinerary"]
                                st.session_state["agent_result"] = refined_res
                                save_itinerary_to_disk(plan_dest, refined_res)
                                st.rerun()
            else:
                st.info("Enter configuration settings and click the button above to generate a verified travel itinerary.")

with tab_diag:
    st.markdown(
        """
        <div class="card">
            <h3>OpenStreetMap Geocoding & POI Test</h3>
            <p>Verify geocoding and point of interest search functionality. This section directly queries the Nominatim and Overpass API interpreter using compliant contact headers.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Geocoding and POI Settings")
        search_location = st.text_input("Enter City Name", value=st.session_state["osm_test_location"])
        
        # User interests checklist / multi-select
        interests = st.multiselect(
            "Select Interests",
            options=["food", "history", "art", "culture", "outdoors", "shopping", "entertainment"],
            default=["food", "history"]
        )
        
        search_radius = st.slider("POI Search Radius (meters)", min_value=250, max_value=5000, value=2000, step=250)
        search_limit = st.slider("Max POIs to Return", min_value=5, max_value=100, value=30, step=5)
        
        test_btn = st.button("Execute Diagnostic Test")
        
    with col2:
        st.subheader("Results")
        if test_btn:
            st.session_state["osm_test_location"] = search_location
            
            with st.spinner("Executing POI Search..."):
                pois = search_pois(
                    city_name=search_location,
                    interests=interests,
                    radius=search_radius,
                    limit=search_limit
                )
                
            if pois:
                st.success(f"Found {len(pois)} POIs in the area!")
                
                # Convert to dataframe for clean visual presentation
                df = pd.DataFrame(pois)
                
                # Render using Streamlit's LinkColumn for premium look
                st.dataframe(
                    df,
                    column_config={
                        "poi_id": st.column_config.TextColumn("ID"),
                        "name": st.column_config.TextColumn("Name"),
                        "category": st.column_config.TextColumn("Category"),
                        "lat": st.column_config.NumberColumn("Latitude"),
                        "lon": st.column_config.NumberColumn("Longitude"),
                        "url": st.column_config.LinkColumn("Details / Website URL")
                    },
                    use_container_width=True
                )
                
                # Simple Map visualization
                map_df = pd.DataFrame({
                    'lat': [p['lat'] for p in pois],
                    'lon': [p['lon'] for p in pois]
                })
                
                st.markdown("#### POI Coordinates Map Visualization")
                st.map(map_df)
            else:
                st.error("No POIs found or location geocoding failed. Please check the city name and try again.")

with tab_rag:
    st.markdown(
        """
        <div class="card">
            <h3>Wikivoyage RAG Search</h3>
            <p>Verify Wikivoyage article fetching, text cleaning, chunking, and semantic search queries using TF-IDF vector embeddings.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_rag_1, col_rag_2 = st.columns([1, 2])
    
    with col_rag_1:
        st.subheader("RAG Parameters")
        rag_destination = st.text_input("Enter Destination City Name", value="Rome")
        rag_query = st.text_input("Enter Search Query (e.g. food, history, sights)", value="local pasta dishes")
        rag_top_k = st.slider("Top Chunks (k)", min_value=1, max_value=10, value=3)
        
        run_rag_btn = st.button("Query Wikivoyage RAG")
        
    with col_rag_2:
        st.subheader("RAG Results")
        if run_rag_btn:
            with st.spinner("Fetching and processing Wikivoyage guide..."):
                index = get_rag_index(rag_destination)
                
            if index:
                st.success("Article successfully resolved and indexed!")
                st.markdown(
                    f"""
                    **Resolved Title:** `{index['title']}`  
                    **Total Chunks Created:** `{len(index['chunks'])}`
                    """
                )
                
                with st.spinner("Searching embeddings..."):
                    rag_results = search_wikivoyage(rag_destination, rag_query, top_k=rag_top_k)
                    
                if rag_results:
                    st.markdown("#### Top Matched Context Chunks")
                    for result in rag_results:
                        st.markdown(
                            f"""
                            <div class="card" style="margin-bottom: 12px; padding: 16px;">
                                <strong>Source:</strong> {result['source']} | <strong>Similarity Score:</strong> {result['score']:.4f}<br/>
                                <small style="color: #a0aec0;">ID: {result['chunk_id']}</small><br/>
                                <p style="margin-top: 8px; font-size: 0.95rem;">{result['text']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.warning("No relevant text chunks found matching your query (similarity score was 0.0 or no match). Try another query.")
            else:
                st.error("Could not fetch or parse a Wikivoyage article for this destination.")

with tab_about:
    st.markdown(
        """
        <div class="card">
            <h3>Wander AI: Intelligent Travel Companion</h3>
            <p>This capstone project is an AI-powered travel agent. It uses tool-calling agents to create personalized trip plans based on geocoded location lookups and real-time points of interest (POI) searches.</p>
            <h4>Core Architecture Overview</h4>
            <ul>
                <li><strong>Streamlit App Skeleton:</strong> A premium, reactive dashboard allowing secure API management and live diagnostic test runs.</li>
                <li><strong>Nominatim API:</strong> Validates search areas, retrieves accurate bounding boxes, and geocodes destination targets.</li>
                <li><strong>Overpass API:</strong> Pulls contextual POI categories including tourist landmarks, food, accommodations, and historic structures.</li>
                <li><strong>OpenAI GPT Agents:</strong> Combines real-time search data with LLM reasoning to produce customized itineraries.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
