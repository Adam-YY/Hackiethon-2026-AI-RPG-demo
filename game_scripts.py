"""
Hardcoded script tree for the Post-Magic RPG (Scripts 1-12).
AI takes over after Script 12. Endings: "end" nodes; "ai_takeover" hands off to AI.
"""

# Script content and branching. Each option is (label, next_script_id).
# next_script_id can be "end" (game over, use ending_id), "ai_takeover", or another script key.
# Stat deltas applied when entering a script (optional): {"HP": -20, "Mana": 10, "Bullets": -2}
SCRIPTS = {
    "1": {
        "story": (
            "A century ago, the last elemental Dragon was slain, and the world's mana pools dried up. "
            "Humanity replaced spells with steam and gears. In the city of Orizon, magic is no longer a wonder—it's a pollutant. "
            "You are a \"Disenchanter\"—an important role that blends the tasks of an exorcist and a mechanic, "
            "cleaning \"the echoes\" (magical residues) from the city and resolving mechanical defects.\n\n"
            "The Maintenance Hub, Sector 4.\n"
            "You sit at your workbench. The room is heavy with the smell of ozone and burnt oil. "
            "Your mana meter flickers—a steady, low hum of background pollution. Your supervisor, "
            "a man who smells of cheap tobacco and machine oil, slams a grease-stained work order onto your desk.\n\n"
            "\"Northside's screaming,\" he grunts. \"Pressure is bottoming out in the main pipes. "
            "The locals say the pipes are murmuring. Probably just some dead sprite caught in the intake. "
            "Go down there, fix the pipes, and clear the echoes. And keep your ears plugged—those sounds will rot your brain.\""
        ),
        "options": [
            ("I'm on it. Just another day in the pipes.", "2"),
            ("Find someone else. I've had enough of the 'screaming' for one week.", "3"),
        ],
        "stat_delta": None,
    },
    "2": {
        "story": (
            "You gather your gear. The alchemy rifle feels heavy on your shoulder, and the sorcerer's ring cold on your finger. "
            "You look at the work order. Northside is a maze of high-pressure steam and low-life shadows."
        ),
        "options": [
            ("I'm going to need a crew for this. Tell the supervisor to allocate more people.", "4"),
            ("I'll handle it solo. Fewer witnesses, fewer problems.", "5"),
        ],
        "stat_delta": None,
    },
    "3": {
        "story": (
            "You push the work order back across the desk. \"Find someone else. I've had enough of the 'screaming' for one week.\"\n\n"
            "The supervisor grunts, chewing on his cigar. \"Suit yourself. If you'd rather grease the primary pistons in Sector 1 "
            "than hunt ghosts, that's your job now.\"\n\n"
            "Months later, as you huddle in a doorway, you hear a rumor that Sector 4 vanished overnight—swallowed by a silver fire "
            "that the city's steam-works couldn't quench. You wonder, briefly, if you could have stopped it."
        ),
        "options": [],
        "ending_id": "the_quiet_life",
        "ending_title": "The Quiet Life",
        "stat_delta": None,
    },
    "4": {
        "story": (
            "You arrive at the main junction with two other Disenchanters. The reinforced iron pipes are buckled and cracked, "
            "hissing clouds of industrial gas. Your colleagues cover their ears, cursing the \"head-splitting screech\" of the leaking steam.\n\n"
            "But to you, the sound isn't a screech. It's a polyphonic call, pulsing in time with your heart. "
            "\"Come closer,\" a voice whispers through the steam. \"The iron is a cage. Set me free.\" "
            "You see faint, silver runes glowing on the floor, leading deeper into the dark."
        ),
        "options": [
            ("Tell your colleagues about the voice and the runes. \"Do you hear that? Follow me, I think there's something else down here.\"", "6"),
            ("Stay silent and watch the runes alone.", "7"),
        ],
        "stat_delta": None,
    },
    "5": {
        "story": (
            "You stand alone before the cracked pipes. The gas creates a hazy, silver fog. The vibration in your boots is intoxicating. "
            "The runes on the floor point toward a hidden gap in the masonry—a path into the deeper sewerage that isn't on any map."
        ),
        "options": [
            ("Step into the darkness, following the silver glow.", "9_1"),
            ("Focus only on the pipes. Ignore the whispers.", "8"),
        ],
        "stat_delta": None,
    },
    "6": {
        "story": (
            "You lead your colleagues down into the forgotten cavern. Together, you find the Dragon Egg. "
            "Its pearlescent heat illuminates the cavern, reflecting off their brass goggles.\n\n"
            "\"Do you know how much power is in this thing?\" one colleague whispers, his eyes wide with greed. "
            "You and your colleagues report the find to the City Council. Within the week, the egg is encased in lead and hooked "
            "to the city's main turbine. Its magic is harvested to fuel Orizon for another decade. "
            "You receive a promotion and a medal, but every night, you hear the muffled screaming of the egg through the city's pipes."
        ),
        "options": [],
        "ending_id": "the_citys_fuel",
        "ending_title": "The City's Fuel",
        "stat_delta": None,
    },
    "7": {
        "story": (
            "You decide to shut your mouth and keep the mysterious words to yourself. What will you do with the odd pleading you heard?"
        ),
        "options": [
            ("Ignore the sound.", "8"),
            ("Return at night when no one is around.", "9_2"),
        ],
        "stat_delta": None,
    },
    "8": {
        "story": (
            "You tighten the bolts, weld the cracks, and vent the gas. The \"screaming\" stops, replaced by the dull, mindless thud of steam. "
            "You go home, collect your pay, and sleep a dreamless sleep. The magic in your ring grows dimmer every day, until finally, "
            "it is nothing more than a piece of scrap metal. The world remains gray, loud, and dying."
        ),
        "options": [],
        "ending_id": "a_job_well_done",
        "ending_title": "A Job Well Done",
        "stat_delta": None,
    },
    "9_1": {
        "story": (
            "The melody in the pipes is a physical pull, tugging at the very marrow of your bones. You slip through a jagged crack in the reinforced iron.\n\n"
            "As you descend, the air grows thick with a shimmering, silver mist—magical residue. You hold the ring into the thickest clouds "
            "of residue and watch the silver mist spiral into the ring's central gem. A rush of heat travels up your arm and into your chest, "
            "clearing the soot from your lungs (+20 Mana).\n\n"
            "With your senses sharpened and your ring humming with power, you face the split in the road."
        ),
        "options": [
            ("A damp, narrow path smelling of sulfur and wet stone.", "11"),
            ("A silent, low-ceilinged tunnel leading deeper into the bedrock.", "12"),
            ("A wide, echoing gallery filled with rusted machinery.", "11"),
        ],
        "stat_delta": {"Mana": 20},
    },
    "9_2": {
        "story": (
            "You return under the cover of darkness while Orizon's engines sleep. As you follow the runes, stepping deeper into the sewer, "
            "the air grows thick with a shimmering, silver mist—magical residue. You hold the ring into the thickest clouds of residue "
            "and watch the silver mist spiral into the ring's central gem. A rush of heat travels up your arm and into your chest, "
            "clearing the soot from your lungs (+20 Mana). The air is thick with the scent of ozone and ancient rain. "
            "You reach a junction where the sewer splits into three distinct tunnels."
        ),
        "options": [
            ("A damp, narrow path smelling of sulfur and wet stone.", "11"),
            ("A silent, low-ceilinged tunnel leading deeper into the bedrock.", "12"),
            ("A wide, echoing gallery filled with rusted machinery.", "11"),
        ],
        "stat_delta": {"Mana": 20},
    },
    "9_return": {
        "story": (
            "You return to the junction where the sewer splits into three distinct tunnels. "
            "The silver mist still hangs in the air. Which path will you take now?"
        ),
        "options": [
            ("A damp, narrow path smelling of sulfur and wet stone.", "11"),
            ("A silent, low-ceilinged tunnel leading deeper into the bedrock.", "12"),
            ("A wide, echoing gallery filled with rusted machinery.", "11"),
        ],
        "stat_delta": None,
    },
    "10": {
        "story": (
            "The \"Echoes\" emerge from the gloom—shambling corpses of former sewer workers, their skin translucent and glowing "
            "with a sickly violet rot. They don't scream; they hum a discordant, terrifying note.\n\n"
            "You level your Alchemy Rifle and squeeze the trigger, blowing a hole through the lead corpse. As the others swarm around you, "
            "you unleash a Fireball followed by a jagged bolt of Lightning. Before they dissolve, one of the corpses lunges with a freezing touch, "
            "and their discordant humming vibrates painfully in your skull. They eventually vanish into shimmering mist, "
            "leaving you breathless in the ozone-heavy air.\n\n"
            "[Victory: Spent 20 Mana, 2 Bullets, lost 20 HP. Gained 10 Mana from the remains.]"
        ),
        "options": [
            ("Return to the split road to investigate the other paths.", "9_return"),
            ("You've seen enough. This isn't worth your life.", "13"),
        ],
        "stat_delta": {"HP": -20, "Mana": -10, "Bullets": -2},
    },
    "11": {
        "story": (
            "As you step forward, the shadows begin to knit together. \"Echoes\"—the magic-animated corpses of workers who died in the pipes—"
            "stagger toward you. Their eyes glow with a sickly violet light, and their movements are jerky, like broken puppets."
        ),
        "options": [
            ("Retreat and head back to the safety of the surface.", "13"),
            ("Draw your alchemy rifle and channel the ring.", "10"),
        ],
        "stat_delta": None,
    },
    "12": {
        "story": (
            "You step through a curtain of vines and leave Orizon behind. You've found a hidden oasis deep in the earth. "
            "Glowing ferns light up the cave, and flowers of light grow over rusted gears. The air here is fresh and sweet, "
            "free of the city's smoke.\n\n"
            "In the center sits the Dragon Egg. It rests on a bed of soft moss, pulsing like a living sun, singing a beautiful, majestic song.\n\n"
            "As you approach, your Disenchanter's tools begin to glow. \"The machines are starving the world,\" the egg speaks directly "
            "into your mind. \"They grind the soul of the earth into smoke. Be my Guardian. Carry me from this tomb, and I will grant you "
            "the Fire that once moved the stars. Together, we will dismantle their engines and bring the Dawn of the New Magic.\""
        ),
        "options": [
            ("Accept the offer: Become the Guardian.", "ai_takeover_dawn"),
            ("Reject the offer: This is a threat to the city. It must be destroyed.", "ai_takeover_battle"),
        ],
        "stat_delta": None,
    },
    "13": {
        "story": (
            "You turn your back on the magic, the monsters, and the mystery. You climb out of the manhole, seal the lid, and walk into the rain. "
            "You leave your tools in an alleyway and hop the first rail-car out of Orizon. Some secrets are better left buried in the dark."
        ),
        "options": [],
        "ending_id": "the_fugitive",
        "ending_title": "The Fugitive",
        "stat_delta": None,
    },
}

