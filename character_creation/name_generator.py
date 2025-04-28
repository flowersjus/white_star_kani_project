import random
import re

# Import name lists from name_seed_list.txt and last_name_seeds.py
# These will be imported directly in the module to avoid circular imports
aristocrat_names = [
    "Alaric", "Selene", "Vorian", "Isolde", "Cadris", "Elaryn", "Tavros", "Velena", "Sorin", "Amara",
    "Vaelorn", "Seraphis", "Althira", "Vantrel", "Elowen", "Lucaryn", "Amrion", "Selvane", "Marquent",
    "Cyradyl", "Vaelith", "Aeloria", "Thalric", "Selvyn", "Caldrin", "Liraeth", "Orvane", "Eryndor",
    "Mylaren", "Vorwyn", "Sylvara", "Elyndra", "Cassivar", "Tavryn", "Zoralen", "Kysera", "Velmira",
    "Altheon", "Seranth", "Lorvyn", "Caelyth", "Vandros", "Nyvaren", "Solvyn", "Averis", "Talvorn",
    "Elvyth", "Ravelle", "Sorewyn"
]
mercenary_names = [
    "Brak", "Tov", "Jax", "Korr", "Vren", "Daxin", "Ryka", "Morn", "Drav", "Zek", "Ryn", "Vex", "Tyro",
    "Zane", "Brix", "Doss", "Kade", "Nyla", "Vorn", "Skarn", "Raxx", "Brek", "Tarn", "Vosk", "Dren",
    "Zev", "Kriv", "Lorn", "Syrn", "Karn", "Mek", "Trov", "Briv", "Dax", "Zorn", "Nesk", "Krel", "Brynn",
    "Sax", "Trix", "Vorn", "Grek", "Drox", "Zarn", "Riv", "Threx", "Bryn", "Vor", "Mesk"
]
pilot_names = [
    "Kira", "Tarin", "Zade", "Vessa", "Orin", "Sela", "Drex", "Lyra", "Kairos", "Mira", "Cassian",
    "Kylo", "Skye", "Jett", "Nox", "Vira", "Dash", "Lira", "Kato", "Raze", "Tana", "Axil", "Navi",
    "Sorn", "Vexa", "Daren", "Tyra", "Calo", "Xela", "Vonn", "Zera", "Kael", "Torin", "Nyra", "Bryn",
    "Zyra", "Vorn", "Lysa", "Drex", "Jora", "Talon", "Vrix", "Nysa", "Sava", "Pyra", "Rix", "Zayl",
    "Myra", "Tove"
]
star_knight_names = [
    "Daelen", "Veyra", "Khalon", "Seris", "Talora", "Jorvan", "Mythra", "Keren", "Vaelen", "Soraya",
    "Zaryn", "Thalyra", "Kaelen", "Solveth", "Myralis", "Velorin", "Avaris", "Torwyn", "Kyrelis",
    "Lorvath", "Sylven", "Auren", "Celyra", "Elyndor", "Tharion", "Lysera", "Ravon", "Soryn", "Azrin",
    "Vareth", "Xyrel", "Miren", "Thyron", "Khalen", "Syrith", "Avaron", "Vyrel", "Torven", "Calryn",
    "Velric", "Olyndra", "Zevryn", "Tirath", "Sarion", "Myrric", "Thalven", "Solryn", "Kylarin", "Aerith"
]
alien_brute_names = [
    "Gornak", "Vurth", "Brakka", "Zurr", "Thrak", "Drolg", "Krusk", "Mavok", "Vorlag", "Durth",
    "Groth", "Vrekk", "Brorg", "Thorg", "Zarn", "Krogg", "Vornak", "Druzz", "Grakk", "Murn",
    "Krivg", "Brog", "Darg", "Vorrg", "Skarv", "Thregg", "Murog", "Grath", "Vorgr", "Thrunn",
    "Brund", "Durng", "Zogr", "Kroth", "Mavrug", "Vrog", "Gurn", "Drath", "Bruk", "Throg",
    "Vragg", "Grorn", "Zarg", "Drog", "Vorak", "Krurg", "Brov", "Drav", "Torg"
]
alien_mystic_names = [
    "Xilra", "Sural", "Vethryn", "Nyssa", "Zylla", "Quorra", "Ythra", "Luvren", "Syrran", "Veloth",
    "Zhora", "Kyvra", "Sylak", "Thyra", "Veydra", "Ryvola", "Azveth", "Soryn", "Xylen", "Vireth",
    "Myzra", "Orlyn", "Velra", "Kyreth", "Sylora", "Thylen", "Zivra", "Qirith", "Velyn", "Tavora",
    "Rinath", "Sorvyn", "Azira", "Zhoren", "Vesryn", "Lyxra", "Xaroth", "Myrel", "Tirven", "Voryn",
    "Zyrel", "Syrith", "Qylla", "Vysra", "Orvyn", "Sylaeth", "Xavren", "Velneth", "Zyrak"
]
robot_names = [
    "RX-9", "K7-0", "SYN-4", "V3-Lon", "PX-7", "ZED-2", "MK-5", "QX-1", "TX-88", "VX-3",
    "R2-K9", "J5-V3", "T4N-X", "X3-7", "M8-4", "B2-LX", "L5-K0", "G7-PX", "D3-V0", "Z6-TR",
    "N7-4K", "V9-R8", "M3-V2", "TX-R1", "RX-13", "KX-17", "B4-5X", "PX-99", "Q7-2R", "VX-90",
    "MZ-4", "ZK-8", "DR-17", "LX-9", "SX-11", "X5-K2", "P4-L7", "V2-X0", "T3-V5", "RX-21",
    "K4-17", "NX-0", "JX-4", "VX-77", "G9-P1", "TX-41", "MK-22", "FX-6", "S3-XP"
]

