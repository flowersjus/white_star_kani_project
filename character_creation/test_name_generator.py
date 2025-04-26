#!/usr/bin/env python3
"""
Test script for the Markov chain name generator.
This script allows you to generate names for different character classes
without going through the entire character creation process.
"""

import sys
import os

# Add the project root to the Python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from character_creation.name_generator import generate_full_name

def main():
    """Main function to test the name generator."""
    print("\n🚀 White Star Name Generator Test 🚀")
    print("===================================\n")
    
    # List available character classes
    classes = [
        "aristocrat", "mercenary", "pilot", "star_knight", 
        "alien_brute", "alien_mystic", "robot"
    ]
    
    print("Available character classes:")
    for i, class_name in enumerate(classes, 1):
        print(f"{i}. {class_name.title()}")
    
    # Get user input for class selection
    while True:
        try:
            choice = int(input("\nSelect a class (1-7) or 0 to exit: "))
            if choice == 0:
                print("\nExiting name generator. Goodbye!")
                return
            if 1 <= choice <= len(classes):
                selected_class = classes[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(classes)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Get number of names to generate
    while True:
        try:
            count = int(input("\nHow many names would you like to generate? (1-10): "))
            if 1 <= count <= 10:
                break
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Generate and display names
    print(f"\nGenerating {count} {selected_class.title()} names:\n")
    names = generate_full_name(selected_class, count)
    
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    
    # Ask if user wants to generate more names
    while True:
        again = input("\nGenerate more names? (y/n): ").lower()
        if again in ['y', 'yes']:
            main()  # Restart the process
            return
        elif again in ['n', 'no']:
            print("\nExiting name generator. Goodbye!")
            return
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()
