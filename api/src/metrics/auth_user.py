from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Contadores
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['status', 'ip', 'endpoint']
)

user_operations_total = Counter(
    'user_operations_total',
    'Total user operations',
    ['operation', 'status']
)

rate_limit_hits_total = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits',
    ['ip', 'endpoint']
)

# Histogramas
token_validation_duration = Histogram(
    'token_validation_seconds',
    'Time spent validating tokens',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint', 'status']
)

# Gauges
active_users = Gauge(
    'active_users_total',
    'Number of currently active users'
)

failed_login_attempts = Gauge(
    'failed_login_attempts',
    'Current failed login attempts in last hour'
)

class MetricsManager:
    """Gerenciador central de métricas"""
    
    @staticmethod
    def record_auth_attempt(status: str, ip: str, endpoint: str):
        """Registra tentativa de autenticação"""
        auth_attempts_total.labels(
            status=status,
            ip=ip,
            endpoint=endpoint
        ).inc()
    
    @staticmethod
    def record_user_operation(operation: str, status: str):
        """Registra operação de usuário"""
        user_operations_total.labels(
            operation=operation,
            status=status
        ).inc()
    
    @staticmethod
    def record_rate_limit_hit(ip: str, endpoint: str):
        """Registra hit de rate limit"""
        rate_limit_hits_total.labels(
            ip=ip,
            endpoint=endpoint
        ).inc()
    
    @staticmethod
    def record_token_validation_time(duration: float):
        """Registra tempo de validação de token"""
        token_validation_duration.observe(duration)
    
    @staticmethod
    def record_request_time(method: str, endpoint: str, status: str, duration: float):
        """Registra tempo de requisição"""
        request_duration.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).observe(duration)
    
    @staticmethod
    def update_active_users(count: int):
        """Atualiza contador de usuários ativos"""
        active_users.set(count)
    
    @staticmethod
    def update_failed_login_attempts(count: int):
        """Atualiza contador de tentativas falhas"""
        failed_login_attempts.set(count)

def metrics_endpoint():
    """Endpoint para expor métricas Prometheus"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )