import json
import random
import re
import os
import math
import inspect
import sys
from kani.ai_function import AIFunction, ai_function
from datetime import datetime

# Configuration
NUM_RECENT_USER_MESSAGES = 10  # Change this value to adjust the summary range
SCENE_LOG_PATH = "ephemeral/scene_log.json"
XP_LOG_PATH = "ephemeral/xp_log.json"

def log_transaction(entry: dict):
    """Append a transaction entry to ledger.json with a timestamp."""
    LEDGER_PATH = "ephemeral/ledger.json"

    # Ensure timestamp exists
    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"

    try:
        with open(LEDGER_PATH, "r") as f:
            ledger = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        ledger = []

    ledger.append(entry)

    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)

async def roll_dice(dice: str) -> str:
    """Roll dice using standard RPG notation (e.g., 1d6, 2d10+3, 1d100-2)."""
    pattern = r"(?P<num>\d*)d(?P<die>\d+)(?P<mod>[+-]\d+)?"
    match = re.fullmatch(pattern, dice.replace(" ", ""))
    if not match:
        return "Invalid format. Use notation like 2d6, 1d20+4, or 3d8-2."

    num = int(match.group("num") or 1)
    die = int(match.group("die"))
    mod = int(match.group("mod") or 0)

    if die not in {4, 6, 8, 10, 12, 20, 100}:
        return f"d{die} is not a valid die type in White Star."

    rolls = [random.randint(1, die) for _ in range(num)]
    total = sum(rolls) + mod
    mod_str = f" {mod:+}" if mod else ""
    return f"🎲 Rolling {dice}: {rolls}{mod_str} → Total: {total}"

async def add_inventory(character: str, item: str, quantity: int = 1) -> str:
    """Add an item and quantity to a character's inventory."""
    INVENTORY_PATH = "ephemeral/inventory.json"

    try:
        with open(INVENTORY_PATH, "r") as f:
            inventory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        inventory = {}

    # Convert legacy list format to dict
    if isinstance(inventory[character], list):
        inventory[character] = {item: 1 for item in inventory[character]}

    if character not in inventory:
        inventory[character] = {}

    character_inventory = inventory[character]

    if item in character_inventory:
        character_inventory[item] += quantity
    else:
        character_inventory[item] = quantity

    with open(INVENTORY_PATH, "w") as f:
        json.dump(inventory, f, indent=2)

    return f"Added {quantity} × {item} to {character}'s inventory."

async def remove_inventory(character: str, item: str, quantity: int = 1) -> str:
    """Remove a quantity of an item from a character's inventory."""
    INVENTORY_PATH = "ephemeral/inventory.json"

    try:
        with open(INVENTORY_PATH, "r") as f:
            inventory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not access inventory data."

    # Convert legacy list format to dict
    if isinstance(inventory[character], list):
        inventory[character] = {item: 1 for item in inventory[character]}

    if character not in inventory:
        return f"No inventory found for {character}."

    character_inventory = inventory[character]

    if item not in character_inventory:
        return f"{item} not found in {character}'s inventory."

    if character_inventory[item] < quantity:
        return f"{character} only has {character_inventory[item]} × {item}."

    character_inventory[item] -= quantity

    if character_inventory[item] <= 0:
        del character_inventory[item]

    with open(INVENTORY_PATH, "w") as f:
        json.dump(inventory, f, indent=2)

    return f"Removed {quantity} × {item} from {character}'s inventory."

async def show_inventory(character: str = "Jax Varn") -> str:
    """Show the full inventory for a character. Defaults to Jax Varn if no name is given."""
    INVENTORY_PATH = "ephemeral/inventory.json"

    try:
        with open(INVENTORY_PATH, "r") as f:
            inventory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not access inventory data."

    if character not in inventory:
        return f"No inventory found for {character}."

    character_inventory = inventory[character]

    if not character_inventory:
        return f"{character} has no items in their inventory."

    lines = [f"**{character}'s Inventory:**"]
    for item, quantity in character_inventory.items():
        lines.append(f"- {item} × {quantity}")

    return "\n".join(lines)

async def add_credits(character: str, amount: int) -> str:
    """Add credits to a character's balance."""
    CREDITS_PATH = "ephemeral/credits.json"

    try:
        with open(CREDITS_PATH, "r") as f:
            credits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        credits = {}

    credits[character] = credits.get(character, 0) + amount

    with open(CREDITS_PATH, "w") as f:
        json.dump(credits, f, indent=2)

    # 🧾 Log it here — AFTER writing the file
    log_transaction({
    "type": "add",
    "character": character,
    "amount": amount,
    "source": "manual"
    })

    return f"{character} now has {credits[character]} credits."
    
