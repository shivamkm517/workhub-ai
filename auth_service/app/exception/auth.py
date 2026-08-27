class InvalidRefreshTokenError(Exception):
    """Raised when a refresh token is invalid or expired."""

    pass


class InvalidPasswordResetTokenError(Exception):
    """Raised when a password reset token is invalid or expired."""

    pass


class InvalidCredentialError(Exception):
    """Raised when the supplied login credentials are invalid."""

    pass