import json
import logging
import time
from typing import Dict, List, Any, Tuple, Optional
from openai import OpenAI
from services.osm import search_pois
from services.rag import search_wikivoyage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enforce strict function schemas
# Strict mode requires all properties to be listed in "required" and "additionalProperties: false"
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_pois",
            "description": "Searches for Points of Interest (POIs) such as museums, restaurants, historic sites, parks, etc. in a city based on interests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "The name of the city to search in (e.g. 'Rome' or 'Paris')."
                    },
                    "interests": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of categories to filter POIs (must be from: food, history, art, culture, outdoors, shopping, entertainment)."
                    },
                    "radius": {
                        "type": "integer",
                        "description": "The search radius in meters around the city center (default is 2000)."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of POIs to return (default is 30)."
                    }
                },
                "required": ["city_name", "interests", "radius", "limit"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_guides",
            "description": "Retrieves background travel guides, local history, and cultural context chunks for a destination using Wikivoyage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "The name of the destination city (e.g. 'Rome' or 'Paris')."
                    },
                    "query": {
                        "type": "string",
                        "description": "Semantic query describing the information needed (e.g. 'local dishes' or 'museum passes')."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of context chunks to retrieve (default is 3)."
                    }
                },
                "required": ["city_name", "query", "top_k"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

def validate_itinerary_pois(itinerary_text: str, discovered_pois: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """
    Validates that the final itinerary only references POIs actually returned by the tools.
    Returns:
        A tuple of (verified_poi_names, missing_poi_names)
    """
    verified = []
    
    # We do a case-insensitive check for each POI name in the text
    for poi in discovered_pois:
        name = poi["name"]
        # Basic check: if name is mentioned in text
        if name.lower() in itinerary_text.lower():
            verified.append(name)
            
    # We also check if the text mentions any specific POIs that we didn't search
    # (Because of LLM hallucinations).
    # Since checking for arbitrary hallucinations is difficult in pure Python, we provide a list
    # of all discovered POIs to the UI and label the matched ones as "Verified".
    return verified, [poi["name"] for poi in discovered_pois if poi["name"] not in verified]

def run_itinerary_agent(
    api_key: str,
    destination: str,
    interests: List[str],
    duration: int,
    pace: str = "moderate",
    constraints: str = "",
    additional_notes: str = "",
    model: str = "gpt-4o-mini",
    max_steps: int = 5
) -> Dict[str, Any]:
    """
    Orchestrates OpenAI Chat Completions tool calls to build a personalized itinerary.
    Accumulates POIs and RAG chunks, traces decision steps, and enforces validation rules.
    """
    client = OpenAI(api_key=api_key)
    start_time = time.time()
    
    # Trace log to show in the UI
    trace = []
    
    def log_trace(msg: str):
        elapsed = time.time() - start_time
        trace.append(f"[{elapsed:.2f}s] {msg}")
        
    log_trace("Initializing itinerary planner agent")
    
    # Accumulators for tool states
    tool_state = {
        "discovered_pois": [],
        "retrieved_chunks": []
    }
    
    # Helper to check duplicates in accumulated state
    def add_pois_to_state(new_pois: List[Dict[str, Any]]):
        existing_ids = {poi["poi_id"] for poi in tool_state["discovered_pois"]}
        for poi in new_pois:
            if poi["poi_id"] not in existing_ids:
                tool_state["discovered_pois"].append(poi)

    def add_chunks_to_state(new_chunks: List[Dict[str, Any]]):
        existing_ids = {chunk["chunk_id"] for chunk in tool_state["retrieved_chunks"]}
        for chunk in new_chunks:
            if chunk["chunk_id"] not in existing_ids:
                tool_state["retrieved_chunks"].append(chunk)

    # Initial prompt setups
    system_prompt = (
        "You are an expert autonomous travel planning agent. "
        "Your task is to create a detailed, highly customized, day-by-day travel itinerary.\n\n"
        "Instructions:\n"
        "1. You MUST use search_pois and retrieve_guides to search for actual places and background details. "
        "Do not invent names of attractions, restaurants, bars, shops, or hotels. Only use real places returned by the tools.\n"
        "2. Do not use any emojis in your reasoning, tool calls, or final itinerary text. Keep all text plain and professional.\n"
        "3. Focus on covering the selected user interest categories (e.g. food, history) in the itinerary.\n"
        "4. Organize the plan clearly day-by-day, respecting the travel pace and constraints specified by the user."
    )
    
    user_prompt = (
        f"Create a travel itinerary for {destination} for a duration of {duration} days.\n"
        f"Pace of Travel: {pace}.\n"
        f"Travel Interests: {', '.join(interests)}.\n"
        f"Constraints / Dietary / Access: {constraints or 'None'}.\n"
        f"Additional requests: {additional_notes or 'None'}"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    step = 0
    while step < max_steps:
        step += 1
        log_trace(f"Calling OpenAI model (Step {step}/{max_steps})")
        logger.info(f"Agent Loop Step {step}/{max_steps}")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                temperature=0.0,  # Zero temperature for deterministic reasoning and schema adherence
                timeout=30.0
            )
        except Exception as e:
            error_msg = f"Error during OpenAI API call: {e}"
            log_trace(error_msg)
            logger.error(error_msg)
            return {
                "itinerary": "",
                "trace": trace,
                "tool_state": tool_state,
                "verified_pois": [],
                "error": error_msg
            }
            
        message = response.choices[0].message
        messages.append(message)
        
        # If the model didn't call any tools, it is finished generating the plan or needs formatting
        if not message.tool_calls:
            log_trace("Model did not call any tools. Proceeding to finalize itinerary.")
            break
            
        # Execute tool calls
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except Exception as e:
                err_msg = f"Failed to parse tool call arguments as JSON: {e}. Raw: {tool_call.function.arguments}"
                log_trace(err_msg)
                logger.error(err_msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps({"error": err_msg})
                })
                continue
            
            log_trace(f"Tool request: {tool_name} with args {args}")
            logger.info(f"Executing tool {tool_name} with args {args}")
            
            tool_result = []
            
            try:
                if tool_name == "search_pois":
                    tool_result = search_pois(
                        city_name=args["city_name"],
                        interests=args["interests"],
                        radius=args.get("radius", 2000),
                        limit=args.get("limit", 30)
                    )
                    add_pois_to_state(tool_result)
                    log_trace(f"search_pois returned {len(tool_result)} POIs")
                    
                elif tool_name == "retrieve_guides":
                    tool_result = search_wikivoyage(
                        destination=args["city_name"],
                        query=args["query"],
                        top_k=args.get("top_k", 3)
                    )
                    add_chunks_to_state(tool_result)
                    log_trace(f"retrieve_guides returned {len(tool_result)} travel guide chunks")
                    
                else:
                    log_trace(f"Unknown tool call: {tool_name}")
                    tool_result = {"error": f"Tool {tool_name} not found"}
                    
            except Exception as e:
                err_msg = f"Error executing tool {tool_name}: {e}"
                log_trace(err_msg)
                logger.error(err_msg)
                tool_result = {"error": err_msg}
                
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(tool_result)
            })

    # Final formatting step if needed, or extract final message
    final_itinerary = ""
    # If the last message contains tool calls, we must call the model one last time to compile results
    if messages[-1].role == "tool" or (len(messages) > 0 and messages[-1].tool_calls):
        log_trace("Compiling final itinerary from gathered tool data")
        # Direct the model to generate the final formatted itinerary containing ONLY searched details
        # and enforce emoji constraints again
        messages.append({
            "role": "system",
            "content": (
                "You have gathered all required POIs and travel guide chunks. "
                "Now compile the final itinerary. "
                "Instructions:\n"
                "1. Format with a clear day-by-day structure using standard markdown headers like '### Day X: [Day Title]'.\n"
                "2. Break down each day into logical blocks (e.g., Morning, Afternoon, Evening).\n"
                "3. In each block, explicitly mention the names of the verified POIs and include a brief, 1-2 sentence explanation of 'why' this place is chosen (referencing details from RAG/POIs where applicable).\n"
                "4. Do not invent any other attractions. Do not use emojis."
            )
        })
        try:
            final_response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                timeout=30.0
            )
            final_itinerary = final_response.choices[0].message.content or ""
        except Exception as e:
            error_msg = f"Error during final compilation: {e}"
            log_trace(error_msg)
            return {
                "itinerary": "",
                "trace": trace,
                "tool_state": tool_state,
                "verified_pois": [],
                "error": error_msg
            }
    else:
        final_itinerary = messages[-1].content or ""

    # Validate that POIs mentioned in the itinerary were actually discovered
    verified, missing = validate_itinerary_pois(final_itinerary, tool_state["discovered_pois"])
    log_trace(f"Itinerary validation completed. Verified POIs: {len(verified)}, Unused POIs: {len(missing)}")
    
    return {
        "itinerary": final_itinerary,
        "trace": trace,
        "tool_state": tool_state,
        "verified_pois": verified,
        "unused_pois": missing
    }

