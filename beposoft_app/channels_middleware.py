from channels.middleware import  BaseMiddleware
from rest_framework.exceptions import AuthenticationFailed
from django.db import close_old_connections
from channels.db import database_sync_to_async
from beposoft_app.tokenauthentication import JWTAuthentication


class JWTWebsocketMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_parameters = dict(qp.split("=") for qp in query_string.split("&"))
        token = query_parameters.get("token", None)
        
        if not token:
            await send({
                "type": "websocket.close",
                "code": 1000,
            })
            return
        
        authentication = JWTAuthentication() 
        try:
            user, _ = await database_sync_to_async(authentication.authenticate_websocket)(scope, token)
            scope["user"] = user
        except AuthenticationFailed as e:
            await send({
                "type": "websocket.close",
                "code": 1000,
            })
            return
        
        return await super().__call__(scope, receive, send)