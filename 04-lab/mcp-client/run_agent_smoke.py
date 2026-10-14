"""Run one real ADK -> MCP -> weather-provider turn for lab evidence."""
from __future__ import annotations

import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from weather_agent import root_agent


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="weather_lab")
    session = await runner.session_service.create_session(
        app_name="weather_lab", user_id="nguyen-van-duy", session_id="day26-smoke")
    message = types.Content(role="user", parts=[types.Part.from_text(
        text="Thời tiết hiện tại và dự báo 2 ngày tới ở Hà Nội thế nào?")])
    final_text = ""
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=message):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "function_call", None):
                    print("TOOL CALL:", part.function_call.name, dict(part.function_call.args or {}))
                if getattr(part, "function_response", None):
                    print("TOOL RESULT:", part.function_response.name)
                if getattr(part, "text", None):
                    final_text = part.text
    print("FINAL ANSWER:\n" + final_text)
    await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