async def spend_credits(character: str, amount: int) -> str:
    """Spend credits from a character's balance."""
    CREDITS_PATH = "ephemeral/credits.json"

    try:
        with open(CREDITS_PATH, "r") as f:
            credits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        credits = {}

    current = credits.get(character, 0)
    if amount > current:
        return f"{character} only has {current} credits. Transaction declined."

    credits[character] -= amount

    with open(CREDITS_PATH, "w") as f:
        json.dump(credits, f, indent=2)

    # 🧾 Log it here — AFTER writing the file
    log_transaction({
    "type": "spend",
    "character": character,
    "amount": amount,
    "purpose": "manual spend"
    })

    return f"{character} now has {credits[character]} credits."

async def show_credits(character: str = "Jax Varn") -> str:
    """Show how many credits a character currently has."""
    CREDITS_PATH = "ephemeral/credits.json"

    try:
        with open(CREDITS_PATH, "r") as f:
            credits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not access credit records."

    amount = credits.get(character, 0)
    return f"{character} has {amount} credits."

async def buy_item(character: str, item: str, quantity: int = 1) -> str:
    """Buy one or more of an item if the character has enough credits."""
    CREDITS_PATH = "ephemeral/credits.json"
    INVENTORY_PATH = "ephemeral/inventory.json"

    # Load credits
    try:
        with open(CREDITS_PATH, "r") as f:
            credits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        credits = {}

    char_credits = credits.get(character, 0)

    # Search for item using fuzzy matching
    import os
    import difflib

    equipment_path = "equipment"
    best_match = None
    best_ratio = 0.0

    for file in os.listdir(equipment_path):
        if file.endswith(".json"):
            with open(os.path.join(equipment_path, file)) as f:
                data = json.load(f)
                for category in data.values():
                    for entry in category:
                        entry_name = entry["name"]
                        ratio = difflib.SequenceMatcher(None, entry_name.lower(), item.lower()).ratio()
                        if ratio > best_ratio:
                            best_match = entry
                            best_ratio = ratio

    item_data = best_match
    item_cost = best_match.get("cost", None) if best_match else None

    if not item_data or best_ratio < 0.6:
        return f"Item '{item}' not found. Closest match was too different: '{best_match['name']}'"

    total_cost = item_cost * quantity
    if char_credits < total_cost:
        return f"{character} has {char_credits} credits but needs {total_cost} to buy {quantity} × '{item_data['name']}'."

    # Deduct credits
    credits[character] -= total_cost
    with open(CREDITS_PATH, "w") as f:
        json.dump(credits, f, indent=2)

    # Load and update inventory
    try:
        with open(INVENTORY_PATH, "r") as f:
            inventory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        inventory = {}

    if character in inventory and isinstance(inventory[character], list):
        inventory[character] = {i: 1 for i in inventory[character]}

    if character not in inventory:
        inventory[character] = {}

    inventory[character][item_data['name']] = inventory[character].get(item_data['name'], 0) + quantity

    with open(INVENTORY_PATH, "w") as f:
        json.dump(inventory, f, indent=2)

    # 🧾 Log it here — AFTER writing the file
    log_transaction({
    "type": "purchase",
    "character": character,
    "item": item_data['name'],
    "quantity": quantity,
    "total_cost": total_cost
    })

    return f"{character} bought {quantity} × '{item_data['name']}' for {total_cost} credits. Remaining balance: {credits[character]} credits."

async def transfer_credits(sender: str, receiver: str, amount: int) -> str:
    """Transfer credits from one character to another."""
    CREDITS_PATH = "ephemeral/credits.json"

    try:
        with open(CREDITS_PATH, "r") as f:
            credits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        credits = {}

    sender_balance = credits.get(sender, 0)

    if sender_balance < amount:
        return f"{sender} only has {sender_balance} credits. Transfer of {amount} credits failed."

    credits[sender] -= amount
    credits[receiver] = credits.get(receiver, 0) + amount

    with open(CREDITS_PATH, "w") as f:
        json.dump(credits, f, indent=2)

    # 🧾 Log it here — AFTER writing the file
    log_transaction({
    "type": "transfer",
    "from": sender,
    "to": receiver,
    "amount": amount
    })

    return f"{sender} transferred {amount} credits to {receiver}. New balances: {sender} = {credits[sender]}, {receiver} = {credits[receiver]}"