# Import last names
from character_creation.last_name_seeds import last_names

def build_markov_model(names, order=1):
    """
    Build a Markov chain model from a list of names.

    Args:
        names: List of sample names
        order: The order of the Markov chain (how many characters to consider)

    Returns:
        A dictionary representing the Markov model
    """
    model = {}
    for name in names:
        name = f"^{''.join(name.split())}$"  # Add start/end markers and remove spaces
        for i in range(len(name) - order):
            key = name[i:i+order]
            next_char = name[i+order]
            if key not in model:
                model[key] = {}
            if next_char not in model[key]:
                model[key][next_char] = 0
            model[key][next_char] += 1
    return model

def is_pronounceable(name):
    """
    Check if a name is pronounceable by ensuring it has vowels and follows
    basic phonetic patterns.

    Args:
        name: The name to check

    Returns:
        True if the name is pronounceable, False otherwise
    """
    if not name:
        return False

    # Check if the name has at least one vowel
    if not any(c in 'aeiouy' for c in name.lower()):
        return False

    # Check for too many consecutive consonants (more than 3)
    consonant_count = 0
    for c in name.lower():
        if c not in 'aeiouy':
            consonant_count += 1
            if consonant_count > 3:
                return False
        else:
            consonant_count = 0

    # Check for too many consecutive vowels (more than 3)
    vowel_count = 0
    for c in name.lower():
        if c in 'aeiouy':
            vowel_count += 1
            if vowel_count > 3:
                return False
        else:
            vowel_count = 0

    return True

def generate_name(model, min_length=3, max_length=10, order=1, max_attempts=5):
    """
    Generate a name using a Markov model.

    Args:
        model: The Markov model dictionary
        min_length: Minimum name length
        max_length: Maximum name length
        order: The order of the Markov chain (should match the order used to build the model)
        max_attempts: Maximum number of attempts to generate a valid name

    Returns:
        A generated name
    """
    # Limit recursion with max_attempts
    if max_attempts <= 0:
        # Fallback to a simple random name if we can't generate a valid one
        vowels = 'aeiouy'
        consonants = 'bcdfghjklmnpqrstvwxz'
        name = random.choice(consonants).upper()

        # Generate a name with alternating consonants and vowels
        for i in range(random.randint(min_length-1, max_length-1)):
            if name[-1].lower() in vowels:
                name += random.choice(consonants)
            else:
                name += random.choice(vowels)

        return name.title()

    current = "^"  # Start marker
    name = ""

    # Try to generate a name
    attempts = 0
    while len(name) < max_length and attempts < 100:  # Prevent infinite loops
        attempts += 1
        key = current[-order:] if len(current) >= order else current
        if key not in model or "$" in key:
            break

        choices = []
        weights = []
        for next_char, count in model[key].items():
            choices.append(next_char)
            weights.append(count)

        if not choices:  # No valid next characters
            break

        next_char = random.choices(choices, weights=weights)[0]
        if next_char == "$":  # End marker
            break

        name += next_char
        current += next_char

    if len(name) < min_length or not is_pronounceable(name):
        # Try again if the name is too short or not pronounceable
        return generate_name(model, min_length, max_length, order, max_attempts - 1)

    return name.title()

def generate_robot_name():
    """
    Generate a robot name with a specific pattern of letters, numbers, and dashes.

    Returns:
        A generated robot name
    """
    patterns = [
        "XX-N", "XN-N", "XXX-N", "X-NN", "XX-NN", "XN-NN", "X-NNN",
        "VX-N", "TX-NN", "RX-N", "PX-N", "MK-N", "SYN-N", "ZED-N"
    ]
    pattern = random.choice(patterns)
    name = ""

    for char in pattern:
        if char == "X":
            name += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        elif char == "N":
            name += random.choice("0123456789")
        else:
            name += char

    return name

