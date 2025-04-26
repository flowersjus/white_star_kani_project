import asyncio
import json
import os
from tools import skill_check

async def test_skill_checks():
    """Test the skill check system with a sample character."""
    
    # Check if we have any characters to test with
    characters_dir = "characters"
    character_files = [
        f for f in os.listdir(characters_dir)
        if f.endswith(".json") and not f.startswith("summary_")
    ]
    
    if not character_files:
        print("No character files found. Please create a character first.")
        return
    
    # Use the first character for testing
    char_file = character_files[0]
    char_name = os.path.splitext(char_file)[0].replace("_", " ").title()
    
    print(f"Testing skill checks with character: {char_name}\n")
    
    # Load character data to display attributes
    with open(f"characters/{char_file}") as f:
        char_data = json.load(f)
    
    print("Character Attributes:")
    for attr, values in char_data["attributes"].items():
        total = values["total"]
        modifier = (total - 10) // 2
        print(f"  {attr.title()}: {total} (Modifier: {modifier:+d})")
    
    print("\n=== SKILL CHECK EXAMPLES ===\n")
    
    # Test different difficulty levels
    difficulties = [
        ("Easy", 10),
        ("Average", 14),
        ("Hard", 18)
    ]
    
    # Test with different attributes
    attributes = ["strength", "intelligence", "wisdom", "dexterity", "charisma"]
    
    # Example scenarios for each attribute
    scenarios = {
        "strength": "force open a jammed door",
        "intelligence": "recall information about an alien species",
        "wisdom": "notice a hidden surveillance device",
        "dexterity": "slip past a security drone undetected",
        "charisma": "convince a guard to let you pass"
    }
    
    # Run a few example skill checks
    for attr in attributes:
        scenario = scenarios[attr]
        for diff_name, diff_value in difficulties:
            print(f"Attempting to {scenario} ({diff_name} DC {diff_value}):")
            result = await skill_check(char_name, attr, diff_value, scenario)
            print(f"{result}\n")
    
    print("=== CRITICAL SUCCESS/FAILURE EXAMPLES ===\n")
    print("Note: These examples use a fixed roll value for demonstration purposes.")
    
    # Demonstrate critical success (natural 20)
    print("Critical Success Example (natural 20):")
    # Mock the random.randint function to always return 20
    import random
    original_randint = random.randint
    random.randint = lambda a, b: 20
    result = await skill_check(char_name, "dexterity", 14, "perform a perfect backflip")
    print(f"{result}\n")
    
    # Demonstrate critical failure (natural 1)
    print("Critical Failure Example (natural 1):")
    # Mock the random.randint function to always return 1
    random.randint = lambda a, b: 1
    result = await skill_check(char_name, "intelligence", 14, "remember the security code")
    print(f"{result}\n")
    
    # Restore the original random.randint function
    random.randint = original_randint
    
    print("=== SKILL CHECK SYSTEM TESTING COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_skill_checks())
