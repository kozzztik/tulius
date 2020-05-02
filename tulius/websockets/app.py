from aiohttp import web
from django.conf import settings

#from aiohttpdemo_polls.db import close_pg, init_pg
#from aiohttpdemo_polls.middlewares import setup_middlewares

from tulius.websockets.routes import setup_routes


async def init_app():
    app = web.Application()

    # create db connection on startup, shutdown on exit
    # app.on_startup.append(init_pg)
    # app.on_cleanup.append(close_pg)

    # setup views and routes
    setup_routes(app)

    # setup_middlewares(app)

    return app


def main():
    app = init_app()
    web.run_app(app,
                host=settings.ASYNC_SERVER['host'],
                port=settings.ASYNC_SERVER['port'])
