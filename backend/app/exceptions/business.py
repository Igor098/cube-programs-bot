class ConflictError(Exception):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message)


class NotFoundError(Exception):
    def __init__(self, message: str = "Not found"):
        super().__init__(message)


class TokenNotValidError(Exception):
    def __init__(self, message: str = "Token not valid"):
        super().__init__(message)


class TokenNotFoundError(Exception):
    def __init__(self, message: str = "Token not found"):
        super().__init__(message)


class UnauthorizedError(Exception):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message)
