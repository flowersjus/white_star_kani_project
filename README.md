# White Star + Kani AI Project Notes

This document tracks the current structure, decisions, tools, and history of your AI-powered solo TTRPG system built with Kani and the White Star ruleset.

---

## 🧠 Project Overview

You are using [Kani](https://github.com/zhudotexe/kani) to serve as a fully interactive AI Game Master for solo sci-fi tabletop RPG sessions using the **White Star** rules.

- Kani model: `OpenAIEngine` using `gpt-4o`
- AI is given structured access to JSON files to persist and manipulate state
- All tools are registered via `AIFunction`

-----

## 🧪 Quickstart (How to Resume Project)

### With Script

`./run.sh`

### Without Script

```bash
# Navigate to the project directory
cd ~/Github/white_star_kani_project

# Activate virtual environment
source kani-env/bin/activate

# Run the AI DM
python run_kani.py
```

### In case of loss of environment

```bash
pip install -r requirements.txt
```



---

## ✅ Current Capabilities

### 📦 Inventory Management

Inventory is stored in:

```bash
ephemeral/inventory.json
```

Format:

```json
{
  "Jax Varn": {
    "Energy Cell": 3,
    "Laser Pistol": 1
  }
}
```

Supported functions:

- `/add_inventory "Jax Varn", "Energy Cell", 2`
- `/remove_inventory "Jax Varn", "Energy Cell", 1`
- `/show_inventory` or `/show_inventory "Jax Varn"`

Internally, each of these is defined as an `async def` Python function and wrapped using `AIFunction()`.

### 🧰 Tools Created

| Tool               | Description                                        |
| ------------------ | -------------------------------------------------- |
| `add_inventory`    | Adds item quantity to a character’s inventory      |
| `remove_inventory` | Subtracts item quantity or removes item entirely   |
| `show_inventory`   | Displays character inventory, defaults to Jax Varn |

---

## 🔍 Technical Decisions

### ❗ Kani Decorator Issue

The Kani version on PyPI **does not export** `@ai_function` correctly. Several attempts to use `@ai_function()` failed because:

- PyPI install did not expose `kani.registry`
- GitHub install did not include `@ai_function` in `__init__.py`
- Even editable installs failed to register decorated functions properly

**Solution:** Manually wrapped each tool using:

```python
from kani.ai_function import AIFunction
...
add_inventory = AIFunction(add_inventory)
```

This works reliably and avoids the broken decorator.

---

## 📁 Project Structure (April 2025)

```plaintext
white_star_kani_project/
├── advancement/
├── ai_dm/              # system prompt config, Mythic GME rules
├── character_creation/ # class and race options
├── characters/         # Jax Varn + summary_cards/
├── equipment/          # standard_gear.json, armor.json, etc.
├── ephemeral/          # active_gifts, inventory.json, etc.
├── npcs/               # creatures and aliens
├── plugins/            # mythic_gme_2e.json etc.
├── rules/              # core_combat.json, meditations.json
├── starships/          # starships.json, modifications
├── system_docs/        # future: faq, license
├── tools.py            # inventory functions (AIFunction wrapped)
├── run_kani.py         # entrypoint to launch the game
└── project.json        # Kani project descriptor
```

---

## 📝 TODO / Roadmap

### 📈 Short-Term

- Create a tool `/summarize_last_scene` that:
  - Looks at the scene
  - Asks the AI to generate a title + summary
- Alternatively, auto-log at intervals to save the entire scene as you go
- Add a 'possible commands' command
  - lists the possible commands

### 🌐 Worldbuilding Goals

- 🪐 Worldbuilding files (`sectors`, `factions`, `contacts`)
- Possibly create a template for world creation
  - Type of world


### Inventory Managment

- 🏷 Metadata linking (pull item names/descriptions from equipment files) `equipment.json`
- 🤖 Auto-triggers like “If I loot, add items automatically unless I cancel”
- ⚖️ Add item weights
- 🤝 Party-based inventory

### 🎭 Character Management

- NPC Memory
  - Track NPCs like in a lightweight json (`npcs.json`) with notes about:
    - personality
    - items
    - past interactions
- Character Creation
- Should we add clothing?
- Money (Credits)
  - 🛒 `/buy_item` or `/transfer_credits` to add economy mechanics

  - 📜 Transaction Log
    - Store every `/add_credits` and `/spend_credits` call with reason, timestamp, and amount
    - Output to `ledger.json`

  - 💸 Named Transactions
    - Example: `/spend_credits "Jax Varn", 15, "Entry fee for illegal fighting ring"`

  - 🔄 Auto Deduct from Purchases
    - When `/buy_item` is called, it deducts credits based on `equipment.json` prices

  - 🧾 Receipt Preview
    - After `/spend_credits`, return: “💳 Spent 15 credits on: [reason] — New balance: 95cr”


### Experience Management

- Have AI add experience to characters
- Have AI advance character levels (with notification)

### Narrative

- 🧪 Dice rolling tools (`/roll 2d6+1`)
- Tasks / Requests / Quests
  - Log active missions, objectives, and progress
  - Stored in `ephemeral/quests.json` or similar
- 🎬 Scene setup with Chaos Factor
- Faction or Location Tracker
- 📖 Summarizing last scene
- 📜 Scene logging
  - 🧾 Log each major scene to `scene_log/<character>.json` with a description and timestamp
  - Makes it easier to resume or recap later
  - Possibly use Kani's suggestion `Chat History`
    - [Kani Read the Docs-Chat History](https://kani.readthedocs.io/en/latest/customization/chat_history.html)
- Mythic GME

### AI

- Consider migrating to another ai (local or openrouter)
- Optimization
  - [Subkani](https://kani.readthedocs.io/en/latest/advanced/subkani.html)
    - Uses a smaller context (cheaper) model as a parent that makes calls to a larger context model


## 💡 Tips for Future You

- If the AI throws a `TypeError` about `function has no attribute 'name'`, you're likely importing an undecorated or unwrapped function — remember to use `AIFunction()` manually
- Your OpenAI key is stored inline in `run_kani.py` for now — consider environment variable support
- You can register more tools at any time by importing and adding to the `functions=[...]` list
- If you ever reinstall Kani and decorators start working, you can refactor to `@ai_function()`
- ## 🧾 Available Commands

  - /add_inventory, /remove_inventory, /show_inventory
  - /add_credits, /spend_credits, /show_credits
  - /transfer_credits, /buy_item, /show_ledger
  - /roll_dice
  - /start_scenario, /log_scene

---

## 🤝 Contact Points / Resources

- Kani GitHub: [https://github.com/zhudotexe/kani](https://github.com/zhudotexe/kani)
- White Star RPG (core rules): stored in `rules/`
- Your character: `characters/jax_varn.json`

---

## Version Reference

- Python 3.12
- Kani 1.4.2 (editable install from GitHub)
- Installed with: `pip install -e ".[openai]"`

-----

## Important Files

- `run_kani.py`

  - ```python
    import json
    import os
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
    )
    
    # Load the character inventory manually
    with open("ephemeral/inventory.json") as f:
        inventory = json.load(f)
    
    # Build the system prompt
    system_prompt = f"""
    You are the AI Game Master for a sci-fi tabletop game using the White Star ruleset.
    
    Your current active character is Jax Varn, a Human Mercenary. His known inventory is (item: quantity format):
    {json.dumps(inventory["Jax Varn"], indent=2)}
    
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
        ],
    )
    
    # Launch terminal chat
    chat_in_terminal(ai)
    ```

- `tools.py`

  - ```py
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
    ```
    
  - 
