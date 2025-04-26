#!/usr/bin/env python3
"""
Script to update existing character files with XP and advancement fields.
This ensures that existing characters are compatible with the new XP and advancement system.
"""

import json
import os
import random

def update_character_files():
    """Update all character files in the characters directory."""
    characters_dir = "characters"
    
    # Get all character files
    character_files = [
        f for f in os.listdir(characters_dir)
        if f.endswith(".json") and not f.startswith("summary_")
    ]
    
    print(f"Found {len(character_files)} character files to update.")
    
    for filename in character_files:
        filepath = os.path.join(characters_dir, filename)
        
        # Load character data
        with open(filepath, "r") as f:
            char_data = json.load(f)
        
        # Check if character already has the required fields
        if all(field in char_data for field in ["experience", "level", "hp", "max_hp", "bhb", "st"]):
            print(f"Character {char_data.get('name', filename)} already has all required fields.")
            continue
        
        # Add missing fields
        modified = False
        
        if "level" not in char_data:
            char_data["level"] = 1
            modified = True
            
        if "experience" not in char_data:
            char_data["experience"] = 0
            modified = True
            
        if "bhb" not in char_data:
            char_data["bhb"] = "+0"  # Default Base Hit Bonus
            modified = True
            
        if "st" not in char_data:
            char_data["st"] = 14  # Default Saving Throw
            modified = True
        
        # Calculate HP if missing
        if "hp" not in char_data or "max_hp" not in char_data:
            # Get Constitution modifier
            con_mod = 0
            if "attributes" in char_data and "Constitution" in char_data["attributes"]:
                con_value = char_data["attributes"]["Constitution"].get("total", 10)
                con_mod = (con_value - 10) // 2
            
            # Roll for HP (1d6 + Con modifier)
            base_hp = random.randint(1, 6)
            initial_hp = max(1, base_hp + con_mod)  # Ensure minimum of 1 HP
            
            if "hp" not in char_data:
                char_data["hp"] = initial_hp
                modified = True
                
            if "max_hp" not in char_data:
                char_data["max_hp"] = initial_hp
                modified = True
        
        # Save updated character data
        if modified:
            with open(filepath, "w") as f:
                json.dump(char_data, f, indent=2)
            print(f"Updated character {char_data.get('name', filename)} with missing fields.")
        else:
            print(f"No updates needed for {char_data.get('name', filename)}.")

if __name__ == "__main__":
    update_character_files()
    print("Character update complete!")
