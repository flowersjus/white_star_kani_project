import json
import os
import asyncio
import re
import random
import glob
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
    quit_game,
)

with open("character_creation/character_classes.json") as f:
    classes_data = json.load(f)["classes"]

with open("character_creation/character_races.json") as f:
    races_data = json.load(f)["character_races"]

async def generate_ai_backstory(name: str, char_class: str, char_race: str, char_alignment: str, attributes: dict, engine) -> str:
    """Generate an AI-crafted backstory based on character attributes and choices."""
    # Define possible character flaws
    character_flaws = [
        "haunted by a betrayal they couldn't prevent",
        "secretly blames themselves for a past tragedy",
        "trusts no one completely, not even allies",
        "harbors guilt over abandoning someone long ago",
        "feels unworthy of the respect they receive",
        "is obsessed with controlling every situation to avoid disaster",
        "nurses a quiet hatred for authority after being wronged",
        "suffers nightmares of their worst mistake",
        "believes deep down that survival always comes at a cost",
        "keeps a carefully guarded secret about their true origins"
    ]
    
    # Select a random flaw
    selected_flaw = random.choice(character_flaws)
    
    # Create a prompt that incorporates character details
    highest_attrs = sorted(
        [(k, v["total"]) for k, v in attributes.items()],
        key=lambda x: x[1],
        reverse=True
    )[:2]  # Get top 2 attributes
    
    prompt = f"""
    Create a 3-5 sentence character backstory for a {char_race} {char_class} named {name} with {char_alignment} alignment.
    Their highest attributes are {highest_attrs[0][0]} ({highest_attrs[0][1]}) and {highest_attrs[1][0]} ({highest_attrs[1][1]}).
    
    The backstory should:
    1. Explain how the character developed their strongest attributes through struggle, hardship, or morally grey experiences.
    2. Tie in their alignment and class choice naturally.
    3. Include a defining event that left a scar: a loss, betrayal, mistake, or harsh reality.
    4. Emphasize survival, difficult choices, or the cost of success when appropriate.
    5. Keep the tone grounded, realistic, and willing to acknowledge flaws, regrets, and internal conflicts.
    6. Avoid portraying characters as perfect heroes; instead, show how their background shaped them into who they are — for better or worse.
    7. Fit naturally within a sci-fi universe rich with danger, opportunity, and moral complexity.
    
    Additionally, subtly weave this personal flaw into the backstory: "{selected_flaw}"
    
    Write in a vivid, concise style (3–5 sentences), focusing more on the character's internal motivations than external achievements.
    """
    
    # Create a temporary Kani instance for backstory generation using the existing engine
    temp_ai = Kani(engine, system_prompt="You are a character backstory writer for a sci-fi RPG.")
    
    # Get AI response
    response = ""
    async for part in temp_ai.full_round_str(prompt):
        response += part
    
    return response.strip()

def load_equipment_data():
    """Load all equipment data from JSON files in the equipment directory."""
    equipment_data = {}
    equipment_files = glob.glob("equipment/*.json")
    
    for file_path in equipment_files:
        category = os.path.splitext(os.path.basename(file_path))[0]
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Extract the array from the wrapper object
            key = list(data.keys())[0]  # Get the first (and should be only) key
            equipment_data[category] = data[key]
    
    return equipment_data

def display_equipment_menu(equipment_data, remaining_credits):
    """Display available equipment categories."""
    print(f"\nChoose a category to browse (Remaining credits: {remaining_credits}):")
    categories = list(equipment_data.keys())
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category.replace('_', ' ').title()}")
    print(f"{len(categories) + 1}. Show Current Gear")
    print(f"{len(categories) + 2}. Finalize purchases")
    return categories

def display_current_gear(inventory):
    """Display the character's current inventory and total items."""
    print("\n🎒 Current Inventory:")
    if not inventory:
        print("- Empty")
    else:
        for item, quantity in inventory.items():
            print(f"- {item} × {quantity}")
    print("\nPress Enter to return to category selection...")
    input()

