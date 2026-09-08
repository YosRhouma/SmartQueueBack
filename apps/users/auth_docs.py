OPENAPI_AUTH_DESCRIPTION = """
SmartQueue authentication API.

1. Register: create a new account and receive a JWT access token and a refresh token.
2. Login: authenticate with username and password and receive both JWT tokens.
3. Refresh: exchange a valid refresh token for a new access token.
4. Logout: blacklist the provided refresh token so it cannot be used again.
5. Me: return the current authenticated user's profile data.

Authentication model:
- Use Authorization: Bearer <access_token> for protected endpoints such as /api/auth/me/ and /api/auth/logout/.
- The refresh token belongs in the request body for logout and refresh.
- For security, refresh tokens need the token blacklist extension in SimpleJWT.
"""
