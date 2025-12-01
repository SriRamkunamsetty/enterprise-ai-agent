# run_test.py
import asyncio
from agents.supervisor import SupervisorAgent

async def main():
    sup = SupervisorAgent()
    # ask for Google (Alphabet) data for October 2025
    msg = {"task": "generate_report", "params": {"symbol": "GOOGL", "month": "2025-10"}}
    res = await sup.on_message(msg, {})
    print("RESULT:", res)

if __name__ == "__main__":
    asyncio.run(main())