def display_category_items(category_data, category_name):
    """Display items in a category with their costs and descriptions."""
    print(f"\n{category_name.replace('_', ' ').title()} Items:")
    for i, item in enumerate(category_data, 1):
        print(f"{i}. {item['name']} - {item['cost']} credits")
        if 'damage' in item:
            print(f"   Damage: {item['damage']}")
        if 'description' in item:
            print(f"   Description: {item['description']}")
        if 'weight' in item:
            print(f"   Weight: {item['weight']}")
    print(f"{len(category_data) + 1}. Back to Gear Categories")
    return category_data

def auto_assign_gear(equipment_data, starting_credits):
    """Automatically assign gear based on weighted probabilities and budget."""
    assigned_gear = []
    total_cost = 0
    
    # Helper function to check if we can afford an item
    def can_afford(item_cost):
        return (total_cost + item_cost) <= (starting_credits - 10)
    
    # Armor selection (30% chance)
    if random.random() < 0.3:
        armor_weights = {'light': 0.7, 'medium': 0.2, 'heavy': 0.1}
        armor_type = random.choices(list(armor_weights.keys()), 
                                  list(armor_weights.values()))[0]
        
        # Filter armor by type and affordability
        affordable_armor = [
            item for item in equipment_data['armor']
            if item.get('type', '').lower() == armor_type and can_afford(item['cost'])
        ]
        
        if affordable_armor:
            selected_armor = random.choice(affordable_armor)
            assigned_gear.append(selected_armor)
            total_cost += selected_armor['cost']
    
    # Melee weapon (80% chance)
    if random.random() < 0.8:
        affordable_melee = [
            item for item in equipment_data['melee_weapons']
            if can_afford(item['cost'])
        ]
        if affordable_melee:
            selected_melee = random.choice(affordable_melee)
            assigned_gear.append(selected_melee)
            total_cost += selected_melee['cost']
    
    # Ranged weapon (50% chance)
    ranged_weapon = None
    if random.random() < 0.5:
        affordable_ranged = [
            item for item in equipment_data['ranged_weapons']
            if can_afford(item['cost'])
        ]
        if affordable_ranged:
            ranged_weapon = random.choice(affordable_ranged)
            assigned_gear.append(ranged_weapon)
            total_cost += ranged_weapon['cost']
    
    # Add ammo if needed
    if ranged_weapon and 'ammo_type' in ranged_weapon:
        ammo_items = [
            item for item in equipment_data['standard_gear']
            if item.get('type') == 'ammo' and 
            item.get('ammo_type') == ranged_weapon.get('ammo_type') and
            can_afford(item['cost'])
        ]
        if ammo_items:
            ammo = random.choice(ammo_items)
            assigned_gear.append(ammo)
            total_cost += ammo['cost']
    
    # Standard gear (2-5 items)
    num_standard_items = random.randint(2, 5)
    affordable_standard = [
        item for item in equipment_data['standard_gear']
        if item.get('type') != 'ammo' and can_afford(item['cost'])
    ]
    
    # Sort by utility (if defined) then cost
    affordable_standard.sort(key=lambda x: (-x.get('utility', 0), x['cost']))
    
    for _ in range(num_standard_items):
        if not affordable_standard or not can_afford(affordable_standard[0]['cost']):
            break
        item = affordable_standard.pop(0)
        assigned_gear.append(item)
        total_cost += item['cost']
    
    return assigned_gear, total_cost