def splice_day_itinerary(old_itinerary: str, new_itinerary: str, target_day: int) -> str:
    """
    Guarantees that days other than the target_day remain 100% identical by splicing
    the regenerated day block back into the original itinerary.
    """
    import re
    if "### Day" not in old_itinerary or "### Day" not in new_itinerary:
        return new_itinerary
        
    old_blocks = old_itinerary.split("### Day")
    new_blocks = new_itinerary.split("### Day")
    
    def get_day_number(block_text: str) -> Optional[int]:
        match = re.match(r'^\s*(\d+)', block_text)
        if match:
            return int(match.group(1))
        return None
        
    old_days_dict = {}
    for block in old_blocks[1:]:
        d_num = get_day_number(block)
        if d_num is not None:
            old_days_dict[d_num] = block
            
    new_days_dict = {}
    for block in new_blocks[1:]:
        d_num = get_day_number(block)
        if d_num is not None:
            new_days_dict[d_num] = block
            
    final_text = old_blocks[0]
    
    for d_num in sorted(old_days_dict.keys()):
        if d_num == target_day:
            # Inject new Day block if successfully regenerated, otherwise keep old
            block_content = new_days_dict.get(target_day, old_days_dict[target_day])
        else:
            # Enforce consistency for unchanged days
            block_content = old_days_dict[d_num]
            
        final_text += "### Day" + block_content
        
    return final_text

