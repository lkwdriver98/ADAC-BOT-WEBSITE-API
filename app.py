import os
import json
from aiohttp import web
import aiohttp_cors
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
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
        with open("data/users.json", "r") as f:
            users = json.load(f)
            return web.json_response({
                "users": [{"name": k, **v} for k, v in users.items()]
            })
    except FileNotFoundError:
        return web.json_response({ "users": [] })

@routes.get("/logs")
async def get_logs(request):
    key = request.headers.get("Authorization")
    if key != API_KEY:
        return web.Response(status=401, text="Unauthorized")
    try:
        with open("data/logs.json", "r") as f:
            logs = json.load(f)
            return web.json_response({ "logs": logs })
    except FileNotFoundError:
        return web.json_response({ "logs": [] })

@routes.post("/users")
async def add_user(request):
    key = request.headers.get("Authorization")
    if key != API_KEY:
        return web.Response(status=401, text="Unauthorized")
    data = await request.json()
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

    users[data["name"]] = {
        "password": data["password"],
        "role": data["role"]
    }

    with open("data/users.json", "w") as f:
        json.dump(users, f, indent=2)
    return web.json_response({"status": "success"})

app = web.Application()
app.add_routes(routes)

# CORS aktivieren
cors = aiohttp_cors.setup(app)
for route in list(app.router.routes()):
    cors.add(route)

if __name__ == "__main__":
    web.run_app(app, port=8080)
