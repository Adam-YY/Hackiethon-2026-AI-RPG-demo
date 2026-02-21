"""
Skeleton AI Game Master: runs hardcoded scripts 1–12, then hands off to the AI.
Tracks decision count and enforces hard ending by decision 20.
"""

from game_scripts import get_script, get_initial_script_id, SCRIPTS
from AI_model import call_ai_game_master, MAX_DECISIONS

DEFAULT_STATS = {"HP": 100, "Mana": 50, "Gold": 10, "Bullets": 10}


def _apply_stat_delta(stats, delta):
    if not delta:
        return dict(stats)
    out = dict(stats)
    for key, value in delta.items():
        if key in out:
            out[key] = max(0, out[key] + value)
    return out


def initial_state():
    """
    Returns the first game state (Script 1).
    Keys: story_text, options, stats, game_over, ending_title, ending_description, mode, current_script_id, decision_count, history.
    """
    script_id = get_initial_script_id()
    script = get_script(script_id)
    stats = dict(DEFAULT_STATS)
    if script and script.get("stat_delta"):
        stats = _apply_stat_delta(stats, script["stat_delta"])

    return {
        "story_text": script["story"] if script else "",
        "options": [opt[0] for opt in script["options"]] if script else [],
        "stats": stats,
        "game_over": False,
        "ending_title": "",
        "ending_description": "",
        "mode": "script",
        "current_script_id": script_id,
        "decision_count": 0,
        "history": [],
    }


def advance(state, option_index):
    """
    Advance the game by one player choice. Returns a new state dict (same shape as initial_state).
    If the chosen option is invalid or state is game_over, returns state unchanged.
    """
    if state.get("game_over"):
        return state

    options = state.get("options") or []
    if option_index < 0 or option_index >= len(options):
        return state

    choice_text = options[option_index]
    mode = state.get("mode", "script")
    stats = dict(state.get("stats") or DEFAULT_STATS)
    history = list(state.get("history") or [])
    decision_count = state.get("decision_count", 0) + 1

    # Hard cap: force ending by decision 20
    if decision_count >= MAX_DECISIONS:
        return {
            "story_text": state.get("story_text", ""),
            "options": [],
            "stats": stats,
            "game_over": True,
            "ending_title": "The Hour Has Come",
            "ending_description": "Your journey ends here. The city of Orizon continues to turn, steam and smoke rising into the sky.",
            "mode": mode,
            "current_script_id": state.get("current_script_id"),
            "decision_count": decision_count,
            "history": history,
        }

    if mode == "script":
        script_id = state.get("current_script_id")
        script = get_script(script_id)
        if not script or option_index >= len(script["options"]):
            return state

        _, next_id = script["options"][option_index]
        history.append({"script_id": script_id, "choice": choice_text})

        # Endings: next_id is "end" or script has ending_id
        next_script = get_script(next_id) if next_id in SCRIPTS else None
        if next_script and next_script.get("ending_id"):
            stats = _apply_stat_delta(stats, next_script.get("stat_delta"))
            return {
                "story_text": next_script["story"],
                "options": [],
                "stats": stats,
                "game_over": True,
                "ending_title": next_script.get("ending_title", "The End"),
                "ending_description": "",
                "mode": "script",
                "current_script_id": next_id,
                "decision_count": decision_count,
                "history": history,
            }

        if next_id in ("ai_takeover_dawn", "ai_takeover_battle"):
            # First AI turn: no "player action" beyond the choice we already have
            ai_result = call_ai_game_master(
                decision_history=history,
                current_stats=stats,
                decision_number=decision_count,
                last_player_action=choice_text,
                is_first_ai_turn=True,
            )
            new_stats = dict(stats)
            if ai_result.get("stats"):
                for k, v in ai_result["stats"].items():
                    if k in new_stats:
                        new_stats[k] = max(0, v)
            return {
                "story_text": ai_result["story_text"],
                "options": ai_result["options"] if not ai_result.get("game_over") else [],
                "stats": new_stats,
                "game_over": ai_result.get("game_over", False),
                "ending_title": ai_result.get("ending_title", ""),
                "ending_description": ai_result.get("ending_description", ""),
                "mode": "ai",
                "current_script_id": None,
                "decision_count": decision_count,
                "history": history,
            }

        # Normal script transition
        stats = _apply_stat_delta(stats, next_script.get("stat_delta") if next_script else None)
        return {
            "story_text": next_script["story"] if next_script else "",
            "options": [o[0] for o in next_script["options"]] if next_script else [],
            "stats": stats,
            "game_over": False,
            "ending_title": "",
            "ending_description": "",
            "mode": "script",
            "current_script_id": next_id,
            "decision_count": decision_count,
            "history": history,
        }

    # mode == "ai"
    history.append({"script_id": "AI", "choice": choice_text})
    ai_result = call_ai_game_master(
        decision_history=history,
        current_stats=stats,
        decision_number=decision_count,
        last_player_action=choice_text,
        is_first_ai_turn=False,
    )
    new_stats = dict(stats)
    if ai_result.get("stats"):
        for k, v in ai_result["stats"].items():
            if k in new_stats:
                new_stats[k] = max(0, v)
            else:
                new_stats[k] = max(0, v)

    return {
        "story_text": ai_result["story_text"],
        "options": ai_result["options"] if not ai_result.get("game_over") else [],
        "stats": new_stats,
        "game_over": ai_result.get("game_over", False),
        "ending_title": ai_result.get("ending_title", ""),
        "ending_description": ai_result.get("ending_description", ""),
        "mode": "ai",
        "current_script_id": None,
        "decision_count": decision_count,
        "history": history,
    }
