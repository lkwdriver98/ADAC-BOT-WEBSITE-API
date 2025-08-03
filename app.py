from aiohttp import web
import json
import os
from dotenv import load_dotenv

load_dotenv()

routes = web.RouteTableDef()

@routes.get("/")
async def health(request):
    return web.Response(text="API läuft!")

@routes.get("/logs")
async def get_logs(request):
    try:
        with open("data/logs.json", "r") as f:
            logs = json.load(f)
        return web.json_response(logs)
    except FileNotFoundError:
        return web.json_response({"logs": []})

@routes.get("/users")
async def get_users(request):
    try:
        with open("data/users.json", "r") as f:
            users = json.load(f)
        return web.json_response(users)
    except FileNotFoundError:
        return web.json_response({"users": []})

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("PORT", 8080)))
