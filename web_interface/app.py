import asyncio
import platform
import time
from datetime import datetime

import psutil
import uvicorn
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Request,
                     Response, WebSocket, status)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from bot_init import bot
from config import PASSWORD_WEB, USER_WEB

app = FastAPI()
boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

templates = Jinja2Templates(directory="web_interface/templates")

def is_authenticated(request: Request) -> bool:
    # Проверяем есть ли кука authenticated=1
    return request.cookies.get("authenticated") == "1"

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Разрешаем доступ к страницам логина без проверки
    if request.url.path in ["/login", "/login_submit", "/favicon.ico"]:
        response = await call_next(request)
        return response

    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    response = await call_next(request)
    return response

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": False})

@app.post("/login_submit", response_class=HTMLResponse)
async def login_submit(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    if username == USER_WEB and password == PASSWORD_WEB:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="authenticated", value="1", httponly=True)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": True})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("authenticated")
    return response

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_event_loop()  # это loop FastAPI
    while True:
        try:
            data = await websocket.receive_text()
            if data == "restart":
                loop_bot = bot.loop  # цикл, в котором бот был запущен

                # Завершаем бота
                await websocket.send_text("Остановка бота...")
                future_close = asyncio.run_coroutine_threadsafe(bot.close(), loop_bot)
                future_close.result()  # дождаться завершения

                # Запускаем заново
                await websocket.send_text("Запуск бота...")
                future_start = asyncio.run_coroutine_threadsafe(bot.start(bot.token), loop_bot)
                future_start.result()

                await websocket.send_text("✅ Бот перезапущен")
        except Exception as e:
            await websocket.send_text(f"❌ Ошибка: {str(e)}")
            break

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



# Пример логов (в реальности — брать из файла/базы)
LOG_STORAGE = [
    {"time": str(datetime.utcnow()), "type": "INFO", "message": "Бот запущен."},
    {"time": str(datetime.utcnow()), "type": "WARNING", "message": "Высокая задержка."},
]

@router.get("/api/logs")
async def get_logs():
    return {"logs": LOG_STORAGE[-100:]}  # последние 100 логов

@router.get("/api/users")
async def get_user_stats():
    total_members = sum(guild.member_count for guild in bot.guilds)
    return {"guilds": len(bot.guilds), "total_members": total_members}

@router.get("/api/commands")
async def get_command_usage():
    # Заменить на реальную статистику команд
    return {
        "ping": 124,
        "restart": 10,
        "help": 58,
        "ban": 5,
    }




@router.get("/api/system")
async def system_info():
    return {
        "system": platform.system(),
        "node_name": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "cpu": {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "usage_per_core": psutil.cpu_percent(percpu=True),
            "total_usage": psutil.cpu_percent()
        },
        "memory": {
            "total": round(psutil.virtual_memory().total / 1024**3, 2),  # GB
            "available": round(psutil.virtual_memory().available / 1024**3, 2),
            "used": round(psutil.virtual_memory().used / 1024**3, 2),
            "percent": psutil.virtual_memory().percent
        },
        "swap": {
            "total": round(psutil.swap_memory().total / 1024**3, 2),
            "used": round(psutil.swap_memory().used / 1024**3, 2),
            "free": round(psutil.swap_memory().free / 1024**3, 2),
            "percent": psutil.swap_memory().percent
        },
        "disk": [
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total": round(psutil.disk_usage(part.mountpoint).total / 1024**3, 2),
                "used": round(psutil.disk_usage(part.mountpoint).used / 1024**3, 2),
                "free": round(psutil.disk_usage(part.mountpoint).free / 1024**3, 2),
                "percent": psutil.disk_usage(part.mountpoint).percent
            }
            for part in psutil.disk_partitions() if part.fstype
        ],
        "boot_time": boot_time,
        "uptime_seconds": int(time.time() - psutil.boot_time()),
        "load_average": list(psutil.getloadavg()) if hasattr(psutil, "getloadavg") else []
    }

RESTART_HISTORY = []

@router.post("/api/restart")
async def restart_bot():
    RESTART_HISTORY.append(str(datetime.utcnow()))
    await bot.close()
    await bot.start(bot.token)
    return {"status": "restarting"}

@router.get("/api/restarts")
async def get_restart_history():
    return {"history": RESTART_HISTORY[-10:]}

@router.get("/api/guilds")
async def list_guilds():
    return [{"name": g.name, "id": g.id, "members": g.member_count} for g in bot.guilds]

def run_web_interface():
    uvicorn.run(app, host="127.0.0.1", port=8000)

app.include_router(router)