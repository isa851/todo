import logging
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class LoggerMixin:
    
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__module__)
        return self._logger
    
    def log_request(self, request, action=None):
        user = getattr(request, 'user', None)
        user_id = user.id if user and user.is_authenticated else 'anonymous'
        
        self.logger.info(
            f"Request: {request.method} {request.get_full_path()} "
            f"User: {user_id} IP: {self._get_client_ip(request)} "
            f"Action: {action or 'N/A'}"
        )
    
    def log_response(self, request, status_code, action=None):
        user = getattr(request, 'user', None)
        user_id = user.id if user and user.is_authenticated else 'anonymous'
        
        self.logger.info(
            f"Response: {status_code} User: {user_id} "
            f"Action: {action or 'N/A'}"
        )
    
    def log_error(self, request, error, action=None):
        user = getattr(request, 'user', None)
        user_id = user.id if user and user.is_authenticated else 'anonymous'
        
        self.logger.error(
            f"Error: {str(error)} User: {user_id} "
            f"IP: {self._get_client_ip(request)} Action: {action or 'N/A'}",
            exc_info=True
        )
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def setup_logging():
    
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
            'detailed': {
                'format': '{levelname} {asctime} {module} {funcName} {lineno:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/todo_app.log',
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5,
                'formatter': 'detailed',
            },
            'console': {
                'level': 'DEBUG' if settings.DEBUG else 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/todo_app_errors.log',
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5,
                'formatter': 'detailed',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True,
            },
            'apps': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG' if settings.DEBUG else 'INFO',
                'propagate': True,
            },
            'core': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG' if settings.DEBUG else 'INFO',
                'propagate': True,
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    }
    
    return LOGGING_CONFIG


class SecurityLogger:
    
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_login_attempt(self, username, ip_address, success=True):
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Login attempt: {username} from {ip_address} - {status}")
    
    def log_permission_denied(self, user, resource, ip_address):
        username = getattr(user, 'username', 'anonymous')
        self.logger.warning(f"Permission denied: {username} trying to access {resource} from {ip_address}")
    
    def log_suspicious_activity(self, user, activity, ip_address):
        username = getattr(user, 'username', 'anonymous')
        self.logger.warning(f"Suspicious activity: {username} - {activity} from {ip_address}")
    
    def log_rate_limit_exceeded(self, user, endpoint, ip_address):
        username = getattr(user, 'username', 'anonymous')
        self.logger.warning(f"Rate limit exceeded: {username} - {endpoint} from {ip_address}")


security_logger = SecurityLogger()