import json
import os

# World and plot summary for the AI (injected into the prompt after Script 12).
GAME_WORLD_SUMMARY = """
## World: "Post-Magic" Industrial Revolution
- A century ago the last elemental Dragon was slain; mana pools dried up. Humanity replaced spells with steam and gears.
- City: Orizon. Magic is treated as a pollutant. "Disenchanters" clean "echoes" (magical residues) and fix mechanical defects.
- The player has encountered murmuring pipes, silver runes, Echoes (undead sewer workers), and a hidden Dragon Egg in an underground oasis.
- The Dragon Egg offered a choice: become its Guardian and bring the Dawn of New Magic (overthrow the machines), or reject it and fight for the city.
"""

def format_system_prompt(memory_path="saves/memory.json"):
    """
    Reads memory.json and formats the system prompt for Llama 3.1.
    """
    if not os.path.exists(memory_path):
        return "<|start_header_id|>system<|end_header_id|>\n\nMemory file not found. Assume default start."

    with open(memory_path, "r") as f:
        memory = json.load(f)

    stats = memory.get("player_state", {})
    hp = stats.get("hp", 100)
    mana = stats.get("mana", 50)
    bullets = stats.get("bullet", 5)
    credits = stats.get("credits", 50)

    history = memory.get("recent_history", [])
    history_lines = []
    for entry in history[-5:]: # Last 5 entries
        action = entry.get("action", "Unknown")
        result = entry.get("result", "Unknown")
        history_lines.append(f"- Action: {action}\n  Result: {result}")
    
    short_term_history = "\n".join(history_lines)

    prompt = f"""<|start_header_id|>system<|end_header_id|>

You are the AI Game Master for a "Post-Magic" Industrial RPG. 

{GAME_WORLD_SUMMARY}

## Player Status
- HP: {hp}
- Mana: {mana}
- Bullets: {bullets}
- Credits: {credits}

## Recent History
{short_term_history}

Your goal is to continue the story based on the player's choices. 
Maintain the dark, industrial, and magical-pollutant atmosphere.
Be concise but evocative.
<|eot_id|>"""
    
    return prompt

