from django.contrib.sessions.middleware import SessionMiddleware


AUTH_COOKIE_NAME = "auth"


class CookieSessionMiddleware(SessionMiddleware):
    def process_response(self, request, response):
        response = super().process_response(request, response)
        if request.user.is_authenticated:
            if AUTH_COOKIE_NAME not in request.COOKIES:
                response.set_cookie(AUTH_COOKIE_NAME, "true", httponly=False, secure=True, samesite="Lax")
        else:
            response.delete_cookie(AUTH_COOKIE_NAME)
        return response
