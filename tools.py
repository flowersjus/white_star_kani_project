import json
import random
import re
import os
from kani.ai_function import AIFunction
from datetime import datetime

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

async def start_scenario() -> str:
    """Generate a basic adventure scenario: location, situation, and hook."""
    
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

    npc_or_detail = [
        "A woman with mirrored eyes is watching you from a distance",
        "Your contact, code-named 'Sable,' is running late",
        "The power keeps flickering every 20 seconds — like clockwork",
        "A child’s voice keeps playing over the station intercom, though no children are registered on board",
        "Everyone here seems to know your name — and not in a good way"
    ]

    scenario = f"""
🪐 **SCENARIO START**

**Location:** {random.choice(locations)}
**Situation:** {random.choice(situations)}
**Detail:** {random.choice(npc_or_detail)}
"""
    return scenario.strip()

import os
from datetime import datetime

async def log_scene(character: str, title: str, summary: str) -> str:
    """Save a scene description under a specific character's log."""
    LOG_DIR = "scene_log"
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"{character.replace(' ', '_').lower()}.json")

    try:
        with open(log_path, "r") as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = []

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "title": title,
        "summary": summary
    }
    log.append(entry)

    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

    return f"Scene '{title}' logged for {character}."

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


