# test_log_scene.py
from tools import log_scene
import asyncio

async def test():
    result = await log_scene("Jax Varn", "Debug Test", "This is a test summary.")
    print(result)

asyncio.run(test())
