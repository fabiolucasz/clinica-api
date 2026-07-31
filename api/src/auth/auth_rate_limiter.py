import time

from fastapi import HTTPException, Request

# In-memory storage fallback (sem Redis)
in_memory_storage = {}


class RateLimiter:

    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window  # em segundos

    def is_allowed(self, key: str) -> bool:
        """Verifica se a requisição é permitida"""
        return self._memory_check(key)

    def _memory_check(self, key: str) -> bool:
        """Verificação usando memória local"""
        current_time = time.time()

        if key not in in_memory_storage:
            in_memory_storage[key] = []

        # Remove entradas antigas
        in_memory_storage[key] = [
            req_time
            for req_time in in_memory_storage[key]
            if current_time - req_time < self.time_window
        ]

        if len(in_memory_storage[key]) >= self.max_requests:
            return False

        in_memory_storage[key].append(current_time)
        return True


# Rate limiters específicos
login_limiter = RateLimiter(max_requests=5, time_window=60)  # 5 por minuto
signup_limiter = RateLimiter(max_requests=3, time_window=60)  # 3 por minuto


def check_rate_limit(request: Request, limiter: RateLimiter, endpoint: str):
    """Verifica rate limit e lança exceção se necessário"""
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}:{endpoint}"

    if not limiter.is_allowed(key):
        print(f"🚫 Rate limit exceeded for {client_ip} on {endpoint}")
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Please try again later.",
            headers={"Retry-After": "60"},
        )


def check_brute_force(ip: str, email: str) -> bool:
    """Verifica se há tentativas suspeitas de brute force"""
    # Em memória local, não implementamos brute force detection
    return False


def reset_failed_attempts(ip: str, email: str):
    """Reseta contador de tentativas falhas após login bem-sucedido"""
