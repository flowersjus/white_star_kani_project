import asyncio
from kani import Kani, chat_in_terminal
from kani.engines.openai import OpenAIEngine

# Replace with your actual OpenAI key or use an env var
api_key = "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"

engine = OpenAIEngine(api_key, model="gpt-4o")  # or gpt-4, gpt-3.5, etc.
ai = Kani(engine)

chat_in_terminal(ai)  # Launches an interactive chat session

