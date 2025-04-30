```
 _       ____  __________________   ______________    ____ 
| |     / / / / /  _/_  __/ ____/  / ___/_  __/   |  / __ \
| | /| / / /_/ // /  / / / __/     \__ \ / / / /| | / /_/ /
| |/ |/ / __  // /  / / / /___    ___/ // / / ___ |/ _, _/ 
|__/|__/_/ /_/___/ /_/ /_____/   /____//_/ /_/  |_/_/ |_| 
                    White Star + Kani
```

# White Star + Kani AI Project

An AI-powered solo TTRPG system built with Kani and the White Star ruleset.

---

## 🧠 Project Overview

This project uses [Kani](https://github.com/zhudotexe/kani) to serve as a fully interactive AI Game Master for solo sci-fi tabletop RPG sessions using the **White Star** rules.

- Kani model: `OpenAIEngine` using `gpt-4o`
- AI is given structured access to JSON files to persist and manipulate state
- All tools are registered via `AIFunction`

-----

## 🧪 Quickstart

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### First-Time Setup

#### For Linux and macOS:

```bash
# Navigate to the project directory
cd path/to/white_star_kani_project

# Create a virtual environment
python3 -m venv kani-env

# Activate the virtual environment
source kani-env/bin/activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Set up your OpenAI API key
cp .env.example .env
# Edit the .env file and replace 'your_api_key_here' with your actual OpenAI API key
```

#### For Windows:

```powershell
# Navigate to the project directory
cd path\to\white_star_kani_project

# Create a virtual environment
python -m venv kani-env

# Activate the virtual environment
.\kani-env\Scripts\Activate.ps1

# Upgrade pip (recommended)
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Set up your OpenAI API key
copy .env.example .env
# Edit .env and add your API key
```

### Running the Game

#### For Linux and macOS:

Using the provided script:

```bash
# Make sure the script is executable
chmod +x run.sh

# Run the game
./run.sh
```

Or manually:

```bash
# Activate the virtual environment
source kani-env/bin/activate

# Run the AI DM
python run_kani.py
```

#### For Windows:

Using the provided batch script:

```cmd
# Run the game
run.bat
```

Or manually:

```powershell
# Activate the virtual environment
.\kani-env\Scripts\Activate.ps1

# Run the AI DM
python run_kani.py
```

---

## ✅ Current Capabilities

### 👤 Character Creation & Management

- Enhanced character creation with:
  - Origin-based race and class restrictions
  - Intelligent name generation based on character class
  - Proper pronoun handling throughout character lifecycle
  - AI-generated or manual backstory options
- Character selection at startup
- Enhanced welcome screen showing:
  - Character stats and attributes
  - Current inventory and credits
  - Recent adventure recap
  - Backstory and special abilities

### 📝 Name Generation System

- Markov chain-based name generation
- Class-specific name patterns
- Support for:
  - Character names based on class
  - Location names (stations, drifts)
  - Robot designations
  - NPC names

### 🎭 Pronoun System

- Comprehensive pronoun support:
  - Custom pronouns for any gender identity
  - Proper pronoun persistence in character data
  - Consistent pronoun usage in all AI interactions
  - Default they/them pronouns for new characters
- Smart pronoun handling in:
  - Character backstories
  - Scene descriptions
  - NPC interactions
  - Adventure summaries

### 📦 Inventory Management

- Inventory is stored in `ephemeral/inventory.json`
- Characters can add, remove, and view items in their inventory
- Supported functions:
  - `/add_inventory "Character Name", "Item Name", Quantity`
  - `/remove_inventory "Character Name", "Item Name", Quantity`
  - `/show_inventory` or `/show_inventory "Character Name"`

### 🧾 Credit + Economy System

- Credits stored in `ephemeral/credits.json`
- Characters can:
  - `/add_credits`, `/spend_credits`, `/show_credits`
  - `/transfer_credits` to other characters
  - `/buy_item` using prices from `equipment/*.json` (fuzzy matched)
- Each transaction is recorded in `ephemeral/ledger.json` with timestamps:
  - `/show_ledger` shows the last 10 transactions for a character

### 🎲 Dice Tools

- `/roll_dice "2d6+1"` rolls and returns real results
- AI is instructed *not* to make up rolls—only use the tool

### 🎬 Scenario Generator

- `/start_scenario "Character Name"` begins a new adventure
  - Includes **Location**, **Situation**, **Narrative Detail**
  - Auto-includes last 3 scene summaries if available
  - Uses character-appropriate pronouns in all descriptions
  - Generates unique location and NPC names

### 📖 Scene Logging + Summary

- Character-specific scene logs stored in `scene_log/<character_slug>.json`
- `/log_scene` stores a title + summary with timestamps
- `/summarize_scene_log` returns a chronological list of all scenes
- Intelligent handling of session end logs:
  - AI-generated contextual summaries for session ends
  - Prevents duplicate session end entries within an hour
  - Updates existing session end entries instead of creating duplicates
- Full support for multi-scene memory, even across sessions

### 🧠 Chat Memory

- All messages are saved to `chat_log/<character>.jsonl`
- `/summarize_recent_chat` summarizes the last 10 user+AI exchanges

### 🎮 Session Management

- `/quit` command for graceful session endings:
  - AI generates a contextual summary of the current situation
  - Automatically logs the session end with the summary
  - Prevents duplicate session end entries
  - Updates existing session end entries if within an hour
  - Saves all progress before exiting

### 🧩 Character Management

- Character selection at startup
- Enhanced welcome screen for existing characters:
  - Displays character information (class, race, level, HP)
  - Shows special abilities and long-term goals
  - Lists current inventory and credits
  - Provides an AI-generated adventure recap that includes:
    - Current location (e.g., "Currently on Tycho-221 in the Frontier Scrapyards")
    - Primary mission/objective (e.g., "recover the stolen quantum flux regulator")
    - Narrative summary of recent adventures
  - Includes a "Press Enter to continue" prompt
- Character creation with:
  - Origin selection (Human, Machine Hybrid, Alien, Robot)
  - Race selection based on origin with unique options for each
  - Class restrictions based on origin and race combinations
  - Suggested alignments shown for applicable classes (e.g., "Most Star Knights are Lawful")
  - 3 rolling methods (3d6 in order, assignable 3d6, 4d6 drop-lowest)
  - Class and race selection from `character_creation/*.json`
  - Attribute modifiers from race (`modifiers` field)
  - Saves class features, XP bonus rules, and race abilities
  - Auto-creates inventory and credit records
  - Starting credits determined by rolling 3d6×10 (as per White Star rules)
  - AI-generated or manual backstory creation
- Equipment selection:
  - Manual shopping with categorized equipment lists
  - Auto-assign option for quick equipment loadouts
  - Budget management with remaining credits display
  - Equipment restrictions based on class
- Markov chain name generator:
  - Generates first names based on character class
  - Generates last names from a common pool of sci-fi/fantasy surnames
  - Creates full names (first + last) for all character types except robots
  - Ensures names are pronounceable and follow natural language patterns
  - Standalone testing via `python character_creation/test_name_generator.py`

### 🎯 Skill Checks & Advancement

- `/skill_check` performs attribute-based checks against difficulty classes
  - Supports all six attributes (STR, INT, WIS, CON, DEX, CHA)
  - Handles critical success/failure on natural 20/1
  - Includes descriptive output with roll details
  - Uses D&D-style modifiers: (attribute-10)/2
  - Difficulty Classes: Easy (10), Average (14), Hard (18)
  - Full documentation in `docs/skill_check_guide.md`
  - Rules formalized in `rules/skill_checks.json`
  - Test script available: `python test_skill_check.py`
- XP and leveling system:
  - `/award_xp` grants experience points with optional bonuses
  - `/show_xp` displays progress to next level with visual bar
  - `/improve_attribute` increases attributes at milestone levels
  - `/show_advancement` displays the full advancement table
  - Class-specific advancement tables in `advancement/` directory
  - Automatic level-up with HP increases, stat updates, and attribute improvements
  - XP bonuses based on prime attributes (defined in character class data)
- All XP awards are logged to `ephemeral/xp_log.json`
- Character welcome screen displays level and XP information
- Utility script `update_characters.py` to update existing characters with XP fields

### 🔍 Help System

- Built-in command documentation with `/help`
- Detailed parameter information with `/help [command]`
- Shows function signatures and descriptions

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

## 📁 Project Structure

```plaintext
white_star_kani_project/
├── advancement/          # Character advancement tables
├── ai_dm/                # System prompt config, Mythic GME rules
├── character_creation/   # Class and race options
├── characters/           # Character JSON files + summary_cards/
├── chat_log/             # Conversation history by character
├── docs/                 # Documentation files
├── equipment/            # standard_gear.json, armor.json, etc.
├── ephemeral/            # Runtime state (inventory, credits, etc.)
├── npcs/                 # Creatures and aliens
├── plugins/              # mythic_gme_2e.json etc.
├── rules/                # core_combat.json, meditations.json
├── scene_log/            # Logged scene summaries
├── starships/            # starships.json, modifications
├── tools.py              # AI-callable functions (AIFunction wrapped)
├── run_kani.py           # Entrypoint to launch the game
├── requirements.txt      # Python dependencies
└── project.json          # Kani project descriptor
```

---

## 🚳 Future Plans

White Star + Kani is actively evolving!

Upcoming major features include:
- Personal quest systems and dynamic character goals
- Procedural scene generation for organic storytelling
- Worldbuilding expansion (sectors, factions, planets)
- Starship management and modular upgrades
- Faction reputation and evolving character relationships

For full details on planned systems, visit the 📚 [Roadmap](docs/ROADMAP.md).

---

## 📂 Development Status

This project is in **active development** (Pre-Alpha Stage).  
Expect regular feature updates, gameplay expansions, and narrative enhancements!

**Current Focus:**
- Deepening character progression through XP, quests, and personal goals
- Expanding world generation (sectors, star systems, NPCs)
- Enhancing AI-driven scene flow and dynamic storytelling

> **Version:** 0.3 (Character creation, inventory, skill checks, XP/leveling fully operational.)

---

## 🧾 Available Commands

- **Inventory Management**: `/add_inventory`, `/remove_inventory`, `/show_inventory`
- **Economy System**: `/add_credits`, `/spend_credits`, `/show_credits`, `/transfer_credits`, `/buy_item`, `/show_ledger`
- **Dice & Skill Checks**: `/roll_dice`, `/skill_check`
- **Scenario Management**: `/start_scenario`, `/log_scene`
- **Memory & Summaries**: `/summarize_recent_chat`, `/summarize_scene_log`
- **Character Advancement**: `/award_xp`, `/show_xp`, `/improve_attribute`, `/show_advancement`
- **Help System**: `/help`, `/help [command]`

---

## 💡 Tips for Development

- If the AI throws a `TypeError` about `function has no attribute 'name'`, you're likely importing an undecorated or unwrapped function — remember to use `AIFunction()` manually
- Your OpenAI key is stored in `.env` file (loaded via dotenv)
- You can register more tools at any time by importing and adding to the `functions=[...]` list
- If you ever reinstall Kani and decorators start working, you can refactor to `@ai_function()`

---

## 🤝 Resources

- Kani GitHub: [https://github.com/zhudotexe/kani](https://github.com/zhudotexe/kani)
- White Star RPG (core rules): stored in `rules/`

---

## Version Reference

- Python 3.12
- Kani 1.4.2 (editable install from GitHub)
- Installed with: `pip install -e ".[openai]"`

---

## 📜 Citation
This project uses [Kani](https://github.com/zhudotexe/kani) for AI orchestration.
If you use this project or build upon it, please consider citing Kani:
```
Andrew Zhu, Liam Dugan, Alyssa Hwang, Chris Callison-Burch. 2023. Kani: A Lightweight and Highly Hackable Framework for Building Language Model Applications. Proceedings of the 3rd Workshop for Natural Language Processing Open Source Software (NLP-OSS 2023), pages 65–77, Singapore. Association for Computational Linguistics. https://doi.org/10.18653/v1/2023.nlposs-1.8
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

