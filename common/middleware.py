from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from common.config import Config
from common.response import APIResponse
import jwt

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            api_routes = request.url.path.split('/')
            print(api_routes)
            if "generate-guest-token" not in api_routes:
                token = request.headers.get("Authorization")
                if token:
                    try:
                        payload = jwt.decode(token.replace("Bearer ", ""), Config.SECRET_KEY, algorithms=["HS256"])
                        request.state.user = payload
                    except jwt.ExpiredSignatureError:
                        return APIResponse.unauthorized(message="Token expired")
                    except jwt.InvalidTokenError:
                        return APIResponse.unauthorized(message="Invalid token")
                else:
                    return APIResponse.unauthorized(message="Missing Authorization token")
            response = await call_next(request)
            return response
        except Exception as e:
            return APIResponse.unauthorized({}, message=str(e))
