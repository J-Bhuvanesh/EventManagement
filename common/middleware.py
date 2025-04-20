from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from common.response import APIResponse
# from common.utils import handle_exception

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Add token validation or logging here if needed
            response = await call_next(request)
            return response
        except Exception as e:
            return APIResponse.unauthorized({}, message=str(e))
