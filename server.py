from aiohttp import web
from config import PORT


async def _health(request):
    return web.Response(text="OK")


async def start_server():
    web_app = web.Application()
    web_app.router.add_get("/", _health)
    web_app.router.add_get("/health", _health)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