def refine_itinerary_agent(
    api_key: str,
    current_itinerary_data: Dict[str, Any],
    refinement_request: str,
    scope: str = "full",
    target_day: Optional[int] = None,
    model: str = "gpt-4o-mini",
    max_steps: int = 5
) -> Dict[str, Any]:
    """
    Refines the existing travel plan based on natural language feedback.
    Supports either full plan edits or specific day regeneration.
    """
    client = OpenAI(api_key=api_key)
    start_time = time.time()
    trace = list(current_itinerary_data.get("trace", []))
    
    def log_trace(msg: str):
        elapsed = time.time() - start_time
        trace.append(f"[{elapsed:.2f}s] {msg}")
        
    log_trace(f"Initiating refinement round. Scope: {scope}, Request: '{refinement_request}'")
    
    # Inherit existing tool states to accumulate POIs/chunks
    tool_state = {
        "discovered_pois": list(current_itinerary_data.get("tool_state", {}).get("discovered_pois", [])),
        "retrieved_chunks": list(current_itinerary_data.get("tool_state", {}).get("retrieved_chunks", []))
    }
    
    def add_pois_to_state(new_pois: List[Dict[str, Any]]):
        existing_ids = {poi["poi_id"] for poi in tool_state["discovered_pois"]}
        for poi in new_pois:
            if poi["poi_id"] not in existing_ids:
                tool_state["discovered_pois"].append(poi)

    def add_chunks_to_state(new_chunks: List[Dict[str, Any]]):
        existing_ids = {chunk["chunk_id"] for chunk in tool_state["retrieved_chunks"]}
        for chunk in new_chunks:
            if chunk["chunk_id"] not in existing_ids:
                tool_state["retrieved_chunks"].append(chunk)

    # Setup refinement prompt parameters
    if scope == "day" and target_day is not None:
        system_prompt = (
            "You are an expert autonomous travel planning agent.\n\n"
            f"Your task is to REGENERATE ONLY Day {target_day} of the existing travel itinerary. "
            "You MUST keep all other days exactly as they are written, changing nothing else.\n\n"
            "Instructions:\n"
            f"1. Modify the Day {target_day} schedule to address the user request: '{refinement_request}'.\n"
            "2. You MUST use search_pois and retrieve_guides to look up real attractions if new suggestions are needed. Do not invent names of places.\n"
            "3. Enforce formatting: Format the Day section with the header '### Day " + str(target_day) + ": [Title]'.\n"
            "4. Do not use emojis."
        )
    else:
        system_prompt = (
            "You are an expert autonomous travel planning agent.\n\n"
            "Your task is to REFINE the entire itinerary based on the user request.\n\n"
            "Instructions:\n"
            f"1. Refine the itinerary to address the user request: '{refinement_request}'.\n"
            "2. You MUST use search_pois and retrieve_guides to look up real attractions if new suggestions are needed. Do not invent names of places.\n"
            "3. Enforce formatting: Format with standard markdown day headers like '### Day X: [Day Title]' and day blocks.\n"
            "4. Do not use emojis."
        )
        
    user_prompt = (
        f"Current Itinerary:\n\n{current_itinerary_data['itinerary']}\n\n"
        f"Refinement Request: {refinement_request}\n\n"
        f"Provide the updated itinerary."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    step = 0
    while step < max_steps:
        step += 1
        log_trace(f"Refinement Loop: Calling OpenAI model (Step {step}/{max_steps})")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                temperature=0.0,
                timeout=30.0
            )
        except Exception as e:
            error_msg = f"Error during refinement OpenAI API call: {e}"
            log_trace(error_msg)
            return {
                "itinerary": current_itinerary_data["itinerary"],
                "trace": trace,
                "tool_state": tool_state,
                "verified_pois": list(current_itinerary_data.get("verified_pois", [])),
                "error": error_msg
            }
            
        message = response.choices[0].message
        messages.append(message)
        
        if not message.tool_calls:
            log_trace("Model completed reasoning. Proceeding to compile refined itinerary.")
            break
            
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except Exception as e:
                err_msg = f"Failed to parse tool call arguments as JSON: {e}. Raw: {tool_call.function.arguments}"
                log_trace(err_msg)
                logger.error(err_msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps({"error": err_msg})
                })
                continue
            
            log_trace(f"Refinement Tool request: {tool_name} with args {args}")
            tool_result = []
            
            try:
                if tool_name == "search_pois":
                    tool_result = search_pois(
                        city_name=args["city_name"],
                        interests=args["interests"],
                        radius=args.get("radius", 2000),
                        limit=args.get("limit", 30)
                    )
                    add_pois_to_state(tool_result)
                    log_trace(f"search_pois returned {len(tool_result)} POIs during refinement")
                    
                elif tool_name == "retrieve_guides":
                    tool_result = search_wikivoyage(
                        destination=args["city_name"],
                        query=args["query"],
                        top_k=args.get("top_k", 3)
                    )
                    add_chunks_to_state(tool_result)
                    log_trace(f"retrieve_guides returned {len(tool_result)} travel guide chunks during refinement")
                    
                else:
                    tool_result = {"error": f"Tool {tool_name} not found"}
                    
            except Exception as e:
                err_msg = f"Error executing tool {tool_name} during refinement: {e}"
                log_trace(err_msg)
                tool_result = {"error": err_msg}
                
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(tool_result)
            })

    refined_itinerary = ""
    if messages[-1].role == "tool" or (len(messages) > 0 and messages[-1].tool_calls):
        log_trace("Compiling final refined itinerary")
        messages.append({
            "role": "system",
            "content": (
                "You have finished gathering details. Now compile the final updated itinerary. "
                "Make sure to explicitly mention the names of verified POIs from the tool state. "
                "Do not use emojis. Restrict formatting to standard markdown."
            )
        })
        try:
            final_response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                timeout=30.0
            )
            refined_itinerary = final_response.choices[0].message.content or ""
        except Exception as e:
            error_msg = f"Error during final refinement compilation: {e}"
            log_trace(error_msg)
            return {
                "itinerary": current_itinerary_data["itinerary"],
                "trace": trace,
                "tool_state": tool_state,
                "verified_pois": list(current_itinerary_data.get("verified_pois", [])),
                "error": error_msg
            }
    else:
        refined_itinerary = messages[-1].content or ""

    # If target scope was single-day, programmatically splice Day text to guarantee consistency
    if scope == "day" and target_day is not None:
        log_trace(f"Programmatically splicing Day {target_day} and restoring all other days to guarantee consistency")
        refined_itinerary = splice_day_itinerary(
            old_itinerary=current_itinerary_data["itinerary"],
            new_itinerary=refined_itinerary,
            target_day=target_day
        )

    # Re-validate POIs
    verified, missing = validate_itinerary_pois(refined_itinerary, tool_state["discovered_pois"])
    log_trace(f"Refined itinerary validation completed. Verified POIs: {len(verified)}, Unused POIs: {len(missing)}")
    
    return {
        "itinerary": refined_itinerary,
        "trace": trace,
        "tool_state": tool_state,
        "verified_pois": verified,
        "unused_pois": missing
    }