def is_too_similar(name, existing_names, threshold=0.8):
    """
    Check if a name is too similar to any existing name.

    Args:
        name: The name to check
        existing_names: List of existing names
        threshold: Similarity threshold (0-1)

    Returns:
        True if the name is too similar to an existing name, False otherwise
    """
    name = name.lower()
    for existing in existing_names:
        existing = existing.lower()

        # Check for exact match
        if name == existing:
            return True

        # Check for substring
        if name in existing or existing in name:
            return True

        # Check for similarity using Levenshtein distance
        if len(name) > 2 and len(existing) > 2:
            # Simple similarity check
            common_chars = sum(1 for c in name if c in existing)
            similarity = common_chars / max(len(name), len(existing))
            if similarity > threshold:
                return True

    return False

def generate_name_by_class(character_class, count=1, min_length=3, max_length=10, order=1):
    """
    Generate names appropriate for a specific character class.

    Args:
        character_class: The character class/type
        count: Number of names to generate
        min_length: Minimum name length
        max_length: Maximum name length
        order: The order of the Markov chain

    Returns:
        A list of generated names
    """
    class_name_map = {
        "aristocrat": aristocrat_names,
        "mercenary": mercenary_names,
        "pilot": pilot_names,
        "star_knight": star_knight_names,
        "alien_brute": alien_brute_names,
        "alien_mystic": alien_mystic_names,
        "robot": robot_names
    }

    # Class-specific length constraints
    class_length_map = {
        "aristocrat": (4, 8),      # Aristocrats have longer, elegant names
        "mercenary": (3, 6),       # Mercenaries have shorter, punchy names
        "pilot": (3, 6),           # Pilots have short, easy-to-call names
        "star_knight": (4, 8),     # Star Knights have longer, mystical names
        "alien_brute": (4, 6),     # Alien Brutes have guttural, shorter names
        "alien_mystic": (4, 7),    # Alien Mystics have exotic, medium-length names
        "robot": (3, 6)            # Robots have short, technical designations
    }

    character_class = character_class.lower()

    # Special case for robot names
    if character_class == "robot":
        return [generate_robot_name() for _ in range(count)]

    # For other classes, use the Markov model
    if character_class not in class_name_map:
        character_class = "human"  # Default fallback to aristocrat names

    names = class_name_map.get(character_class, aristocrat_names)
    model = build_markov_model(names, order)

    # Use class-specific length constraints if available
    if character_class in class_length_map:
        min_length, max_length = class_length_map[character_class]

    # Generate unique names
    result = []
    attempts = 0
    seed_names = class_name_map.get(character_class, [])

    while len(result) < count and attempts < count * 10:
        attempts += 1
        name = generate_name(model, min_length, max_length, order)

        # Check if the name is unique and not too similar to existing names
        if name not in result and not is_too_similar(name, result + seed_names, 0.7):
            result.append(name)

    # If we couldn't generate enough unique names, fill with fallbacks
    while len(result) < count:
        if character_class == "robot":
            name = generate_robot_name()
        else:
            vowels = 'aeiouy'
            consonants = 'bcdfghjklmnpqrstvwxz'
            name = random.choice(consonants).upper()

            # Generate a name with alternating consonants and vowels
            for i in range(random.randint(min_length-1, max_length-1)):
                if name[-1].lower() in vowels:
                    name += random.choice(consonants)
                else:
                    name += random.choice(vowels)

        if name not in result:
            result.append(name)

    return result

def generate_last_name(min_length=4, max_length=8, order=1):
    """
    Generate a last name using the Markov chain model.

    Args:
        min_length: Minimum name length
        max_length: Maximum name length
        order: The order of the Markov chain

    Returns:
        A generated last name
    """
    model = build_markov_model(last_names, order)
    return generate_name(model, min_length, max_length, order)

def generate_full_name(character_class, count=1):
    """
    Generate full names (first + last) for a character class.

    Args:
        character_class: The character class/type
        count: Number of names to generate

    Returns:
        A list of full names (first + last)
    """
    first_names = generate_name_by_class(character_class, count)
    result = []

    # For each first name, generate a last name (except for robots)
    for first_name in first_names:
        if character_class.lower() == "robot":
            # Robots don't get last names
            result.append(first_name)
        else:
            # Generate a last name and combine
            last_name = generate_last_name()
            result.append(f"{first_name} {last_name}")

    return result

def suggest_names(character_class, count=3):
    """
    Generate and display suggested names for a character class.

    Args:
        character_class: The character class/type
        count: Number of names to suggest

    Returns:
        A list of suggested names
    """
    names = generate_full_name(character_class, count)

    print(f"\nSuggested names for {character_class.title()}:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")

    return names

if __name__ == "__main__":
    # Test the name generator
    for class_name in ["aristocrat", "mercenary", "pilot", "star_knight",
                       "alien_brute", "alien_mystic", "robot"]:
        print(f"\n{class_name.title()} names:")
        for _ in range(3):
            names = generate_full_name(class_name, 3)
            print(", ".join(names))