async def show_ledger(character: str = "Jax Varn") -> str:
    """Display a brief summary of transactions involving the character."""
    LEDGER_PATH = "ephemeral/ledger.json"

    try:
        with open(LEDGER_PATH, "r") as f:
            ledger = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "No transaction history found."

    relevant = [
        entry for entry in ledger
        if entry.get("character") == character or entry.get("from") == character or entry.get("to") == character
    ]

    if not relevant:
        return f"No transactions found for {character}."

    lines = [f"**Transaction history for {character}:**"]
    for entry in relevant[-10:]:  # last 10
        lines.append(f"- [{entry['timestamp']}] {entry['type'].title()} - {entry}")

    return "\n".join(lines)

@ai_function()
async def start_scenario() -> str:
    """Generate a basic adventure scenario with a brief recap of recent events."""

    # Attempt to include scene recap
    SCENE_LOG_PATH = "ephemeral/scene_log.json"
    recap = ""
    try:
        if os.path.exists(SCENE_LOG_PATH):
            with open(SCENE_LOG_PATH, "r") as f:
                logs = json.load(f)
                if logs:
                    recent = logs[-3:]  # Get last 3 scenes
                    bullet_points = [f"- {entry['summary']}" for entry in recent if entry.get("summary")]
                    if bullet_points:
                        recap = "📖 **Previously on Jax Varn’s journey:**\n" + "\n".join(bullet_points) + "\n\n"
    except Exception as e:
        recap = ""  # Fallback to no recap if something goes wrong

    # Scenario generation
    locations = [
        "Tycho-221, a rusting mining station orbiting a dead moon",
        "Krellar’s Drift, a smuggler outpost on the edge of lawful space",
        "The Verdant Wreck, a crashed science vessel overtaken by vegetation",
        "Bastion Core, a half-functional AI-run defense platform",
        "Drifter's Coil, a rotating casino/fuel depot hybrid"
    ]

    situations = [
        "a mysterious signal has been broadcasting a looping distress call",
        "someone has stolen a vital piece of your ship's hardware",
        "a shady deal is about to go wrong — and you're caught in the middle",
        "you wake up with no memory of how you arrived here",
        "you're hunting a bounty that may not be what it seems"
    ]

    # Generate a random contact name if needed
    contact_names = ["Whisper", "Echo", "Cipher", "Shadow", "Pulse", "Flare", "Vortex", "Nexus", "Specter", "Mirage"]
    contact_name = random.choice(contact_names)
    
    npc_or_detail = [
        "A woman with mirrored eyes is watching you from a distance",
        f"Your enigmatic contact, known only as '{contact_name},' is delayed—perhaps intentionally",
        "The power keeps flickering every 20 seconds — like clockwork",
        "A child's voice keeps playing over the station intercom, though no children are registered on board",
        "Everyone here seems to know your name — and not in a good way"
    ]

    scenario = f"""
🪐 **SCENARIO START**

**Location:** {random.choice(locations)}
**Situation:** {random.choice(situations)}
**Detail:** {random.choice(npc_or_detail)}
""".strip()

    return recap + scenario


