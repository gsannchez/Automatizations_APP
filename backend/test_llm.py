import asyncio
import sys
from app.core.llm_client import llm_client

async def test():
    print("Sending prompt to LLM...")
    try:
        res = await asyncio.wait_for(llm_client.generate("Say hello in JSON", json_mode=True), timeout=30.0)
        print("Response:", res)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