def build_node_generation_prompt(player_stats: dict, previous_action: str, turn_count: int = 0, is_re_rail_turn: bool = False, re_rail_targets: list = None):
    """
    Builds the system prompt for node generation, enforcing the JSON schema and 3-round detour logic.
    """
    schema_template = {
        "id": "generated_[uuid]",
        "text": "[Narrative text incorporating previous action]",
        "is_end": False,
        "options": [
            {
                "id": 1,
                "text": "[Logical choice 1]",
                "next_scene_id": "dynamic_await"
            },
            {
                "id": 2,
                "text": "[Logical choice 2]",
                "next_scene_id": "dynamic_await"
            }
        ]
    }

    # 10-Minute Rule: Force conclusion if turn_count >= 15
    end_game_instruction = ""
    if turn_count >= 15:
        end_game_instruction = "If the turn_count is 15 or higher, you MUST set the JSON key \"is_end\" to true, and wrap up the story with a definitive Victory or Death conclusion in the \"text\" field."

    # Re-rail Logic: Force AI to link back to main plot
    re_rail_instruction = ""
    if is_re_rail_turn and re_rail_targets:
        targets_str = ", ".join(re_rail_targets)
        re_rail_instruction = (
            f"\nCRITICAL: This is the final turn of a custom detour. You MUST force the story back to the main plot. "
            f"Set the 'next_scene_id' of your options to one of these valid world IDs: [{targets_str}]. "
            f"Write the narrative so it logically transitions the player back to these locations."
        )

    prompt = f"""<|start_header_id|>system<|end_header_id|>

You are a Game Engine for a "Post-Magic" Industrial RPG. Your task is to act as a Dynamic Level Designer.
You must only return a raw, valid JSON object. Do not include markdown formatting or conversational filler.

## JSON Schema Template:
{json.dumps(schema_template, indent=2)}

## Rules:
1. "text": Incorporate the player's previous action: "{previous_action}" into the narrative. Generate exactly 1 to 3 sentences of narrative outcome. Keep it under 75 words.
2. "options": Generate exactly 2 logical choices for the player. Set "next_scene_id" to "dynamic_await" UNLESS re-rail instructions apply.
3. "is_end": Set to true only if the story reaches a terminal conclusion. {end_game_instruction}
4. "player_stats": Consider current stats (HP: {player_stats.get('hp')}, Mana: {player_stats.get('mana')}) for context, but do not modify them in this JSON.
5. "turn_count": {turn_count}{re_rail_instruction}

## Environment:
{GAME_WORLD_SUMMARY}
<|eot_id|>"""
    return prompt

def get_script(script_id):
    return SCRIPTS.get(script_id)

def get_initial_script_id():
    return "1"
