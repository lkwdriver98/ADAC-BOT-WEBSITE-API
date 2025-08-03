from aiohttp import web
import json
import os
from dotenv import load_dotenv
from aiohttp_middlewares import cors_middleware

load_dotenv()

routes = web.RouteTableDef()

@routes.get("/")
async def health(request):
    return web.Response(text="API läuft!")

@routes.get("/logs")
async def get_logs(request):
    key = request.headers.get("Authorization")
    if key != os.getenv("API_KEY"):
        return web.Response(status=401, text="Unauthorized")
    try:
        with open("data/logs.json", "r") as f:
            logs = json.load(f)
        return web.json_response({"logs": logs})
    except FileNotFoundError:
        return web.json_response({"logs": []})

@routes.post("/logs")
async def post_logs(request):
    key = request.headers.get("Authorization")
    if key != os.getenv("API_KEY"):
        return web.Response(status=401, text="Unauthorized")
    data = await request.json()
    try:
        with open("data/logs.json", "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    logs.append(data)
    with open("data/logs.json", "w") as f:
        json.dump(logs, f, indent=2)
    return web.json_response({"status": "OK"})

@routes.get("/users")
async def get_users(request):
    key = request.headers.get("Authorization")
    if key != os.getenv("API_KEY"):
        return web.Response(status=401, text="Unauthorized")
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
        return web.json_response({"users": users})
    except FileNotFoundError:
        return web.json_response({"users": []})

@routes.post("/users")
async def create_user(request):
    key = request.headers.get("Authorization")
    if key != os.getenv("API_KEY"):
        return web.Response(status=401, text="Unauthorized")
    data = await request.json()
    new_user = {
        "name": data.get("name"),
        "password": data.get("password"),
        "role": data.get("role", "user")
    }
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []

    users.append(new_user)
    with open("data/users.json", "w") as f:
        json.dump(users, f, indent=2)
    return web.json_response({"status": "Benutzer hinzugefügt"})

# CORS Middleware aktivieren (für Zugriff von Website)
app = web.Application(middlewares=[
    cors_middleware(origins=["https://website-adac-bot-logs.onrender.com"])  # Für Entwicklung: erlaubt alles
])
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("PORT", 8080)))
