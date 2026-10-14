# Báo cáo Lab Day 26 — MCP và Function Calling

**Học viên:** Nguyễn Văn Duy

**MSSV:** 2A202602729

**Repo:** `K4-DAY26-NguyenVanDuy-2A202602729`

## Kết quả

| Phần | Kết quả đã chạy | Bằng chứng |
|---|---|---|
| Function Calling | Gemini yêu cầu hai tool call; app tự thực thi rồi gửi kết quả lại cho model | [Ảnh 01](screenshots/01-function-calling.png) |
| MCP stdio | Client khám phá `get_weather` và gọi server cho ba thành phố | [Ảnh 02](screenshots/02-mcp-stdio.png) |
| Auth | MCP HTTP xác thực bearer token và trả kết quả tool | [Ảnh 03](screenshots/03-production.png) |
| Tool Registry | Tìm theo tag, ưu tiên tool không deprecated có version cao nhất | [Ảnh 03](screenshots/03-production.png) |
| Versioning | v1 tiếp tục hoạt động; v2 bổ sung JSON, forecast và metadata migration | [Ảnh 03](screenshots/03-production.png) |
| Weather MCP | Streamable HTTP công bố ba tool và trả dữ liệu thời tiết thật | [Ảnh 04](screenshots/04-weather-mcp.png) |
| Google ADK | Agent tự gọi hai MCP tools rồi tổng hợp trả lời | [Ảnh 05](screenshots/05-adk-agent.png) |
| Setup | Dependencies, cấu trúc agent, server và import đều đạt | [Ảnh 06](screenshots/06-setup-verification.png) |

## Những lỗi đã sửa

1. `registry_client.py` đọc `registry.json` bằng encoding mặc định CP1252 trên Windows; chuyển sang UTF-8.
2. Cổng 8000 đang được backend khác sử dụng; demo Auth hỗ trợ `MCP_AUTH_PORT` và mặc định dùng 8086.
3. Model `gemini-2.5-flash` không còn phục vụ tài khoản mới; chuyển sang `gemini-3.5-flash-lite` đang khả dụng.
4. Gemini gọi tên thành phố không dấu; Function Calling thêm alias để ánh xạ `Hanoi` và `Da Nang` vào mock data đúng.
5. `verify_setup.py` không in một phần API key ra terminal hoặc ảnh bằng chứng.

## Nguồn thời tiết

Server giữ đường gọi WeatherAPI khi có `WEATHERAPI_KEY`. Máy thực hành chưa có
khóa WeatherAPI, vì vậy lần chạy này dùng Open-Meteo làm fallback không cần khóa
để chứng minh luồng dữ liệu thật. Kết quả và provider được ghi rõ trong output;
không coi fallback là bằng chứng đã gọi WeatherAPI.

## Luồng cuối cùng

```text
Người dùng
  → Gemini trong Google ADK chọn tool
  → McpToolset gọi MCP server qua Streamable HTTP
  → MCP server gọi nguồn thời tiết thật
  → kết quả tool quay lại ADK
  → Gemini tổng hợp câu trả lời tiếng Việt
```

## Chạy lại

```powershell
# Bước 1–3
$env:PYTHONUTF8='1'
.\.venv\Scripts\python.exe .\01-function-calling\weather_function_calling.py
cd .\02-mcp-basics; ..\.venv\Scripts\python.exe weather_client.py
cd ..\03-production; ..\.venv\Scripts\python.exe registry_client.py
..\.venv\Scripts\python.exe versioned_client.py

# Bước 4–5: mở server trước
cd .\04-lab\mcp-server
$env:PORT='8085'
uv run python weather.py

# Terminal khác, đặt GOOGLE_API_KEY trong môi trường hoặc .env đã gitignore
cd .\04-lab\mcp-client
$env:MCP_SERVER_URL='http://127.0.0.1:8085/mcp'
uv run python run_agent_smoke.py
```
