import time
from typing import Any

import structlog

# Configuração do structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def log_auth_attempt(
    email: str, ip: str, success: bool, reason: str = "", endpoint: str = ""
):
    """Log structured authentication attempt"""
    logger.info(
        "auth_attempt",
        email=email,
        ip=ip,
        success=success,
        reason=reason,
        endpoint=endpoint,
        timestamp=time.time(),
    )


def log_user_operation(
    operation: str, user_id: int, success: bool, details: dict[str, Any] | None = None
):
    """Log structured user operation"""
    logger.info(
        "user_operation",
        operation=operation,
        user_id=user_id,
        success=success,
        details=details or {},
        timestamp=time.time(),
    )


def log_token_validation(
    token_valid: bool, duration: float, user_id: int | None = None
):
    """Log token validation with metrics"""
    logger.info(
        "token_validation",
        valid=token_valid,
        user_id=user_id,
        duration=duration,
        timestamp=time.time(),
    )
