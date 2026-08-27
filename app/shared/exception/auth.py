class EmailAlreadyRegisteredError(Exception):
    pass

class InvalidRefreshTokenError(Exception):
    pass

class UserNotFoundError(Exception):
    pass


class InvalidPasswordResetTokenError(Exception):
    pass

class InactiveUserError(Exception):
    pass

class InvalidCredentialError(Exception):
    pass