async def log_scene(character: str, title: str, summary: str) -> str:
    """Logs a summarized scene entry for the specified character."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "title": title,
        "summary": summary
    }

    try:
        if os.path.exists(SCENE_LOG_PATH):
            with open(SCENE_LOG_PATH, "r") as f:
                content = f.read().strip()
                data = json.loads(content) if content else []
        else:
            data = []

        data.append(log_entry)

        with open(SCENE_LOG_PATH, "w") as f:
            json.dump(data, f, indent=2)

        return f'The scene "{title}" has been logged for {character}. {summary}'
    except Exception as e:
        return f"Failed to log scene: {e}"

async def summarize_recent_chat(character: str) -> str:
    """
    Summarize the last N user/AI message pairs for the specified character.
    """
    log_path = f"chat_log/{character.lower().replace(' ', '_')}.jsonl"
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return f"No chat log found for {character}."

    # Parse and reverse for recent-first
    messages = [json.loads(line) for line in lines][::-1]

    user_msg_count = 0
    summary_block = []
    for msg in messages:
        summary_block.insert(0, msg)
        if msg["role"] == "user":
            user_msg_count += 1
        if user_msg_count >= NUM_RECENT_USER_MESSAGES:
            break

    if not summary_block:
        return "Not enough recent chat data to summarize."

    # Convert to text transcript
    transcript = ""
    for msg in summary_block:
        prefix = "You" if msg["role"] == "user" else "GM"
        transcript += f"{prefix}: {msg['message']}\n"

    # Call the LLM to summarize
    return (
        "Summarize this recent gameplay log into a short paragraph:\n\n"
        + transcript
    )

CHAT_LOG_DIR = "chat_log"

def append_to_chat_log(character: str, role: str, message: str):
    os.makedirs(CHAT_LOG_DIR, exist_ok=True)
    log_path = os.path.join(CHAT_LOG_DIR, f"{character.replace(' ', '_').lower()}.jsonl")

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "role": role,
        "message": message.strip()
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

async def summarize_scene_log_function(character: str) -> str:
    """Summarize the full scene log for a given character."""
    if not os.path.exists(SCENE_LOG_PATH):
        return f"No scene log exists for {character}."

    with open(SCENE_LOG_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return "Scene log could not be read."

    if not data:
        return f"There are no logged scenes for {character}."

    # Optional: filter by character if needed
    summaries = [entry["summary"] for entry in data]
    combined = "\n".join(f"- {summary}" for summary in summaries)
    return f"Here is a summary of all scenes involving {character}:\n\n{combined}"

import os

async def choose_character() -> str:
    """Prompt the user to select a character from existing files or create a new one."""
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
                return "__NEW__"
        except ValueError:
            pass
        print("Invalid input. Please choose a valid number.")

async def skill_check(character: str, attribute: str, difficulty: int = 14, description: str = None) -> str:
    """
    Perform a skill check using the specified attribute against a difficulty class.
    
    Args:
        character: The character's name
        attribute: The attribute to use (strength, intelligence, wisdom, constitution, dexterity, charisma)
        difficulty: The difficulty class (DC) to beat (default: 14 - Average)
        description: Optional description of what the character is attempting
    
    Returns:
        A formatted string with the result of the skill check
    """
    # Load character data to get attribute value
    char_slug = character.lower().replace(" ", "_")
    char_path = f"characters/{char_slug}.json"
    
    try:
        with open(char_path, "r") as f:
            char_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find character data for {character}."
    
    # Get the attribute value
    attribute = attribute.lower()
    valid_attrs = ["strength", "intelligence", "wisdom", "constitution", "dexterity", "charisma"]
    if attribute not in valid_attrs:
        return f"Invalid attribute: {attribute}. Must be one of: strength, intelligence, wisdom, constitution, dexterity, charisma."
    
    # Get the total attribute value (including racial modifiers)
    # Handle case-insensitive attribute lookup
    attr_key = next((key for key in char_data["attributes"] if key.lower() == attribute), None)
    if not attr_key:
        return f"Attribute {attribute} not found in character data."
    
    attr_value = char_data["attributes"][attr_key]["total"]
    
    # Calculate modifier
    modifier = (attr_value - 10) // 2
    
    # Roll the die
    roll = random.randint(1, 20)
    total = roll + modifier
    
    # Determine outcome
    if roll == 1:
        result = "critical_failure"
        outcome = "❌ Critical Failure!"
    elif roll == 20:
        result = "critical_success"
        outcome = "✅ Critical Success!"
    elif total >= difficulty:
        result = "success"
        outcome = "✅ Success!"
    else:
        result = "failure"
        outcome = "❌ Failure!"
    
    # Format the output
    action_desc = f" attempting to {description}" if description else ""
    return f"🎲 Skill Check: {character}{action_desc} using {attribute.title()}\nRolled {roll} + Modifier {modifier} = {total} (Needs {difficulty})\n{outcome}"

async def award_xp(character: str, amount: int, reason: str = None) -> str:
    """
    Award XP to a character and check for level up.
    
    Args:
        character: The character's name
        amount: The amount of XP to award
        reason: Optional reason for the XP award
    
    Returns:
        A formatted string with the result of the XP award
    """
    # Load character data
    char_slug = character.lower().replace(" ", "_")
    char_path = f"characters/{char_slug}.json"
    
    try:
        with open(char_path, "r") as f:
            char_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find character data for {character}."
    
    # Initialize XP fields if they don't exist
    if "experience" not in char_data:
        char_data["experience"] = 0
    if "level" not in char_data:
        char_data["level"] = 1
    
    # Get character class for advancement table
    char_class = char_data.get("class", "Unknown")
    
    # Load class advancement data
    advancement_path = f"advancement/{char_class.lower()}_advancement.json"
    try:
        with open(advancement_path, "r") as f:
            advancement_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find advancement data for {char_class}."
    
    # Calculate XP bonus if applicable
    xp_bonus = 0
    if "xp_bonus" in char_data:
        bonus_attr = char_data["xp_bonus"].get("attribute", "").lower()
        if bonus_attr:
            # Find the attribute in the character data
            attr_key = next((key for key in char_data["attributes"] if key.lower() == bonus_attr), None)
            if attr_key:
                attr_value = char_data["attributes"][attr_key]["total"]
                # Check thresholds for bonus
                thresholds = char_data["xp_bonus"].get("thresholds", {})
                for threshold, bonus_percent in thresholds.items():
                    min_val, max_val = map(int, threshold.split("-")) if "-" in threshold else (int(threshold.replace("+", "")), 100)
                    if min_val <= attr_value <= max_val:
                        bonus_percent_value = int(bonus_percent.replace("%", ""))
                        xp_bonus = math.floor(amount * (bonus_percent_value / 100))
                        break
    
    # Add XP to character
    old_xp = char_data["experience"]
    char_data["experience"] += amount + xp_bonus
    
    # Check if level up is needed
    level_up_occurred = False
    level_up_message = ""
    
    # Find the next level threshold
    current_level = char_data["level"]
    next_level_data = next((level for level in advancement_data if level["level"] > current_level), None)
    
    if next_level_data and char_data["experience"] >= next_level_data["xp"]:
        # Level up
        level_up_result = await level_up(character)
        level_up_occurred = True
        level_up_message = f"\n\n{level_up_result}"
    
    # Save character data
    with open(char_path, "w") as f:
        json.dump(char_data, f, indent=2)
    
    # Log XP award
    log_xp_award(character, amount, xp_bonus, reason)
    
    # Format the output
    reason_text = f" for {reason}" if reason else ""
    bonus_text = f" (+{xp_bonus} bonus)" if xp_bonus > 0 else ""
    
    return f"🌟 {character} gained {amount} XP{bonus_text}{reason_text}! Total XP: {char_data['experience']}{level_up_message}"

def log_xp_award(character: str, amount: int, bonus: int = 0, reason: str = None):
    """Log an XP award to the XP log file."""
    try:
        with open(XP_LOG_PATH, "r") as f:
            xp_log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        xp_log = []
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "character": character,
        "amount": amount,
        "bonus": bonus,
        "reason": reason or "Not specified"
    }
    
    xp_log.append(entry)
    
    os.makedirs(os.path.dirname(XP_LOG_PATH), exist_ok=True)
    with open(XP_LOG_PATH, "w") as f:
        json.dump(xp_log, f, indent=2)

async def level_up(character: str) -> str:
    """
    Handle the level up process for a character.
    
    Args:
        character: The character's name
    
    Returns:
        A formatted string with the result of the level up
    """
    # Load character data
    char_slug = character.lower().replace(" ", "_")
    char_path = f"characters/{char_slug}.json"
    
    try:
        with open(char_path, "r") as f:
            char_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find character data for {character}."
    
    # Get character class for advancement table
    char_class = char_data.get("class", "Unknown")
    
    # Load class advancement data
    advancement_path = f"advancement/{char_class.lower()}_advancement.json"
    try:
        with open(advancement_path, "r") as f:
            advancement_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find advancement data for {char_class}."
    
    # Get current level and find next level data
    current_level = char_data.get("level", 1)
    next_level = current_level + 1
    
    next_level_data = next((level for level in advancement_data if level["level"] == next_level), None)
    if not next_level_data:
        return f"No advancement data found for {char_class} level {next_level}."
    
    # Update level
    char_data["level"] = next_level
    
    # Update base hit bonus (bhb) and saving throw (st)
    char_data["bhb"] = next_level_data["bhb"]
    char_data["st"] = next_level_data["st"]
    
    # Roll for HP increase
    hd = next_level_data["hd"]
    hp_roll_result = await roll_hp(hd, char_data)
    hp_increase = int(hp_roll_result.split("→ HP increase: ")[-1].split(" ")[0])
    
    # Update HP
    if "hp" not in char_data:
        char_data["hp"] = hp_increase
    else:
        char_data["hp"] += hp_increase
    
    if "max_hp" not in char_data:
        char_data["max_hp"] = hp_increase
    else:
        char_data["max_hp"] += hp_increase
    
    # Check for attribute improvement (every 4 levels)
    attr_improvement_message = ""
    if next_level % 4 == 0:
        attr_improvement_message = "\n\n🔼 You can now improve one attribute by 1 point. Use /improve_attribute to select which attribute to improve."
    
    # Save character data
    with open(char_path, "w") as f:
        json.dump(char_data, f, indent=2)
    
    # Format the output
    return f"🎉 {character} has reached level {next_level}!\n\n{hp_roll_result}\n\nBase Hit Bonus: {char_data['bhb']}\nSaving Throw: {char_data['st']}{attr_improvement_message}"

async def roll_hp(hd: str, char_data: dict) -> str:
    """
    Roll for HP increase based on hit dice and Constitution modifier.
    
    Args:
        hd: The hit dice string (e.g., "1+1", "2", "3+2")
        char_data: The character data dictionary
    
    Returns:
        A formatted string with the result of the HP roll
    """
    # Parse hit dice
    match = re.match(r"(\d+)(?:\+(\d+))?", hd)
    if not match:
        return f"Invalid hit dice format: {hd}"
    
    base_dice = int(match.group(1))
    bonus = int(match.group(2) or 0)
    
    # Get Constitution modifier
    con_key = next((key for key in char_data["attributes"] if key.lower() == "constitution"), None)
    con_mod = 0
    if con_key:
        con_value = char_data["attributes"][con_key]["total"]
        con_mod = (con_value - 10) // 2
    
    # Roll for HP (1d6 per hit dice)
    rolls = [random.randint(1, 6) for _ in range(base_dice)]
    hp_increase = sum(rolls) + bonus + con_mod
    
    # Ensure minimum of 1 HP per level
    hp_increase = max(1, hp_increase)
    
    # Format the output
    con_mod_str = f" {con_mod:+}" if con_mod != 0 else ""
    bonus_str = f" {bonus:+}" if bonus != 0 else ""
    
    return f"🎲 Rolling for HP: {rolls}{bonus_str}{con_mod_str} → HP increase: {hp_increase}"

async def show_xp(character: str) -> str:
    """
    Show current XP and progress to next level.
    
    Args:
        character: The character's name
    
    Returns:
        A formatted string with the character's XP information
    """
    # Load character data
    char_slug = character.lower().replace(" ", "_")
    char_path = f"characters/{char_slug}.json"
    
    try:
        with open(char_path, "r") as f:
            char_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find character data for {character}."
    
    # Get character class for advancement table
    char_class = char_data.get("class", "Unknown")
    
    # Load class advancement data
    advancement_path = f"advancement/{char_class.lower()}_advancement.json"
    try:
        with open(advancement_path, "r") as f:
            advancement_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find advancement data for {char_class}."
    
    # Get current level and XP
    current_level = char_data.get("level", 1)
    current_xp = char_data.get("experience", 0)
    
    # Find next level threshold
    next_level_data = next((level for level in advancement_data if level["level"] > current_level), None)
    
    if not next_level_data:
        return f"{character} is at maximum level ({current_level}) with {current_xp} XP."
    
    next_level_xp = next_level_data["xp"]
    next_level = next_level_data["level"]
    
    # Find previous level threshold for progress calculation
    prev_level_data = next((level for level in advancement_data if level["level"] == current_level), None)
    prev_level_xp = prev_level_data["xp"] if prev_level_data else 0
    
    # Calculate progress
    xp_needed = next_level_xp - prev_level_xp
    xp_gained = current_xp - prev_level_xp
    progress_percent = min(100, int((xp_gained / xp_needed) * 100))
    
    # Create progress bar
    bar_length = 20
    filled_length = int(bar_length * progress_percent / 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # Format the output
    return f"""📊 **XP Status for {character}**
