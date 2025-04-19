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
    append_to_chat_log,
    summarize_recent_chat,
    summarize_scene_log,
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
        summarize_recent_chat,
        summarize_scene_log,
    ],
)

# Launch terminal chat
import asyncio

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

        append_to_chat_log("Jax Varn", "user", user_input)
        reply_parts = []
        async for part in ai.full_round_str(user_input):
            reply_parts.append(part)
        reply = "".join(reply_parts)
        append_to_chat_log("Jax Varn", "ai", reply)
        print(f"AI: {reply}\n")
        print("USER: ", end="", flush=True)

asyncio.run(custom_chat_loop())

