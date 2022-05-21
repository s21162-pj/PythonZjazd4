from starlette.responses import JSONResponse
from starlette.responses import Response
import json
import jwt
from starlette.endpoints import HTTPException
from starlette import status
from starlette.requests import Request
from datetime import timezone, datetime, timedelta
from starlette.endpoints import HTTPEndpoint
from commands import users
from exceptions import RegisterException, LoginException



async def login(request):
    try:
        request = await Request.json(request)
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="{'error' : 'wrong_data'}")
    else:
        password, login = request.get("password"), request.get("login")
        try:
            user = users.login_command(login=login, password=password)
        except LoginException as e:
            if e.args[0] == "wrong_login":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="{'error' : '%s'}" % (e.args[0]))
        token = users.generate_token(login, password, user.id)
        return Response("{'token' : %s}" % token, status_code=status.HTTP_200_OK)


async def register(request):
    try:
        request = await Request.json(request)
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="{'error' : 'wrong_data'}")
    password, login = request.get("password"), request.get("login")
    try:
        users.register_command(login=login, password=password)
    except RegisterException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="{'error' : '%s'}" % (e.args[0]))
    return Response("{}", status_code=status.HTTP_200_OK)


async def refresh(request):
    request = Request.headers.fget(request)
    payload = users.decode_token(request["token"])
    if payload:
        login, password, userID = payload["login"], payload["password"], payload["sub"]
        token = users.generate_token(login, password, userID)
        return Response("{'token' : %s}" % token, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="{}")

    