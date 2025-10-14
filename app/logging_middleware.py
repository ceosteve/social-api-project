
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging_context import user_id_context
from jose import jwt, JWTError
from app.config import settings
from venv import logger


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request:Request, call_next):
        user_id_context.set("-")

        """extract authorization headers from the request and decode it"""
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            try:
                pay_load = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = pay_load.get("user_id")
                if user_id:
                    user_id_context.set(user_id)
            except JWTError as e:
                logger.warning(f"JWT decoding failed: {str(e)}")

        """proceed to execute request and return the response"""
        try:
            response = await call_next(request)
        finally:
            user_id_context.set("-")
        return response
        
        
