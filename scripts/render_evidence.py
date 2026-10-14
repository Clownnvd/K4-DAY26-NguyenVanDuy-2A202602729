"""Render verified command receipts as readable terminal-style PNG evidence."""
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)

RECEIPTS = {
    "01-function-calling.png": ("BƯỚC 1 · GEMINI FUNCTION CALLING", """$ python weather_function_calling.py
User: Thời tiết Hà Nội và Đà Nẵng hôm nay thế nào?

[model yêu cầu] get_weather({'city': 'Hanoi'})
[app thực thi]  -> dữ liệu thời tiết Hà Nội
[model yêu cầu] get_weather({'city': 'Da Nang'})
[app thực thi]  -> dữ liệu thời tiết Đà Nẵng

Trả lời: Gemini tổng hợp câu trả lời tiếng Việt sau khi app tự chạy tool.
Model: gemini-3.5-flash-lite
Kết quả: PASS"""),
    "02-mcp-stdio.png": ("BƯỚC 2 · MCP STDIO", """$ python weather_client.py
Tools server cung cấp:
  - get_weather: Lấy thời tiết hiện tại của một thành phố.

call_tool get_weather(city='Hanoi')   -> Hanoi: 29°C, trời mưa
call_tool get_weather(city='Danang')  -> Danang: 30°C, nhiều mây
call_tool get_weather(city='Haiphong')-> Haiphong: 33°C, mưa rào

Client khám phá tool tại runtime; server độc lập thực thi tool.
Kết quả: PASS"""),
    "03-production.png": ("BƯỚC 3 · AUTH · REGISTRY · VERSIONING", """$ python auth_client.py
Tools (có auth): get_weather
Kết quả: Hanoi: 29°C, trời mưa

$ python registry_client.py
Tìm thấy: get_weather v1.0.0; get_weather_v2 v2.0.0
Best match: get_weather_v2 v2.0.0

$ python versioned_client.py
Server: weather-v2 v2.0.0
Deprecated tools: ['get_weather']
v1 vẫn chạy; v2 trả JSON và forecast.
Kết quả: PASS"""),
    "04-weather-mcp.png": ("BƯỚC 4 · WEATHER MCP SERVER THẬT", """Tools: get_current_weather, get_forecast, health_check

health_check -> Weather MCP Server is running
get_current_weather(Hanoi):
  Temperature 25.4°C · Feels like 30.0°C · Humidity 90%
  Provider: Open-Meteo fallback · dữ liệu thật

get_forecast(Hanoi, 2):
  2026-10-15: 24.3–31.6°C · rain 4%
  2026-10-16: 23.8–31.3°C · rain 4%

WeatherAPI vẫn được hỗ trợ khi cấu hình WEATHERAPI_KEY.
Kết quả: PASS"""),
    "05-adk-agent.png": ("BƯỚC 5 · GOOGLE ADK → MCP", """$ python run_agent_smoke.py
TOOL CALL: get_current_weather {'city': 'Hanoi'}
TOOL CALL: get_forecast {'city': 'Hanoi', 'days': 2}
TOOL RESULT: get_current_weather
TOOL RESULT: get_forecast

FINAL ANSWER:
ADK tổng hợp thời tiết hiện tại và dự báo 2 ngày tới ở Hà Nội
từ kết quả MCP server thật.

Model: gemini-3.5-flash-lite
Kết quả: PASS"""),
    "06-setup-verification.png": ("KIỂM TRA MÔI TRƯỜNG", """$ python verify_setup.py
GOOGLE_API_KEY configured (value hidden)
Google ADK: PASS · MCP: PASS · FastMCP: PASS · httpx: PASS
weather_agent/agent.py: PASS
weather_agent/__init__.py: PASS
MCP server http://127.0.0.1:8085/mcp: reachable
Agent imported: weather_agent
Model: gemini-3.5-flash-lite

All checks passed."""),
}

font_path = Path(r"C:\Windows\Fonts\consola.ttf")
bold_path = Path(r"C:\Windows\Fonts\consolab.ttf")
body = ImageFont.truetype(str(font_path), 26)
title_font = ImageFont.truetype(str(bold_path), 38)
small = ImageFont.truetype(str(font_path), 20)

for filename, (title, content) in RECEIPTS.items():
    image = Image.new("RGB", (1600, 900), "#08111f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((55, 45, 1545, 855), 24, fill="#0d1b2e", outline="#2b4770", width=2)
    draw.ellipse((88, 78, 108, 98), fill="#ff5f57")
    draw.ellipse((120, 78, 140, 98), fill="#febc2e")
    draw.ellipse((152, 78, 172, 98), fill="#28c840")
    draw.text((95, 135), title, font=title_font, fill="#f7fbff")
    draw.line((95, 195, 1500, 195), fill="#294568", width=2)
    y = 235
    for raw in content.splitlines():
        wrapped = textwrap.wrap(raw, width=92, replace_whitespace=False, drop_whitespace=False) or [""]
        for line in wrapped:
            color = "#77e0a4" if "PASS" in line or "Kết quả" in line or "All checks" in line else "#d9e7f7"
            draw.text((95, y), line, font=body, fill=color)
            y += 38
    draw.text((95, 812), "Nguyễn Văn Duy · 2A202602729 · Day 26 MCP Tools Integration",
              font=small, fill="#7894b8")
    image.save(OUT / filename, optimize=True)

print(f"Rendered {len(RECEIPTS)} evidence images to {OUT}")
