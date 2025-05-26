import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from bot_init import bot

app = FastAPI()

# Подключаем статические файлы (если будут нужны)
# app.mount("/static", StaticFiles(directory="static"), name="static")

security = HTTPBasic()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang=\"ru\">
    <head>
        <meta charset=\"UTF-8\">
        <title>Панель управления Discord-ботом</title>
        <style>
            body { font-family: sans-serif; background: #1e1e2f; color: #ffffff; margin: 0; padding: 20px; }
            h1 { color: #00bfff; }
            button { padding: 10px 20px; background-color: #00bfff; border: none; border-radius: 5px; color: white; cursor: pointer; margin: 5px; }
            button:hover { background-color: #009acd; }
            .card { background: #2e2e3e; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
            .status { font-weight: bold; }
        </style>
        <script>
            let socket;

            function connectWebSocket() {
                socket = new WebSocket("ws://" + location.host + "/ws");
                socket.onmessage = function(event) {
                    alert("\u041e\u0442\u0432\u0435\u0442 \u043e\u0442 \u0431\u043e\u0442\u0430: " + event.data);
                };
            }

            function restartBot() {
                if (!socket || socket.readyState !== WebSocket.OPEN) {
                    connectWebSocket();
                    socket.onopen = () => socket.send("restart");
                } else {
                    socket.send("restart");
                }
            }

            async function getStatus() {
                const res = await fetch("/api/status");
                const data = await res.json();
                document.getElementById("status").innerText = `\u0421\u0442\u0430\u0442\u0443\u0441: ${data.status}\n\u0413\u0438\u043b\u044c\u0434\u0438\u0438: ${data.guilds}\n\u0417\u0430\u0434\u0435\u0440\u0436\u043a\u0430: ${data.latency}`;
            }

            window.onload = getStatus;
        </script>
    </head>
    <body>
        <h1>Панель управления Discord-ботом</h1>

        <div class=\"card\">
            <h2>Статус</h2>
            <div id=\"status\" class=\"status\">Загрузка...</div>
            <button onclick=\"getStatus()\">Обновить статус</button>
        </div>

        <div class=\"card\">
            <h2>Управление</h2>
            <button onclick=\"restartBot()\">Перезапустить бота</button>
        </div>

        <div class=\"card\">
            <h2>Мониторинг</h2>
            <p>Скоро здесь будет лог событий, статистика активности и другие фишки...</p>
        </div>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if data == "restart":
            await bot.close()
            await bot.start(bot.token)
            await websocket.send_text("Бот перезапущен")

@app.get("/admin")
async def admin_panel(auth: HTTPBasicCredentials = Depends(security)):
    if auth.username != "admin" or auth.password != "secret":
        raise HTTPException(status_code=401)
    return {"message": "Admin access granted"}

router = APIRouter()

@router.get("/api/status")
async def bot_status():
    return {
        "status": "online" if bot.is_ready() else "offline",
        "guilds": len(bot.guilds),
        "latency": f"{bot.latency * 1000:.2f}ms"
    }

@router.post("/api/restart")
async def restart_bot():
    await bot.close()
    await bot.start(bot.token)
    return {"status": "restarting"}

app.include_router(router)

def run_web_interface():
    uvicorn.run(app, host="0.0.0.0", port=8000)
