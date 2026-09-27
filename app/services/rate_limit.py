"""Janela deslizante por IP, atômica entre threads de um único processo.

Conta toda tentativa antes do processamento, inclusive logins válidos e bodies
inválidos. Para múltiplos workers/réplicas, substituir por contador compartilhado.
"""

import math
import threading
import time
from collections import OrderedDict, deque
from collections.abc import Callable


class LoginRateLimiter:
    def __init__(
        self, max_attempts: int, window_seconds: int,
        *, clock: Callable[[], float] = time.monotonic, max_keys: int = 10_000,
    ):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.clock = clock
        self.max_keys = max_keys
        self._lock = threading.Lock()
        self._attempts: OrderedDict[str, deque[float]] = OrderedDict()

    def consume(self, key: str) -> int:
        """Reserva uma tentativa; retorna 0 ou Retry-After em segundos."""
        with self._lock:
            now = self.clock()
            cutoff = now - self.window_seconds
            # Ordenação pela última reserva permite remover IPs expirados sem
            # percorrer todos os registros a cada request.
            while self._attempts:
                oldest = next(iter(self._attempts))
                if self._attempts[oldest][-1] > cutoff:
                    break
                self._attempts.popitem(last=False)
            bucket = self._attempts.get(key)
            if bucket is None:
                if len(self._attempts) >= self.max_keys:
                    # Não elimina buckets ativos: isso permitiria contornar o
                    # limite enchendo a tabela. Falha fechada com memória limitada.
                    return self.window_seconds
                bucket = deque()
                self._attempts[key] = bucket
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.max_attempts:
                return max(1, math.ceil(bucket[0] + self.window_seconds - now))
            bucket.append(now)
            self._attempts.move_to_end(key)
            return 0
