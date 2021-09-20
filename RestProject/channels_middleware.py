from urllib.parse import parse_qs
from rest_framework_jwt.utils import jwt_decode_handler
from asgiref.sync import sync_to_async, async_to_sync

from accounts.models import User


class TokenAuthMiddleware:
    """
    Custom token auth middleware
    """

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Close old database connections to prevent usage of timed out connections
        # close_old_connections()

        # Get the token
        token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]
        other_username = parse_qs(scope["query_string"].decode("utf8"))["user"][0]

        # Try to authenticate the user
        # try:
        # This will automatically validate the token and raise an error if token is invalid
        # UntypedToken(token)
        # except (InvalidToken, TokenError) as e:
        # Token is invalid
        # print(e)
        # return None
        # else:
        #  Then token is valid, decode it
        decoded_data = await sync_to_async(jwt_decode_handler)(token)
        print(decoded_data)
        # Will return a dictionary like -
        # {
        #     "token_type": "access",
        #     "exp": 1568770772,
        #     "jti": "5c15e80d65b04c20ad34d77b6703251b",
        #     "user_id": 6
        # }

        # Get the user using ID
        # user = await sync_to_async(get_user_model().objects.get(id=decoded_data["user_id"]))
        # scope['user'] = user
        # Return the inner application directly and let it run everything else
        scope['user_id'] = decoded_data['user_id']
        get_user = await sync_to_async(_get_user)(other_username)
        scope['other_user'] = get_user.id
        return await self.inner(scope, receive, send)


def _get_user(username):
    return User.objects.filter(username=username)[0]
