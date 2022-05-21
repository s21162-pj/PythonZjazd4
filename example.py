from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def homepage(request):
    return JSONResponse({'hello': 'world'})

async def hello(request):
    return JSONResponse({'elo': 'world'})

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/api/hello', hello)
])