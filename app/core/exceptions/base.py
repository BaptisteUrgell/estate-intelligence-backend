class BaseApplicationException(Exception):
    def __init__(self, message: str, error_code: str):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class DomainException(BaseApplicationException):
    pass


class InfrastructureException(BaseApplicationException):
    pass
