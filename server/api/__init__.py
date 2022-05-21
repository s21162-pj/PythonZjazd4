from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.routing import Mount
import server.api.users as users_routes

routes = [
    Mount("/users", routes=users_routes.routes)
]