Level: {current_level}
XP: {current_xp} / {next_level_xp} (Level {next_level})
Progress: {progress_percent}%
[{bar}]
XP needed for next level: {next_level_xp - current_xp}"""

async def improve_attribute(character: str, attribute: str) -> str:
    """
    Improve a character's attribute by 1 point.
    
    Args:
        character: The character's name
        attribute: The attribute to improve (strength, intelligence, wisdom, constitution, dexterity, charisma)
    
    Returns:
        A formatted string with the result of the attribute improvement
    """
    # Load character data
    char_slug = character.lower().replace(" ", "_")
    char_path = f"characters/{char_slug}.json"
    
    try:
        with open(char_path, "r") as f:
            char_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find character data for {character}."
    
    # Check if character is eligible for attribute improvement
    current_level = char_data.get("level", 1)
    if current_level % 4 != 0:
        return f"{character} is not eligible for attribute improvement at level {current_level}. Attribute improvements are available at levels 4, 8, 12, etc."
    
    # Check if attribute improvement has already been used
    if char_data.get("attribute_improvement_used", False):
        return f"{character} has already used their attribute improvement for level {current_level}."
    
    # Validate attribute
    attribute = attribute.lower()
    valid_attrs = ["strength", "intelligence", "wisdom", "constitution", "dexterity", "charisma"]
    if attribute not in valid_attrs:
        return f"Invalid attribute: {attribute}. Must be one of: strength, intelligence, wisdom, constitution, dexterity, charisma."
    
    # Find the attribute in the character data (case-insensitive)
    attr_key = next((key for key in char_data["attributes"] if key.lower() == attribute), None)
    if not attr_key:
        return f"Attribute {attribute} not found in character data."
    
    # Add or increment level_mod
    if "level_mod" not in char_data["attributes"][attr_key]:
        char_data["attributes"][attr_key]["level_mod"] = 1
    else:
        char_data["attributes"][attr_key]["level_mod"] += 1
    
    # Update total
    char_data["attributes"][attr_key]["total"] = (
        char_data["attributes"][attr_key]["base"] + 
        char_data["attributes"][attr_key]["race_mod"] + 
        char_data["attributes"][attr_key]["level_mod"]
    )
    
    # Mark attribute improvement as used
    char_data["attribute_improvement_used"] = True
    
    # Save character data
    with open(char_path, "w") as f:
        json.dump(char_data, f, indent=2)
    
    # Format the output
    new_value = char_data["attributes"][attr_key]["total"]
    new_modifier = (new_value - 10) // 2
    modifier_str = f"{new_modifier:+}"
    
    return f"🔼 {character}'s {attr_key} has been improved to {new_value} (modifier: {modifier_str})."

async def show_advancement(character: str) -> str:
    """
    Show the advancement table for a character's class.
    
    Args:
        character: The character's name
    
    Returns:
        A formatted string with the character's class advancement table
    """
    # Load character data
    char_slug = character.lower().replace(" ", "_")
    char_path = f"characters/{char_slug}.json"
    
    try:
        with open(char_path, "r") as f:
            char_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find character data for {character}."
    
    # Get character class for advancement table
    char_class = char_data.get("class", "Unknown")
    
    # Load class advancement data
    advancement_path = f"advancement/{char_class.lower()}_advancement.json"
    try:
        with open(advancement_path, "r") as f:
            advancement_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return f"Could not find advancement data for {char_class}."
    
    # Get current level and XP
    current_level = char_data.get("level", 1)
    current_xp = char_data.get("experience", 0)
    
    # Format the output
    lines = [f"📈 **Advancement Table for {char_class}**"]
    lines.append("```")
    lines.append("Level | XP      | HD    | BHB   | ST")
    lines.append("------|---------|-------|-------|----")
    
    for level in advancement_data:
        # Highlight current level
        prefix = "➤ " if level["level"] == current_level else "  "
        lines.append(f"{prefix}{level['level']:<5} | {level['xp']:<7} | {level['hd']:<5} | {level['bhb']:<5} | {level['st']}")
    
    lines.append("```")
    lines.append(f"Current Level: {current_level}")
    lines.append(f"Current XP: {current_xp}")
    
    # Find next level threshold
    next_level_data = next((level for level in advancement_data if level["level"] > current_level), None)
    if next_level_data:
        lines.append(f"XP needed for next level: {next_level_data['xp'] - current_xp}")
    else:
        lines.append("Maximum level reached!")
    
    return "\n".join(lines)

async def help_command(command: str = "") -> str:
    """
    Display a list of all available commands or detailed help for a specific command.
    
    Args:
        command: Optional specific command to get detailed help for
    
    Returns:
        A formatted string with command help information
    """
    # Dictionary of all commands with their descriptions
    commands = {
        "add_inventory": "Add an item to a character's inventory",
        "remove_inventory": "Remove an item from a character's inventory",
        "show_inventory": "Display a character's current inventory",
        "add_credits": "Add credits to a character's balance",
        "spend_credits": "Spend credits from a character's balance",
        "show_credits": "Show a character's current credit balance",
        "buy_item": "Purchase an item using credits",
        "transfer_credits": "Transfer credits between characters",
        "show_ledger": "View transaction history",
        "roll_dice": "Roll dice using standard RPG notation",
        "start_scenario": "Generate a new adventure scenario",
        "log_scene": "Record an important scene for future reference",
        "summarize_recent_chat": "Get a summary of recent gameplay",
        "summarize_scene_log": "Review all recorded scenes",
        "skill_check": "Perform an attribute check against a difficulty",
        "award_xp": "Give experience points to a character",
        "show_xp": "Display current XP and progress to next level",
        "improve_attribute": "Increase an attribute by 1 point",
        "show_advancement": "View the advancement table for a character's class",
        "help": "Display this help information"
    }
    
    if command and command.strip():
        # Show detailed help for a specific command
        command = command.lower().strip('/')
        if command not in commands:
            return f"Command '/{command}' not found. Use /help to see all available commands."
        
        # Get the function object to access its docstring
        current_module = sys.modules[__name__]
        
        # Try to get the function directly
        func = getattr(current_module, command, None)
        
        # If not found, try with _command suffix (for help_command)
        if func is None and command == "help":
            func = getattr(current_module, "help_command", None)
            
        # If still not found, try with other common patterns
        if func is None:
            # Try some common variations
            variations = [
                command,                  # exact match
                command + "_command",     # command suffix
                command + "_function",    # function suffix
                "summarize_" + command    # summarize prefix
            ]
            
            for var in variations:
                func = getattr(current_module, var, None)
                if func is not None:
                    break
        
        # Special case for summarize_scene_log which uses a different function name
        if command == "summarize_scene_log" and func is None:
            func = getattr(current_module, "summarize_scene_log_function", None)
        
        if func:
            # Try to get the docstring directly from the function
            doc = inspect.getdoc(func) or "No documentation available."
            
            # If the function is an AIFunction, try to get the wrapped function
            if hasattr(func, "__wrapped__"):
                wrapped_func = func.__wrapped__
                try:
                    signature = inspect.signature(wrapped_func)
                    doc = inspect.getdoc(wrapped_func) or doc  # Use wrapped docstring if available
                except (ValueError, TypeError):
                    # If we can't get the signature from wrapped function, try the original
                    try:
                        signature = inspect.signature(func)
                    except (ValueError, TypeError):
                        return f"Detailed help for '/{command}' is not available (cannot get signature)."
            else:
                # Try to get signature directly
                try:
                    signature = inspect.signature(func)
                except (ValueError, TypeError):
                    return f"Detailed help for '/{command}' is not available (cannot get signature)."
            
            # Extract parameters
            params = []
            for name, param in signature.parameters.items():
                if name == 'return':
                    continue
                
                # Format the parameter
                if param.default is param.empty:
                    params.append(f"{name} (required)")
                else:
                    default = "None" if param.default is None else param.default
                    params.append(f"{name} (default: {default})")
            
            return f"""**/{command}**
            