async def handle_equipment_selection(starting_credits, character_name):
    """Handle the equipment selection process."""
    equipment_data = load_equipment_data()
    inventory = {}
    remaining_credits = starting_credits
    
    print("\nHow would you like to equip your character?")
    print("1. Shop for gear manually")
    print("2. Let fate decide (auto-assign gear)")
    
    while True:
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == "1":
            # Manual shopping
            while True:
                categories = display_equipment_menu(equipment_data, remaining_credits)
                try:
                    category_choice = int(input("\nEnter your choice: "))
                    if category_choice == len(categories) + 2:  # Finalize purchases
                        confirm = input("\nFinalize purchases and continue? (y/N): ").lower()
                        if confirm in ['y', 'yes']:
                            break
                        continue
                    elif category_choice == len(categories) + 1:  # Show Current Gear
                        display_current_gear(inventory)
                        continue
                    elif 1 <= category_choice <= len(categories):
                        category = categories[category_choice - 1]
                        while True:
                            category_data = display_category_items(equipment_data[category], category)
                            try:
                                item_choice = int(input("\nEnter your choice: "))
                                if item_choice == len(category_data) + 1:
                                    break
                                
                                if 1 <= item_choice <= len(category_data):
                                    item = category_data[item_choice - 1]
                                    if item['cost'] <= remaining_credits:
                                        confirm = input(f"\nPurchase {item['name']} for {item['cost']} credits? (y/N): ").lower()
                                        if confirm in ['y', 'yes']:
                                            inventory[item['name']] = inventory.get(item['name'], 0) + 1
                                            remaining_credits -= item['cost']
                                            print(f"\nPurchased {item['name']}. Remaining credits: {remaining_credits}")
                                    else:
                                        print("\nNot enough credits!")
                            except ValueError:
                                print("Invalid choice. Please enter a number.")
                except ValueError:
                    print("Invalid choice. Please enter a valid number.")
            break
            
        elif choice == "2":
            # Auto-assign gear
            assigned_gear, total_cost = auto_assign_gear(equipment_data, starting_credits)
            remaining_credits = starting_credits - total_cost
            
            print(f"\n🎒 Auto-assigned gear (Total cost: {total_cost} credits):")
            for item in assigned_gear:
                inventory[item['name']] = inventory.get(item['name'], 0) + 1
                print(f"- {item['name']}")
            print(f"Remaining credits: {remaining_credits}")
            
            confirm = input("\nAccept this equipment loadout? (Y/n): ").lower()
            if confirm in ['', 'y', 'yes']:
                break
            else:
                inventory = {}
                remaining_credits = starting_credits
                continue
        
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    return inventory, remaining_credits

