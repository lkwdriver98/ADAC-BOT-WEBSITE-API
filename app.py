import os
import json
from aiohttp import web
import aiohttp_cors
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY ist nicht gesetzt. Bitte sicherstellen, dass die .env-Datei korrekt geladen wurde.")

routes = web.RouteTableDef()

@routes.get("/")
async def index(request):
    return web.Response(text="ADAC-BOT API läuft", content_type="text/plain")

@routes.get("/users")
async def get_users(request):
    key = request.headers.get("Authorization")
    if key != API_KEY:
        return web.Response(status=401, text="Unauthorized")
    try:
        with open("data/users.json", "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                raise json.JSONDecodeError("Leere Datei", content, 0)
            users = json.loads(content)
            return web.json_response({
                "users": [{"name": k, **v} for k, v in users.items()]
            })
    except (FileNotFoundError, json.JSONDecodeError):
        return web.json_response({"users": []})

@routes.get("/logs")
async def get_logs(request):
    key = request.headers.get("Authorization")
    if key != API_KEY:
        return web.Response(status=401, text="Unauthorized")
    try:
        with open("data/logs.json", "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                raise json.JSONDecodeError("Leere Datei", content, 0)
            logs = json.loads(content)
            return web.json_response({"logs": logs})
    except (FileNotFoundError, json.JSONDecodeError):
        return web.json_response({"logs": []})

@routes.post("/users")
async def add_user(request):
    key = request.headers.get("Authorization")
    if key != API_KEY:
        return web.Response(status=401, text="Unauthorized")
    data = await request.json()
    try:
        with open("data/users.json", "r", encoding="utf-8") as f:
            content = f.read()
            users = json.loads(content) if content.strip() else {}
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    users[data["name"]] = {
        "password": data["password"],
        "role": data["role"]
    }

    os.makedirs("data", exist_ok=True)
    with open("data/users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)
    return web.json_response({"status": "success"})

@routes.post("/auth")
async def authenticate(request):
    data = await request.json()
    try:
        with open("data/users.json", "r", encoding="utf-8") as f:
            content = f.read()
            users = json.loads(content) if content.strip() else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return web.Response(status=403, text="Keine Nutzer gefunden")

    user = users.get(data.get("username"))
    if user and user["password"] == data.get("password"):
        return web.json_response({"status": "ok", "role": user["role"]})
    return web.Response(status=403, text="Ungültige Anmeldedaten")

def create_app():
    app = web.Application()
    app.add_routes(routes)

    cors = aiohttp_cors.setup(app)
    for route in list(app.router.routes()):
        cors.add(route, {
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
        })
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, port=8080)
