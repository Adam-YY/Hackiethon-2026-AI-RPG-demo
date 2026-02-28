import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from models import Scene, Option

load_dotenv(".env.local")

from game_scripts import GAME_WORLD_SUMMARY, build_node_generation_prompt

# Fill in your own api key here folks, get it here: https://groq.com/
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_ID = "meta-llama/llama-4-maverick-17b-128e-instruct"
MAX_DECISIONS = 15

# --- Fallback Scene ---
FALLBACK_SCENE = Scene(
    id="fallback_node",
    text="The path ahead is clouded by a strange distortion in the weave of reality. You must gather your thoughts and try again.",
    is_end=False,
    options=[
        Option(id=1, text="Try to push through the distortion.", next_scene_id="current_scene"),
        Option(id=2, text="Wait for the mists to clear.", next_scene_id="current_scene")
    ]
)

def extract_json(llm_response):
    """
    Extracts JSON from the LLM response. 
    Handles cases where the model wraps JSON in markdown blocks or <output> tags.
    """
    # Try finding content in ```json ... ``` blocks
    json_block_match = re.search(r"```json\s*([\s\S]*?)\s*```", llm_response)
    if json_block_match:
        return json_block_match.group(1).strip()
    
    # Try finding content in <output> ... </output> tags
    output_tag_match = re.search(r"<output>\s*([\s\S]*?)\s*</output>", llm_response)
    if output_tag_match:
        return output_tag_match.group(1).strip()
    
    # Try finding anything that looks like a JSON object
    json_object_match = re.search(r"\{[\s\S]*\}", llm_response)
    if json_object_match:
        return json_object_match.group(0).strip()
    
    return llm_response.strip()

def build_gm_prompt(
    decision_history,
    current_stats,
    decision_number,
    last_player_action=None,
    is_first_ai_turn=False,
):
    """Build the prompt for the AI Game Master (used after Script 12)."""
    history_text = "\n".join(
        f"  {i + 1}. {entry.get('script_id', 'AI')}: {entry.get('choice', entry.get('action', '—'))}"
        for i, entry in enumerate(decision_history)
    ) or "  (none yet)"

    stats_text = (
        f"HP: {current_stats.get('HP', 100)}, "
        f"Mana: {current_stats.get('Mana', 50)}, "
        f"Gold: {current_stats.get('Gold', 10)}, "
        f"Bullets: {current_stats.get('Bullets', 10)}"
    )

    if is_first_ai_turn:
        turn_instruction = (
            "This is the first turn after the Dragon Egg scene. "
            "Continue the story based on the player's choice."
        )
        player_input = f"The player's last choice was: {last_player_action}"
    else:
        turn_instruction = (
            f"The player chose one of the previous options. Continue the story."
        )
        player_input = f"Player action: {last_player_action}"

    prompt = f"""You are the Game Master for a narrative RPG. 
You MUST return valid JSON matching the following structure:
{{
  "id": "scene_id_string",
  "text": "The narrative description of what happens next.",
  "is_end": false,
  "options": [
    {{ "id": 1, "text": "Choice 1 text", "next_scene_id": "next_id_1" }},
    {{ "id": 2, "text": "Choice 2 text", "next_scene_id": "next_id_2" }},
    {{ "id": 3, "text": "Choice 3 text", "next_scene_id": "next_id_3" }}
  ]
}}

{GAME_WORLD_SUMMARY}

## Decision history
{history_text}

## Current player stats
{stats_text}

## Decision count: {decision_number} / {MAX_DECISIONS}

Rules:
- Output ONLY the JSON object.
- If it is the end of the story, set "is_end" to true.
- Keep "text" under 100 words.
- Ensure "id" is unique.

{turn_instruction}
{player_input}
"""
    return prompt

def parse_gm_response(raw_content):
    """
    Parse the model's response into a Scene object.
    Returns a Scene object or the FALLBACK_SCENE on failure.
    """
    json_str = extract_json(raw_content)
    try:
        data = json.loads(json_str)
        
        # Validate and build Option objects
        raw_options = data.get("options", [])
        options = []
        for i, opt in enumerate(raw_options):
            if isinstance(opt, dict) and "text" in opt:
                options.append(Option(
                    id=opt.get("id", i+1),
                    text=opt["text"],
                    next_scene_id=opt.get("next_scene_id", "next_node")
                ))
        
        # Ensure we have options if not end
        if not options and not data.get("is_end"):
            options = [Option(id=1, text="Continue...", next_scene_id="next_node")]

        return Scene(
            id=data.get("id", "ai_node"),
            text=data.get("text", "The story continues..."),
            is_end=bool(data.get("is_end", False)),
            options=options
        )
        
    except (json.JSONDecodeError, KeyError, TypeError):
        return FALLBACK_SCENE

def call_ai_game_master(
    decision_history,
    current_stats,
    decision_number,
    last_player_action=None,
    is_first_ai_turn=False,
    turn_count=0,
    is_re_rail_turn=False,
    re_rail_targets=None
):
    """
    Call the AI as Game Master. Returns a Scene object.
    """
    # Use the structured node generation prompt
    prompt = build_node_generation_prompt(
        player_stats=current_stats,
        previous_action=last_player_action or "The story continues...",
        turn_count=turn_count,
        is_re_rail_turn=is_re_rail_turn,
        re_rail_targets=re_rail_targets
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
            temperature=0.7,
            max_tokens=1024,
        )
        raw = chat_completion.choices[0].message.content or "{}"
        return parse_gm_response(raw)
    except Exception as e:
        print(f"AI Error: {e}")
        return FALLBACK_SCENE

