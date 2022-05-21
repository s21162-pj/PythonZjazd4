from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import server.api.users.endpoints

routes= [
    Route("/register", endpoints.register, methods=["POST"]),
    Route("/login", endpoints.login, methods=["POST"]),
    Route("/refresh", endpoints.refresh, methods=["POST"])
]
