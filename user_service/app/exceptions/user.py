class EmailAlreadyRegisteredError(Exception):
    """Raised when an email is already registered."""

    pass


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""

    pass


class InactiveUserError(Exception):
    """Raised when a user account is inactive."""

    pass