async def create_character() -> str:
    import re
    from tools import roll_dice

    print("\n🛠 Let's create a new character!")

    # Step 1: Choose Origin
    print("\nChoose your origin:")
    print("1. Human")
    print("   Ambitious and adaptable, humans carve their mark across the stars.")
    print("2. Machine Hybrid")
    print("   Blending flesh and machine, hybrids walk the line between humanity and cold efficiency.")
    print("3. Alien")
    print("   From mysterious psychics to primal hunters, aliens shape the galaxy in ways beyond human comprehension.")
    print("4. Robot")
    print("   Built, not born — robots forge their own destinies amid the stars.")

    origin_choice = None
    while origin_choice is None:
        try:
            choice = int(input("\nChoose your origin (1-4): "))
            if 1 <= choice <= 4:
                origin_choice = choice
            else:
                print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Step 2: Handle Race Selection based on Origin
    if origin_choice == 1:  # Human
        print("\nYou chose to be a human.")
        print("Ambitious and adaptable, humans carve their mark across the stars.")
        selected_race = next(race for race in races_data if race["name"] == "Human")
        char_race = "Human"
        # Define available classes for humans
        available_classes = {
            key: classes_data[key] for key in [
                "Aristocrat", "Mercenary", "Pilot", "Star Knight",
                "Soldier", "Space Savage", "Void Knight"
            ] if key in classes_data
        }
    else:
        # Filter races based on origin
        available_races = []
        if origin_choice == 2:  # Machine Hybrid
            print("\nYou chose to be a hybrid.")
            print("Blending flesh and machine, hybrids walk the line between humanity and cold efficiency.")
            available_races = [
                race for race in races_data 
                if race["name"] in ["Cyborg, Metallic", "Cyborg, Replica"]
            ]
        elif origin_choice == 3:  # Alien
            print("\nYou chose to be an alien.")
            print("From mysterious psychics to primal hunters, aliens shape the galaxy in ways beyond human comprehension.")
            available_races = [
                race for race in races_data 
                if race["name"] in [
                    "Falcon-Men", "Felinoids", "Greys", "Mindoids", "Odays",
                    "Procyon", "Qinlons", "Uttins", "Wolflings", "Yabnabs"
                ]
            ]
        else:  # Robot
            print("\nYou chose to be a robot.")
            print("Built, not born — robots forge their own destinies amid the stars.")
            available_races = [
                race for race in races_data 
                if race["name"] in ["Humanoid", "Cannick"]
            ]

        # Display available races
        print("\nAvailable races:")
        for i, race in enumerate(available_races, 1):
            print(f"{i}. {race['name']}: {race['description']}")

        # Select race
        while True:
            try:
                race_choice = int(input("\nChoose a race by number: "))
                if 1 <= race_choice <= len(available_races):
                    selected_race = available_races[race_choice - 1]
                    char_race = selected_race["name"]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(available_races)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        # Define available classes based on origin and race
        if origin_choice == 2:  # Machine Hybrid
            if char_race == "Cyborg, Metallic":
                available_classes = {
                    key: classes_data[key] for key in [
                        "Soldier", "Space Savage"
                    ] if key in classes_data
                }
            else:  # Cyborg, Replica
                available_classes = {
                    key: classes_data[key] for key in [
                        "Aristocrat", "Mercenary", "Pilot",
                        "Soldier", "Space Savage"
                    ] if key in classes_data
                }
        elif origin_choice == 3:  # Alien
            available_classes = {
                key: classes_data[key] for key in [
                    "Alien Brute", "Alien Mystic", "Space Savage"
                ] if key in classes_data
            }
        else:  # Robot
            if char_race == "Cannick":
                available_classes = {
                    key: classes_data[key] for key in [
                        "Soldier", "Mercenary", "Space Savage"
                    ] if key in classes_data
                }
            else:  # Humanoid
                available_classes = {
                    key: classes_data[key] for key in ["Servitor"]
                    if key in classes_data
                }

    # Step 3: Choose class
    print("\nAvailable classes for your origin and race:")
    class_keys = list(available_classes.keys())

    if not class_keys:
        print("Error: No valid classes found for your origin/race combination.")
        print("Defaulting to available basic classes...")
        available_classes = {
            "Soldier": classes_data["Soldier"]
        }
        class_keys = list(available_classes.keys())

    for i, key in enumerate(class_keys, 1):
        print(f"{i}. {key}: {available_classes[key]['description']}")

    while True:
        try:
            choice = int(input("\nChoose a class by number: "))
            if 1 <= choice <= len(class_keys):
                char_class_key = class_keys[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(class_keys)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    char_class = char_class_key  # No need to title() since we're using exact keys
    char_class_data = classes_data[char_class_key]

    # Step 4: Now that we have class and race, handle name generation
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
                    continue
                elif choice == len(generated_names) + 2:
                    name = input("Enter a name for your character: ").strip()
                    if name and re.match("^[a-zA-Z0-9 _-]+$", name):
                        break
                    print("Invalid name. Use letters, numbers, spaces, dashes, or underscores only.")
                else:
                    print("Invalid input. Please choose a valid option.")
            except ValueError:
                print("Invalid input. Please choose a valid option.")
    else:
        # Original manual name entry
        while True:
            name = input("Enter a name for your character: ").strip()
            if name and re.match("^[a-zA-Z0-9 _-]+$", name):
                break
            print("Invalid name. Use letters, numbers, spaces, dashes, or underscores only.")

    print(f"\nWelcome, {name}!")

    # Step 5: Choose rolling method
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

    # Step 6: Choose alignment
    suggested = classes_data[char_class_key].get("suggested_alignment", "Any")
    if suggested in ["Lawful", "Chaotic"]:
        print(f"\nMost {char_class}s are {suggested}")
    char_alignment = input("Enter alignment (e.g., Lawful, Neutral, Chaotic): ").strip().title()

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

    # After alignment selection and before saving character data, add:
    print("\nWould you like to write a custom backstory for your character or have the AI create one?")
    print("1. Write your own backstory")
    print("2. AI generated backstory")
    
    backstory = ""
    while True:
        choice = input("\nEnter your choice (1-2): ").strip()
        if choice == "1":
            print("\nWrite your character's backstory (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:  # Two empty lines in a row
                    break
                lines.append(line)
            backstory = "\n".join(lines[:-1])  # Remove the last empty line
            break
        elif choice == "2":
            print("\nGenerating AI backstory based on your character's attributes and choices...")
            # Create OpenAI engine instance
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Error: OpenAI API key not found. Defaulting to manual backstory entry.")
                print("\nWrite your character's backstory (press Enter twice when done):")
                lines = []
                while True:
                    line = input()
                    if not line and lines and not lines[-1]:
                        break
                    lines.append(line)
                backstory = "\n".join(lines[:-1])
            else:
                engine = OpenAIEngine(api_key, model="gpt-4")
                while True:
                    backstory = await generate_ai_backstory(
                        name, char_class, char_race, char_alignment, structured_attributes, engine
                    )
                    print(f"\nGenerated Backstory:\n{backstory}")
                    
                    # Ask if they like the backstory
                    approval = input(f"\nDo you like this backstory for {name}? (Y/n): ").strip().lower()
                    if approval in ['', 'y', 'yes']:
                        break
                    print("\nGenerating a new backstory...")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    # Step 7: Save character JSON
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
    "backstory": backstory,
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

    # Step 8: Initialize inventory and credits
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
    
    # Add equipment selection
    char_inventory, remaining_credits = await handle_equipment_selection(credits_value, name)
    
    # Update the credits value to remaining amount
    credits_value = remaining_credits
    
    # Continue with existing code...
    credits_path = "ephemeral/credits.json"
    try:
        with open(credits_path, "r") as f:
            credits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        credits = {}
    credits[name] = credits_value
    with open(credits_path, "w") as f:
        json.dump(credits, f, indent=2)

    # Update inventory
    inventory_path = "ephemeral/inventory.json"
    try:
        with open(inventory_path, "r") as f:
            inventory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        inventory = {}
    inventory[name] = char_inventory
    with open(inventory_path, "w") as f:
        json.dump(inventory, f, indent=2)

    return name, True


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
                return selected, False
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

def display_character_welcome(character_name, char_data, char_inventory, char_credits, adventure_summary, is_new_character=False):
    """Display a welcome message with character info, inventory, credits, and recent adventures."""
    
    # Display welcome message
    print(f"\n{'=' * 60}")
    if is_new_character:
        print(f"Your journey begins now, {character_name}!")
    else:
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
    
    # After displaying attributes and before special abilities, add:
    if 'backstory' in char_data and char_data['backstory']:
        print("\n📖 BACKSTORY:")
        print(char_data['backstory'])
    
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
chosen_character, is_new_character = asyncio.run(choose_character())
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
display_character_welcome(chosen_character, char_data, char_inventory, char_credits, adventure_summary, is_new_character)

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
        quit_game,
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

        # Handle quit command
        if user_input.strip().lower() == "/quit":
            # Get a summary from the AI for the session end
            reply_parts = []
            async for part in ai.full_round_str("Generate a brief, one-sentence session end summary that captures the current situation or recent events."):
                reply_parts.append(part)
            summary = "".join(reply_parts).strip()
            
            # Log final scene with AI-generated summary
            await log_scene(
                chosen_character,
                "Session End",
                summary
            )
            print(f"\n🌟 Saving progress for {chosen_character}...")
            print("👋 Until our next adventure! May the stars guide your path.\n")
            break

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
