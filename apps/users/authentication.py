from rest_framework_simplejwt.authentication import JWTAuthentication


class SwaggerJWTAuthentication(JWTAuthentication):
    """Accept standard Bearer tokens and Swagger's raw apiKey token value."""

    def get_raw_token(self, header):
        raw_token = super().get_raw_token(header)
        if raw_token is not None:
            return raw_token

        # Swagger's OpenAPI 2 apiKey dialog may send the access token directly
        # in the Authorization header. It remains subject to normal JWT checks.
        if len(header.split()) == 1:
            return header

        return None
