import requests
import logging
import streamlit as st
import re
import html
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard User-Agent header for API compliance
USER_AGENT = "TripPlannerAgentCapstone/1.0 (contact@example.com)"
HEADERS = {"User-Agent": USER_AGENT}

def resolve_wikivoyage_title(destination: str) -> str:
    """
    Queries Wikivoyage search API to resolve a destination name to the best matching page title.
    """
    url = "https://en.wikivoyage.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": destination,
        "format": "json"
    }
    
    try:
        logger.info(f"Resolving Wikivoyage page title for: '{destination}'")
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        search_results = data.get("query", {}).get("search", [])
        if search_results:
            resolved_title = search_results[0]["title"]
            logger.info(f"Resolved '{destination}' to page title: '{resolved_title}'")
            return resolved_title
            
    except requests.RequestException as e:
        logger.warning(f"Error resolving Wikivoyage title for '{destination}': {e}")
        
    # Fallback to the original user input
    return destination

def fetch_wikivoyage_html(page_title: str) -> Optional[Dict[str, Any]]:
    """
    Fetches the parsed HTML text of a Wikivoyage article.
    """
    url = "https://en.wikivoyage.org/w/api.php"
    params = {
        "action": "parse",
        "page": page_title,
        "format": "json",
        "prop": "text",
        "redirects": "true",
        "disablelimitreport": 1,
        "disableeditsection": 1
    }
    
    try:
        logger.info(f"Fetching Wikivoyage article: '{page_title}'")
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            logger.warning(f"Wikivoyage parse error for '{page_title}': {data['error'].get('info')}")
            return None
            
        parse_data = data.get("parse", {})
        return {
            "title": parse_data.get("title", page_title),
            "html": parse_data.get("text", {}).get("*", "")
        }
        
    except requests.RequestException as e:
        logger.error(f"Error fetching Wikivoyage article '{page_title}': {e}")
        return None

def clean_html(html_content: str) -> str:
    """
    Cleans raw HTML, removing script/style tags and extracting clean text.
    """
    # Remove script and style blocks
    text = re.sub(r'<(script|style)[^>]*>([\s\S]*?)<\/\1>', '', html_content)
    # Remove HTML comments
    text = re.sub(r'<!--[\s\S]*?-->', '', text)
    # Add spacing around block-level elements before stripping
    text = re.sub(r'</?(div|p|h1|h2|h3|h4|h5|h6|li|tr|td|th|table|blockquote)[^>]*>', ' ', text)
    # Remove all other tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entity references
    text = html.unescape(text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    """
    Splits text into chunks of roughly 800-1000 characters using a sliding sentence window.
    """
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_len = len(sentence)
        
        # If single sentence exceeds chunk size, add it on its own
        if sentence_len >= chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            chunks.append(sentence)
            continue
            
        # Check if adding exceeds limits
        if current_length + sentence_len + 1 > chunk_size:
            chunks.append(" ".join(current_chunk))
            
            # Backtrack to implement overlap
            overlap_chunk = []
            overlap_len = 0
            for s in reversed(current_chunk):
                if overlap_len + len(s) + 1 <= overlap:
                    overlap_chunk.insert(0, s)
                    overlap_len += len(s) + 1
                else:
                    break
            current_chunk = overlap_chunk
            current_length = overlap_len
            
        current_chunk.append(sentence)
        current_length += sentence_len + 1
        
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    # Filter out extremely short chunks (under 100 characters)
    return [c for c in chunks if len(c) > 100]

@st.cache_resource(show_spinner=False)
def get_rag_index(destination: str) -> Optional[Dict[str, Any]]:
    """
    Fetches, cleans, chunks, and vectorizes a Wikivoyage article for a destination.
    Cached as a resource because it creates scikit-learn models/matrices.
    """
    # 1. Resolve search term to standard page title
    page_title = resolve_wikivoyage_title(destination)
    
    # 2. Fetch article HTML
    article_data = fetch_wikivoyage_html(page_title)
    if not article_data or not article_data["html"]:
        logger.warning(f"No content found on Wikivoyage for '{page_title}'")
        return None
        
    # 3. Clean HTML to plain text
    plain_text = clean_html(article_data["html"])
    
    # 4. Chunk text into segments
    chunks = chunk_text(plain_text)
    if not chunks:
        logger.warning(f"Article '{page_title}' resolved to empty text chunks.")
        return None
        
    logger.info(f"Created {len(chunks)} text chunks for '{page_title}'")
    
    # 5. Fit TF-IDF Vectorizer with travel-specific stop words to reduce query noise
    custom_stops = list(TfidfVectorizer(stop_words='english').get_stop_words()) + [
        'local', 'city', 'town', 'get', 'take', 'go', 'directions', 'main', 'here', 'there',
        'place', 'places', 'tourism', 'destination', 'travel', 'way', 'route', 'bus', 'train',
        'airport', 'station', 'metro'
    ]
    vectorizer = TfidfVectorizer(stop_words=custom_stops)
    tfidf_matrix = vectorizer.fit_transform(chunks)
    
    return {
        "title": article_data["title"],
        "chunks": chunks,
        "vectorizer": vectorizer,
        "tfidf_matrix": tfidf_matrix
    }

@st.cache_data(show_spinner=False)
def search_wikivoyage(destination: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Queries the Wikivoyage index for the top-k semantically relevant chunks matching the query.
    """
    index = get_rag_index(destination)
    if not index:
        return []
        
    chunks = index["chunks"]
    vectorizer = index["vectorizer"]
    tfidf_matrix = index["tfidf_matrix"]
    title = index["title"]
    
    # Transform query to TF-IDF vector
    query_vec = vectorizer.transform([query])
    
    # Compute Cosine Similarity between query and chunks
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Get top-k indices sorted in descending order
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        score = float(similarities[idx])
        # Return matched chunks with positive similarity
        if score > 0.0:
            results.append({
                "chunk_id": f"wikivoyage_{title.replace(' ', '_').lower()}_{idx}",
                "source": f"Wikivoyage: {title}",
                "text": chunks[idx],
                "score": score
            })
            
    logger.info(f"Retrieved {len(results)} relevant chunks for query: '{query}' in '{destination}'")
    return results
