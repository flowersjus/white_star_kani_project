from kani import ai_function

@ai_function()
async def test_func(name: str) -> str:
    return f"Hello, {name}!"

print("Type:", type(test_func))
print("Has name:", hasattr(test_func, "name"))
print("Function name:", getattr(test_func, "name", "Missing"))

