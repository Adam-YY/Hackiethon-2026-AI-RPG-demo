import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from models import Scene, Option

load_dotenv(".env.local")

from game_scripts import GAME_WORLD_SUMMARY, build_dynamic_prompt

# Fill in your own api key here folks, get it here: https://groq.com/
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_ID = "openai/gpt-oss-120b"

# --- Fallback Scene ---
FALLBACK_SCENE = Scene(
    id="fallback_node",
    text="The path ahead is clouded by a strange distortion in the weave of reality. You must gather your thoughts and try again.",
    is_end=False,
    options=[
        Option(id=1, text="Try to push through the distortion.", next_scene_id="ai_sandbox_node"),
        Option(id=2, text="Wait for the mists to clear.", next_scene_id="ai_sandbox_node")
    ]
)

def extract_json(llm_response):
    """
    Extracts JSON from the LLM response. 
    Handles cases where the model wraps JSON in markdown blocks or <output> tags.
    """
    json_block_match = re.search(r"```json\s*([\s\S]*?)\s*```", llm_response)
    if json_block_match:
        return json_block_match.group(1).strip()
    
    output_tag_match = re.search(r"<output>\s*([\s\S]*?)\s*</output>", llm_response)
    if output_tag_match:
        return output_tag_match.group(1).strip()
    
    json_object_match = re.search(r"\{[\s\S]*\}", llm_response)
    if json_object_match:
        return json_object_match.group(0).strip()
    
    return llm_response.strip()

def safe_int(value, default=0):
    """Safely convert a value to an integer, returning a default on failure."""
    try:
        if value is None:
            return default
        return int(float(value)) # Handle '10.0' or '10'
    except (ValueError, TypeError):
        return default

def parse_gm_response(raw_content):
    """
    Parse the model's response into a Scene object.
    Returns a Scene object or the FALLBACK_SCENE on failure.
    """
    json_str = extract_json(raw_content)
    try:
        data = json.loads(json_str)
        
        raw_options = data.get("options", [])
        options = []
        for i, opt in enumerate(raw_options):
            if isinstance(opt, dict) and "text" in opt:
                ns_id = str(opt.get("next_scene_id", "ai_sandbox_node"))
                # PREVENT STORY RESTART: If AI returns a script number or 'script_X', 
                # but hasn't flagged reached_target_plot, force it to stay in sandbox.
                if ns_id.isdigit() or ns_id.startswith("script_") or ns_id == "next_node":
                    if not bool(data.get("reached_target_plot", False)):
                        ns_id = "ai_sandbox_node"
                
                options.append(Option(
                    id=opt.get("id", i+1),
                    text=opt["text"],
                    next_scene_id=ns_id
                ))
        
        if not options and not data.get("is_end"):
            options = [Option(id=1, text="Continue...", next_scene_id="ai_sandbox_node")]

        # Extract stat changes with safe parsing
        raw_stats = data.get("stat_changes", {})
        stat_changes = {
            "hp": safe_int(raw_stats.get("hp")),
            "mana": safe_int(raw_stats.get("mana")),
            "bullet": safe_int(raw_stats.get("bullet")),
            "credits": safe_int(raw_stats.get("credits"))
        }

        # Generate a semi-unique ID if none provided
        import time
        node_id = data.get("id")
        if not node_id or node_id == "ai_node":
            node_id = f"dynamic_{int(time.time())}"

        return Scene(
            id=node_id,
            text=data.get("text", "The story continues..."),
            is_end=bool(data.get("is_end", False)),
            options=options,
            reached_target_plot=bool(data.get("reached_target_plot", False)),
            stat_changes=stat_changes
        )
        
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        print(f"JSON Parsing Error: {e}")
        return FALLBACK_SCENE

def call_ai_game_master(
    decision_history,
    current_stats,
    decision_number,
    last_player_action=None,
    is_first_ai_turn=False,
    turn_count=0,
    max_turns=20,
    target_scene_text=None,
    target_scene_id=None
):
    """
    Call the AI as Game Master. Returns a Scene object.
    """
    prompt = build_dynamic_prompt(
        player_stats=current_stats,
        custom_input=last_player_action or "The story continues...",
        recent_history=decision_history,
        target_scene_text=target_scene_text,
        target_scene_id=target_scene_id,
        current_turn=turn_count,
        max_turns=max_turns
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional RPG Game Master and Engine. You must respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            model=MODEL_ID,
            temperature=0.8,
            max_tokens=1024,
        )
        raw = chat_completion.choices[0].message.content or "{}"
        return parse_gm_response(raw)
    except Exception as e:
        print(f"AI Error: {e}")
        return FALLBACK_SCENE
