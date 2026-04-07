from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class CustomAPIException(APIException):
    
    def __init__(self, detail=None, status_code=status.HTTP_400_BAD_REQUEST, default_code='error'):
        if detail is None:
            detail = _('An error occurred')
        self.detail = detail
        self.status_code = status_code
        self.default_code = default_code


class AuthenticationError(CustomAPIException):
    
    def __init__(self, detail=_('Authentication failed')):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED, 'authentication_failed')


class PermissionDeniedError(CustomAPIException):
    
    def __init__(self, detail=_('Permission denied')):
        super().__init__(detail, status.HTTP_403_FORBIDDEN, 'permission_denied')


class NotFoundError(CustomAPIException):
    
    def __init__(self, detail=_('Resource not found')):
        super().__init__(detail, status.HTTP_404_NOT_FOUND, 'not_found')


class ValidationError(CustomAPIException):
    
    def __init__(self, detail=_('Validation failed')):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST, 'validation_error')


class ConflictError(CustomAPIException):
    
    def __init__(self, detail=_('Resource already exists')):
        super().__init__(detail, status.HTTP_409_CONFLICT, 'conflict')


class RateLimitError(CustomAPIException):
    
    def __init__(self, detail=_('Rate limit exceeded')):
        super().__init__(detail, status.HTTP_429_TOO_MANY_REQUESTS, 'rate_limit_exceeded')


class ServiceUnavailableError(CustomAPIException):
    
    def __init__(self, detail=_('Service temporarily unavailable')):
        super().__init__(detail, status.HTTP_503_SERVICE_UNAVAILABLE, 'service_unavailable')
