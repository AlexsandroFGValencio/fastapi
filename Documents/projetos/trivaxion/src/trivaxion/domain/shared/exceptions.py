class DomainException(Exception):
    pass


class ValidationError(DomainException):
    pass


class NotFoundError(DomainException):
    pass


class UnauthorizedError(DomainException):
    pass


class ForbiddenError(DomainException):
    pass


class ConflictError(DomainException):
    pass


class BusinessRuleViolation(DomainException):
    pass