Description: {commands[command]}

Parameters:
{chr(10).join(f"- {p}" for p in params)}

Details:
{doc}
"""
        else:
            return f"Detailed help for '/{command}' is not available (function not found)."
    else:
        # Show list of all commands
        lines = ["**Available Commands:**"]
        
        for cmd, desc in sorted(commands.items()):
            lines.append(f"- /{cmd}: {desc}")
        
        lines.append("\nUse /help [command] for detailed information about a specific command.")
        
        return "\n".join(lines)

# ✅ Simpler wrapping for current AIFunction version
add_inventory = AIFunction(add_inventory)
remove_inventory = AIFunction(remove_inventory)
show_inventory = AIFunction(show_inventory)
add_credits = AIFunction(add_credits)
spend_credits = AIFunction(spend_credits)
show_credits = AIFunction(show_credits)
buy_item = AIFunction(buy_item)
transfer_credits = AIFunction(transfer_credits)
show_ledger = AIFunction(show_ledger)
roll_dice = AIFunction(roll_dice)
start_scenario = AIFunction(start_scenario)
log_scene = AIFunction(log_scene)
summarize_recent_chat = AIFunction(summarize_recent_chat)
summarize_scene_log = AIFunction(summarize_scene_log_function)
skill_check = AIFunction(skill_check)
award_xp = AIFunction(award_xp)
show_xp = AIFunction(show_xp)
improve_attribute = AIFunction(improve_attribute)
show_advancement = AIFunction(show_advancement)
help_command = AIFunction(help_command)
