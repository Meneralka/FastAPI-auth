from fastapi import HTTPException, status


class BaseAuthException(HTTPException):
    def __init__(self,
                 *,
                 status_code: int,
                 detail: str | dict[str, str],
                 error_type: str = "Authorization failed",
                 ):
        super().__init__(
            detail={"status": "error",
                    "type": error_type,
                    "detail": detail},
            status_code=status_code,
        )


class ValueAlreadyExistsException(BaseAuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Value already exists"
        )


class NoIdTokenException(BaseAuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has not been identified",
        )


class InvalidTokenException(BaseAuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


class TokenUnidentifiedException(BaseAuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has not been identified",
        )


class TokenTypeException(BaseAuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token type incorrect",
        )


class TokenExpiredException(BaseAuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )


class InvalidCredentialsException(BaseAuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )


class Forbidden(BaseAuthException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token")


class NeedMorePermission(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have the necessary rights.",
        )


class SessionNotFound(BaseAuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )


class DatabaseError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Oops! Unknown error",
        )
