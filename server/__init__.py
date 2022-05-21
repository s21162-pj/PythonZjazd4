from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import server.api as api_routes
from starlette.routing import Mount

routes = [
    Mount("/api", routes=api_routes.routes, name="api"),
]
