import os
import json
from aiohttp import web
import aiohttp_cors
from datetime import datetime

routes = web.RouteTableDef()

@routes.get("/")
async def index(request):
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

    return web.json_response({"status": "ok"})

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
async def post_users(request):
    key = request.headers.get("Authorization")
    if key != os.getenv("API_KEY"):
        return web.Response(status=401, text="Unauthorized")

    new_user = await request.json()

    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []

    users.append(new_user)

    with open("data/users.json", "w") as f:
        json.dump(users, f, indent=2)

    return web.json_response({"status": "user added"})


# App erstellen
app = web.Application()
app.add_routes(routes)

# CORS aktivieren
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

# CORS auf alle Routen anwenden
for route in list(app.router.routes()):
    cors.add(route)

# App starten
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, port=port)
