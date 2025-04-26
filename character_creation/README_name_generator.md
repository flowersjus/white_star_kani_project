# White Star Name Generator

A Markov chain-based name generator for the White Star RPG system. This tool generates character names (both first and last names) that match the style and patterns of different character classes.

## Features

- Generates first names based on character class (aristocrat, mercenary, pilot, star knight, alien brute, alien mystic, robot)
- Generates last names from a common pool of sci-fi/fantasy surnames
- Creates full names (first + last) for all character types except robots
- Uses Markov chains to learn patterns from seed names
- Ensures names are pronounceable and follow natural language patterns
- Avoids generating names too similar to existing ones
- Customizes name length based on character class
- Special handling for robot names with appropriate patterns

## Usage

### In Character Creation

The name generator is integrated into the character creation process. When creating a new character, you'll be given the option to:

1. Enter a name manually
2. Generate a name based on character class

If you choose to generate a name, you'll be presented with several options and can request more if none of the suggestions appeal to you.

### Standalone Testing

You can test the name generator without going through the character creation process by running:

```bash
python character_creation/test_name_generator.py
```

This will allow you to:
- Select a character class
- Generate multiple name suggestions
- Generate additional sets of names

## Technical Details

### Markov Chain Implementation

The name generator uses a first-order Markov chain, which means it considers one character at a time when generating the next character in a name. This works well with the limited seed data available.

For each character class, the generator:
1. Builds a model from the seed names
2. Generates new names using the probability distributions in the model
3. Validates the names for pronounceability and uniqueness
4. Ensures the names match the style of the character class

### Class-Specific Constraints

Each character class has specific length constraints to match their style:

- **Aristocrat**: 4-8 characters (longer, elegant first names)
- **Mercenary**: 3-6 characters (shorter, punchy first names)
- **Pilot**: 3-6 characters (short, easy-to-call first names)
- **Star Knight**: 4-8 characters (longer, mystical first names)
- **Alien Brute**: 4-6 characters (guttural, shorter first names)
- **Alien Mystic**: 4-7 characters (exotic, medium-length first names)
- **Robot**: Special pattern-based generation (e.g., "RX-9", "TX-88") - robots don't get last names

Last names are typically 4-8 characters and follow a sci-fi/fantasy style.

### Validation Checks

Names are validated to ensure they:
- Have at least one vowel
- Don't have too many consecutive consonants or vowels
- Are not too similar to existing names
- Meet minimum and maximum length requirements

## Extending the Generator

### Adding More Seed Names

To improve the quality of generated names, you can add more seed names to:
- `name_seed_list.txt` - For first names organized by character class
- `last_name_seeds.py` - For last names used across all character classes

The more examples provided, the better the generator will learn the patterns.

### Adjusting Parameters

You can adjust the following parameters in the code:
- `order`: The order of the Markov chain (default: 1)
- `min_length` and `max_length`: The minimum and maximum length of generated names
- `threshold`: The similarity threshold for determining if names are too similar

## Implementation Files

- `name_generator.py`: The main implementation of the Markov chain name generator
- `name_seed_list.txt`: The seed first names for each character class
- `last_name_seeds.py`: The seed last names used across all character classes
- `test_name_generator.py`: A standalone script for testing the name generator
- `run_kani.py`: Integration with the character creation process
