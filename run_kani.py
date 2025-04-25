import json
import os
import asyncio
from dotenv import load_dotenv
from kani import Kani, chat_in_terminal
from kani.engines.openai import OpenAIEngine
from tools import (
    add_inventory,
    remove_inventory,
    show_inventory,
    add_credits,
    spend_credits,
    show_credits,
    buy_item,
    transfer_credits,
    show_ledger,
    roll_dice,
    start_scenario,
    log_scene,
    append_to_chat_log,
    summarize_recent_chat,
    summarize_scene_log,
)

with open("character_creation/character_classes.json") as f:
    classes_data = json.load(f)["classes"]

with open("character_creation/character_races.json") as f:
    races_data = json.load(f)["character_races"]

async def create_character() -> str:
    import re
    from tools import roll_dice

    print("\n🛠 Let's create a new character!")

    # Step 1: Get a character name
    while True:
        name = input("Enter a name for your character: ").strip()
        if name and re.match("^[a-zA-Z0-9 _-]+$", name):
            break
        print("Invalid name. Use letters, numbers, spaces, dashes, or underscores only.")

    print(f"\nWelcome, {name}!")

    # Step 2: Choose rolling method
    methods = [
        "Roll 3d6 in order for each attribute.",
        "Roll 3d6 six times and assign freely.",
        "Roll 4d6, drop the lowest die, assign freely (heroic)."
    ]
    for i, method in enumerate(methods, 1):
        print(f"{i}. {method}")
    while True:
        try:
            method_choice = int(input("Choose a rolling method (1-3): "))
            if 1 <= method_choice <= len(methods):
                break
        except ValueError:
            pass
        print("Invalid input. Please choose 1–3.")

    print(f"\nRolling attributes using method {method_choice}: {methods[method_choice - 1]}")

    ATTRS = ["Strength", "Intelligence", "Wisdom", "Constitution", "Dexterity", "Charisma"]
    rolls = []

    if method_choice == 1:
        # Roll 3d6 in order
        for attr in ATTRS:
            result = await roll_dice("3d6")
            print(f"{attr}: {result}")
            rolls.append(int(result.split("→ Total: ")[-1]))
    else:
        # Roll pools
        num_rolls = 6
        for _ in range(num_rolls):
            formula = "4d6" if method_choice == 3 else "3d6"
            result = await roll_dice(formula)
            total = int(result.split("→ Total: ")[-1])
            rolls.append(total)
        print(f"\nRolled values: {rolls}")
        print("Now assign them to attributes:")
        assigned = {}
        for attr in ATTRS:
            while True:
                try:
                    val = int(input(f"Assign to {attr}: "))
                    if val in rolls:
                        assigned[attr] = val
                        rolls.remove(val)
                        break
                    else:
                        print("That value isn't available.")
                except ValueError:
                    pass
        rolls = [assigned[attr] for attr in ATTRS]

    # Step 3: Class, race, alignment
    print("\nAvailable classes:")
    class_keys = list(classes_data.keys())

    for i, key in enumerate(class_keys, 1):
        print(f"{i}. {key.title()}: {classes_data[key]['description']}")

    while True:
        try:
            choice = int(input("\nChoose a class by number: "))
            if 1 <= choice <= len(class_keys):
                char_class_key = class_keys[choice - 1]
                break
        except ValueError:
            pass
        print("Invalid input. Please enter a valid number.")

    char_class = char_class_key.title()
    char_class_data = classes_data[char_class_key]

    print("\nAvailable races:")
    for i, race in enumerate(races_data, 1):
        print(f"{i}. {race['name']}: {race['description']}")

    # Initialize selected_race with a default value
    selected_race = None
    
    while True:
        try:
            race_choice = int(input("\nChoose a race by number: "))
            if 1 <= race_choice <= len(races_data):
                selected_race = races_data[race_choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(races_data)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    if selected_race is None:
        # Fallback to Human if something went wrong
        print("Error in race selection. Defaulting to Human race.")
        for race in races_data:
            if race["name"] == "Human":
                selected_race = race
                break
    
    char_race = selected_race["name"]

    # ✅ Create structured attributes with base values, race modifiers, and totals:
    base_attributes = dict(zip(ATTRS, rolls))
    modifiers = selected_race.get("modifiers", {}) if selected_race else {}
    structured_attributes = {}
    
    for attr in ATTRS:
        race_mod = modifiers.get(attr, 0)
        base_val = base_attributes[attr]
        total = base_val + race_mod
        structured_attributes[attr] = {
            "base": base_val,
            "race_mod": race_mod,
            "total": total
        }
        if race_mod != 0:
            print(f"🧬 {attr} modified by {race_mod} from race: {total}")

    char_alignment = input("Enter alignment (e.g., Lawful): ").strip().title()

    # Step 4: Save character JSON
    slug = name.lower().replace(" ", "_")
    char_file = f"characters/{slug}.json"
    character_data = {
    "name": name,
    "class": char_class,
    "race": char_race,
    "alignment": char_alignment,
    "attributes": structured_attributes,
    "class_description": char_class_data.get("description", "No description available"),
    "class_features": char_class_data.get("class_features", []),
    "weapon_armor_restrictions": char_class_data.get("weapon_armor_restrictions", {}),
    "xp_bonus": char_class_data.get("xp_bonus", {}),
    "race_description": selected_race.get("description", "No description available"),
    "race_special_abilities": selected_race.get("special_abilities", "None"),
    "race_movement": selected_race.get("movement", "12"),
    "race_notes": selected_race.get("notes", "No additional notes")
    }

    with open(char_file, "w") as f:
        json.dump(character_data, f, indent=2)
    print(f"\n✅ Character '{name}' created and saved to {char_file}")

    # Step 5: Initialize inventory and credits
    inventory_path = "ephemeral/inventory.json"
    try:
        with open(inventory_path, "r") as f:
            inventory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        inventory = {}
    inventory[name] = {}
    with open(inventory_path, "w") as f:
        json.dump(inventory, f, indent=2)

    credits_path = "ephemeral/credits.json"
    try:
        with open(credits_path, "r") as f:
            credits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        credits = {}
    credits[name] = 0
    with open(credits_path, "w") as f:
        json.dump(credits, f, indent=2)

    return name


async def choose_character() -> str:
    """Prompt the user to select an existing character or create a new one."""
    characters_dir = "characters"
    character_files = [
        f for f in os.listdir(characters_dir)
        if f.endswith(".json") and not f.startswith("summary_")
    ]
    character_names = [os.path.splitext(f)[0].replace("_", " ").title() for f in character_files]

    print("\n🎭 Welcome to White Star. Choose your character:\n")
    for idx, name in enumerate(character_names, 1):
        print(f"{idx}. {name}")
    print(f"{len(character_names) + 1}. Create a new character")

    while True:
        try:
            choice = int(input("\nEnter your choice: "))
            if 1 <= choice <= len(character_names):
                selected = character_names[choice - 1]
                print(f"\n✨ You selected: {selected}")
                return selected
            elif choice == len(character_names) + 1:
                return await create_character()
        except ValueError:
            pass
        print("Invalid input. Please choose a valid number.")

# Select character interactively
chosen_character = asyncio.run(choose_character())
char_slug = chosen_character.lower().replace(" ", "_")
char_path = f"characters/{char_slug}.json"

# Load character data
with open(char_path) as f:
    char_data = json.load(f)
char_class = char_data.get("class", "Unknown Class")
char_race = char_data.get("race", "Unknown Race")

# Load inventory
with open("ephemeral/inventory.json") as f:
    inventory = json.load(f)
char_inventory = inventory.get(chosen_character, {})

# Build the system prompt
system_prompt = f"""
You are the AI Game Master for a sci-fi tabletop game using the White Star ruleset.

Your current active character is {chosen_character}, a {char_race} {char_class}. Their known inventory is (item: quantity format):
{json.dumps(char_inventory, indent=2)}

You may call any of the following functions to take action:
- /add_inventory to add items
- /remove_inventory to remove items
- /show_inventory to list current gear
- /add_credits, /spend_credits, /show_credits to manage funds
- /buy_item to purchase equipment using credits
- /transfer_credits allows characters to send credits to each other.

Always use the tools if available instead of asking the user to do it manually.
Do not generate your own dice results. Use the /roll_dice function to make all rolls and include the result in your narration.
Use /start_scenario to generate a fresh adventure setup with a location, hook, and detail.
"""

# Connect to OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("No OpenAI API key found in environment. Set OPENAI_API_KEY in .env.")
engine = OpenAIEngine(api_key, model="gpt-4o")

# Create Kani with system prompt and registered tools
ai = Kani(
    engine,
    system_prompt=system_prompt,
    functions=[
        add_inventory,
        remove_inventory,
        show_inventory,
        add_credits,
        spend_credits,
        show_credits,
        buy_item,
        transfer_credits,
        show_ledger,
        roll_dice,
        start_scenario,
        log_scene,
        summarize_recent_chat,
        summarize_scene_log,
    ],
)

# Launch terminal chat
async def custom_chat_loop():
    print("USER: ", end="", flush=True)
    while True:
        try:
            user_input = input()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting chat.")
            break

        if not user_input.strip():
            continue

        append_to_chat_log(chosen_character, "user", user_input)
        reply_parts = []
        async for part in ai.full_round_str(user_input):
            reply_parts.append(part)
        reply = "".join(reply_parts)
        append_to_chat_log(chosen_character, "ai", reply)
        print(f"AI: {reply}\n")
        print("USER: ", end="", flush=True)

asyncio.run(custom_chat_loop())
