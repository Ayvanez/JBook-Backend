class EntityDoesNotExist(Exception):
    """Raised when entity was not found in database."""


class RequireUser(Exception):
    """Raised when user should be included in query"""
