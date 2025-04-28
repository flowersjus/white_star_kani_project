import json
import os
import asyncio
import re
import random
from dotenv import load_dotenv
from kani import Kani, chat_in_terminal
from kani.engines.openai import OpenAIEngine
from character_creation.name_generator import generate_full_name, suggest_names
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
    skill_check,
    award_xp,
    show_xp,
    improve_attribute,
    show_advancement,
    help_command,
)

with open("character_creation/character_classes.json") as f:
    classes_data = json.load(f)["classes"]

with open("character_creation/character_races.json") as f:
    races_data = json.load(f)["character_races"]

async def create_character() -> str:
    import re
    from tools import roll_dice

    print("\n🛠 Let's create a new character!")

    # Step 1: Choose class
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

    # Check if Robot class was selected
    if char_class_key.lower() == "robot":
        # Automatically set race to Robot
        selected_race = None
        for race in races_data:
            if race["name"] == "Robot":
                selected_race = race
                char_race = "Robot"
                print("\nAs a Robot class character, your race is automatically set to Robot.")
                break
        
        # Fallback in case Robot race is not found (shouldn't happen)
        if selected_race is None:
            print("Error: Robot race not found. Defaulting to Human race.")
            for race in races_data:
                if race["name"] == "Human":
                    selected_race = race
                    char_race = "Human"
                    break
    else:
        # Only show race selection for non-Robot classes
        print("\nAvailable races:")
        # Filter out Robot race for non-Robot classes to avoid confusion
        available_races = [race for race in races_data if race["name"] != "Robot"]
        
        for i, race in enumerate(available_races, 1):
            print(f"{i}. {race['name']}: {race['description']}")

        # Initialize selected_race with a default value
        selected_race = None
        
        while True:
            try:
                race_choice = int(input("\nChoose a race by number: "))
                if 1 <= race_choice <= len(available_races):
                    selected_race = available_races[race_choice - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(available_races)}.")
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

    # Step 3: Now that we have class and race, handle name generation
    print("\nHow would you like to name your character?")
    print("1. Enter a name manually")
    print("2. Generate a name based on your character class")

    name_choice = input("Choose an option (1-2): ").strip()

    if name_choice == "2":
        # Generate and display name suggestions based on the already selected class
        generated_names = generate_full_name(char_class_key, count=5)
        while True:
            print("\nHere are some suggested names:")
            for idx, name in enumerate(generated_names, 1):
                print(f"{idx}. {name}")
            print(f"{len(generated_names) + 1}. Generate more names")
            print(f"{len(generated_names) + 2}. Enter a name manually")
            
            try:
                choice = int(input("\nChoose a name: "))
                if 1 <= choice <= len(generated_names):
                    name = generated_names[choice - 1]
                    break
                elif choice == len(generated_names) + 1:
                    generated_names = generate_full_name(char_class_key, count=5)
                elif choice == len(generated_names) + 2:
                    name = input("Enter a name for your character: ").strip()
                    if name and re.match("^[a-zA-Z0-9 _-]+$", name):
                        break
                    print("Invalid name. Use letters, numbers, spaces, dashes, or underscores only.")
            except ValueError:
                pass
            print("Invalid input. Please choose a valid option.")
    else:
        # Original manual name entry
        while True:
            name = input("Enter a name for your character: ").strip()
            if name and re.match("^[a-zA-Z0-9 _-]+$", name):
                break
            print("Invalid name. Use letters, numbers, spaces, dashes, or underscores only.")

    print(f"\nWelcome, {name}!")

    # Step 4: Choose rolling method
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

    # Step 5: Choose alignment
    char_alignment = input("Enter alignment (e.g., Lawful): ").strip().title()

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


    # Step 6: Save character JSON
    slug = name.lower().replace(" ", "_")
    char_file = f"characters/{slug}.json"
    
    # Load class advancement data to get initial XP threshold
    advancement_path = f"advancement/{char_class_key.lower()}_advancement.json"
    try:
        with open(advancement_path, "r") as f:
            advancement_data = json.load(f)
            next_level_xp = advancement_data[1]["xp"] if len(advancement_data) > 1 else 2000
    except (FileNotFoundError, json.JSONDecodeError):
        next_level_xp = 2000  # Default if advancement data not found
    
    # Roll for initial HP based on class hit dice
    base_hp = random.randint(1, 6)  # Default to d6
    con_mod = (structured_attributes["Constitution"]["total"] - 10) // 2
    initial_hp = max(1, base_hp + con_mod)  # Ensure minimum of 1 HP
    
    character_data = {
    "name": name,
    "class": char_class,
    "race": char_race,
    "alignment": char_alignment,
    "level": 1,
    "experience": 0,
    "hp": initial_hp,
    "max_hp": initial_hp,
    "bhb": "+0",  # Base Hit Bonus
    "st": 14,     # Default Saving Throw
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

    # Step 7: Initialize inventory and credits
    inventory_path = "ephemeral/inventory.json"
    try:
        with open(inventory_path, "r") as f:
            inventory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        inventory = {}
    inventory[name] = {}
    with open(inventory_path, "w") as f:
        json.dump(inventory, f, indent=2)

    # Roll 3d6 and multiply by 10 to determine starting credits
    print("\nRolling for starting credits (3d6 × 10)...")
    credits_roll = await roll_dice("3d6")
    credits_value = int(credits_roll.split("→ Total: ")[-1]) * 10
    print(f"Starting credits: {credits_value}")
    
    credits_path = "ephemeral/credits.json"
    try:
        with open(credits_path, "r") as f:
            credits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        credits = {}
    credits[name] = credits_value
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

async def generate_adventure_summary(character_name, scene_log_entries, engine):
    """Generate an AI-crafted narrative summary of recent adventures."""
    if not scene_log_entries:
        return "You haven't embarked on any adventures yet."
    
    # Create a prompt for the AI
    adventures_text = "\n".join([
        f"- {entry.get('title', 'Untitled')}: {entry.get('summary', 'No details available')}"
        for entry in scene_log_entries
    ])
    
    prompt = f"""
    Create a brief, engaging narrative summary of {character_name}'s recent adventures based on these scene log entries:
    
    {adventures_text}
    
    Begin your summary by clearly stating the character's current location (e.g., "Currently on Tycho-221 in the Frontier Scrapyards").
    
    Then, identify and highlight the character's current primary objective or quest based on these entries.
    
    After that, continue with the narrative summary of recent events.
    
    Write in second person perspective ("you") as if recapping for the player what their character has been doing.
    Keep the entire summary under 200 words and make it feel like the opening crawl to a sci-fi adventure.
    """
    
    # Create a temporary Kani instance for summary generation
    temp_ai = Kani(engine, system_prompt="You are a narrative summarizer.")
    
    # Get AI response
    response = ""
    async for part in temp_ai.full_round_str(prompt):
        response += part
    
    return response.strip()

def display_character_welcome(character_name, char_data, char_inventory, char_credits, adventure_summary):
    """Display a welcome message with character info, inventory, credits, and recent adventures."""
    
    # Display welcome message
    print(f"\n{'=' * 60}")
    print(f"Welcome back, {character_name}!")
    print(f"{'=' * 60}")
    
    # Display character info
    print(f"\n📊 CHARACTER INFORMATION:")
    print(f"Class: {char_data.get('class', 'Unknown')}")
    print(f"Race: {char_data.get('race', 'Unknown')}")
    print(f"Level: {char_data.get('level', 1)}")
    print(f"XP: {char_data.get('experience', 0)}")
    print(f"HP: {char_data.get('hp', 0)}/{char_data.get('max_hp', 0)}")
    
    # Display attributes if available
    if 'attributes' in char_data:
        print("\n📈 ATTRIBUTES:")
        for attr, values in char_data['attributes'].items():
            if isinstance(values, dict) and 'total' in values:
                print(f"{attr}: {values['total']}")
            else:
                print(f"{attr}: {values}")
    
    # Display special abilities if available
    if 'special_abilities' in char_data and char_data['special_abilities']:
        print("\n✨ SPECIAL ABILITIES:")
        for ability in char_data['special_abilities']:
            print(f"- {ability}")
    
    # Display long-term goals if available
    if 'goals' in char_data and char_data['goals']:
        print("\n🎯 LONG-TERM GOALS:")
        for goal in char_data['goals']:
            print(f"- {goal}")
    
    # Display inventory
    print(f"\n🎒 INVENTORY:")
    if char_inventory:
        for item, quantity in char_inventory.items():
            print(f"- {item} × {quantity}")
    else:
        print("- Empty")
    
    # Display credits
    print(f"\n💰 CREDITS: {char_credits}")
    
    # Display narrative summary of recent adventures
    print(f"\n📜 ADVENTURE RECAP:")
    print(f"{adventure_summary}")
    
    print(f"\n{'=' * 60}")
    print("Ready for your next adventure!")
    print(f"{'=' * 60}")
    
    # Add a "Ready?" prompt
    input("\nPress Enter to continue your journey...")

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

# Load credits
with open("ephemeral/credits.json") as f:
    credits = json.load(f)
char_credits = credits.get(chosen_character, 0)

# Load scene log for AI summary
scene_log_path = f"scene_log/{char_slug}.json"
recent_adventures = []
if os.path.exists(scene_log_path):
    with open(scene_log_path) as f:
        try:
            scene_log = json.load(f)
            recent_adventures = scene_log[-3:] if len(scene_log) > 0 else []
        except (json.JSONDecodeError, FileNotFoundError):
            recent_adventures = []

# Generate AI summary if there are adventures
adventure_summary = "You haven't embarked on any adventures yet."
if recent_adventures:
    # Connect to OpenAI for summary generation
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        engine_for_summary = OpenAIEngine(api_key, model="gpt-4o")
        adventure_summary = asyncio.run(generate_adventure_summary(chosen_character, recent_adventures, engine_for_summary))

# Display welcome with the AI-generated summary
display_character_welcome(chosen_character, char_data, char_inventory, char_credits, adventure_summary)

# Build the system prompt
system_prompt = f"""
You are the AI Game Master for a sci-fi tabletop game using the White Star ruleset.

Your current active character is {chosen_character}, a {char_race} {char_class}. Their known inventory is (item: quantity format):
{json.dumps(char_inventory, indent=2)}

You may call any of the following functions to take action:
- /help to see a list of all available commands or get detailed help on a specific command
- /add_inventory to add items
- /remove_inventory to remove items
- /show_inventory to list current gear
- /add_credits, /spend_credits, /show_credits to manage funds
- /buy_item to purchase equipment using credits
- /transfer_credits allows characters to send credits to each other
- /show_ledger to view transaction history
- /roll_dice to make dice rolls (always use this instead of generating your own results)
- /start_scenario to generate a fresh adventure setup with a location, hook, and detail
- /log_scene to record important scenes for future reference
- /summarize_recent_chat to get a summary of recent gameplay
- /summarize_scene_log to review all recorded scenes
- /skill_check to determine success or failure for character actions using attribute checks

Character Advancement:
- /award_xp to give experience points to a character (with optional reason)
- /show_xp to display current XP and progress to next level
- /improve_attribute to increase an attribute by 1 point (available at levels 4, 8, 12, etc.)
- /show_advancement to view the full advancement table for a character's class

Always use the tools if available instead of asking the user to do it manually.
Do not generate your own dice results. Use the /roll_dice function for all rolls and include the result in your narration.

When to use skill checks:
- Use skill checks when a character attempts something with meaningful risk or reward
- Only call for skill checks when the outcome is uncertain
- Don't use skill checks for simple, risk-free actions
- Use the appropriate attribute for the task (STR for physical force, INT for knowledge, etc.)
- Difficulty Class (DC) guidelines: Easy = 10, Average = 14, Hard = 18
- Critical success (natural 20) and critical failure (natural 1) have special outcomes

When to award XP:
- Award XP at meaningful story milestones, not after every minor event
- Typical awards: 100-500 XP for completing objectives, 50-200 XP for significant discoveries
- Always provide a reason when awarding XP
- The system will automatically check for level ups when XP is awarded
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
        skill_check,
        award_xp,
        show_xp,
        improve_attribute,
        show_advancement,
        help_command,
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
        
        # Check if the input is a /help command
        if user_input.strip().startswith("/help"):
            # Parse the command
            parts = user_input.strip().split(maxsplit=1)
            command_arg = parts[1] if len(parts) > 1 else ""  # Empty string instead of None
            
            # Call the help_command function directly
            reply = await help_command(command_arg)
        else:
            # Normal AI processing for other inputs
            reply_parts = []
            async for part in ai.full_round_str(user_input):
                reply_parts.append(part)
            reply = "".join(reply_parts)
        
        append_to_chat_log(chosen_character, "ai", reply)
        print(f"AI: {reply}\n")
        print("USER: ", end="", flush=True)

asyncio.run(custom_chat_loop())
