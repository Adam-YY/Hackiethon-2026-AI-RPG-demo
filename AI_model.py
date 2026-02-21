import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv(".env.local")

from game_scripts import GAME_WORLD_SUMMARY

# Fill in your own api key here folks, get it here: https://groq.com/
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_ID = "meta-llama/llama-4-maverick-17b-128e-instruct"
MAX_DECISIONS = 20

# --- Structured output schema for the AI Game Master ---
# The model must return valid JSON with these keys:
# - story_text: string (next part of the story)
# - options: array of exactly 3 strings (choices for the player)
# - game_over: boolean
# - ending_title: string (required if game_over is true)
# - ending_description: string (optional, if game_over is true)
# - stats: object optional { "HP", "Mana", "Gold", "Bullets" } (only include keys that changed)


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
            "The player has just chosen to either Accept the offer (Guardian / New Dawn) or Reject the offer (Battle for Orizon). "
            "Continue the story from that moment: describe what happens next and present 3 choices."
        )
        player_input = f"The player's last choice was: {last_player_action}"
    else:
        turn_instruction = (
            f"The player chose one of the previous options. Continue the story based on that choice, "
            "then present 3 new options."
        )
        player_input = f"Player action: {last_player_action}"

    prompt = f"""You are the Game Master for a narrative RPG set in a "Post-Magic" industrial world. You have full control of the story after the dragon egg scene. Be descriptive, atmospheric, and stay within the tone of the world.

{GAME_WORLD_SUMMARY}

## Decision history (choices made so far)
{history_text}

## Current player stats
{stats_text}

## Current decision number
{decision_number} of {MAX_DECISIONS}. You MUST bring the game to an end by decision {MAX_DECISIONS}. As you approach that limit, steer the story toward a satisfying conclusion. If decision_number >= {MAX_DECISIONS}, you MUST set game_over to true and provide an ending.

## Random events
You may occasionally introduce a random event (e.g. environmental hazard, encounter, discovery) to keep the story interesting. Do not overuse this.

{turn_instruction}
{player_input}

## Your response MUST be valid JSON only, no other text. Use this exact structure:
{{
  "story_text": "Your narrative here. One or more paragraphs.",
  "options": ["First choice", "Second choice", "Third choice"],
  "game_over": false,
  "ending_title": "",
  "ending_description": "",
  "stats": {{ "HP": 100, "Mana": 50, "Gold": 10, "Bullets": 10 }}
}}

Rules:
- Always output exactly 3 options unless game_over is true (then options can be empty array).
- If game_over is true, set ending_title and optionally ending_description.
- Only include "stats" if values changed (use current values above as baseline). Include all four keys in stats when you do.
- Output nothing but the JSON object."""

    return prompt


def parse_gm_response(raw_content):
    """
    Parse the model's response into a structured dict.
    Returns dict with: story_text, options, game_over, ending_title, ending_description, stats (optional).
    """
    text = raw_content.strip()
    # Try to extract JSON if the model wrapped it in markdown or extra text
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        text = json_match.group(0)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: return a safe structure so the game doesn't crash
        return {
            "story_text": raw_content[:500] if raw_content else "The story continues...",
            "options": ["Continue.", "Look around.", "Press on."],
            "game_over": False,
            "ending_title": "",
            "ending_description": "",
            "stats": None,
        }

    story_text = data.get("story_text") or "The story continues..."
    options = data.get("options")
    if not isinstance(options, list):
        options = ["Continue.", "Look around.", "Press on."]
    options = [str(o) for o in options[:3]]
    while len(options) < 3 and not data.get("game_over"):
        options.append("Continue.")

    return {
        "story_text": story_text,
        "options": options,
        "game_over": bool(data.get("game_over")),
        "ending_title": str(data.get("ending_title") or ""),
        "ending_description": str(data.get("ending_description") or ""),
        "stats": data.get("stats"),
    }


def call_ai_game_master(
    decision_history,
    current_stats,
    decision_number,
    last_player_action=None,
    is_first_ai_turn=False,
):
    """
    Call the AI as Game Master after Script 12. Returns a structured dict:
    story_text, options, game_over, ending_title, ending_description, stats (optional).
    """
    prompt = build_gm_prompt(
        decision_history=decision_history,
        current_stats=current_stats,
        decision_number=decision_number,
        last_player_action=last_player_action,
        is_first_ai_turn=is_first_ai_turn,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional RPG Game Master. You must respond with valid JSON only, no markdown or explanation.",
            },
            {"role": "user", "content": prompt},
        ],
        model=MODEL_ID,
        temperature=0.7,
        max_tokens=1024,
    )

    raw = chat_completion.choices[0].message.content or "{}"
    return parse_gm_response(raw)


def call_llama_4_gm(player_action, history=""):
    """Legacy free-form GM call (kept for compatibility)."""
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional RPG Game Master. Keep track of the story and player stats. Be descriptive and creative.",
            },
            {
                "role": "user",
                "content": f"Game History: {history}\n\nPlayer Action: {player_action}",
            },
        ],
        model=MODEL_ID,
        temperature=0.7, # Higher = more creative, lower = more consistent
        max_tokens=500,
    )
    return chat_completion.choices[0].message.content
