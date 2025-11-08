import logging
import time
import random
from limits import RateLimitItem, parse, storage, strategies
from limits.strategies import SlidingWindowCounterRateLimiter

from esipie.config import CONFIG
from esipie.rate_limit_configs import GeneralRateLimit, RateLimitConfig

logger = logging.getLogger(__name__)

class RateLimitManager:
    def __init__(self):
        self._rate_limiters: dict[str, RateLimitOperator] = {}
        self.limit_storage = storage.RedisStorage(CONFIG.cache_redis_url)
        self.limiter: SlidingWindowCounterRateLimiter = strategies.SlidingWindowCounterRateLimiter(self.limit_storage)

    def _init_group_limit(self, group_name: str) -> None:
        if group_name in self._rate_limiters:
            logger.debug(f"Rate limiter for group '{group_name}' already initialized.")
            return
        try:
            config_class = globals()[f"{''.join(word.capitalize() for word in group_name.split('-'))}RateLimit"]
            config_instance: RateLimitConfig = config_class()
        except KeyError:
            logger.warning(
                f"Rate limit configuration for group '{group_name}' not found. Defaulting to the GeneralRateLimit."
            )
            config_instance: RateLimitConfig = GeneralRateLimit()
        rate_limit_item: RateLimitItem = parse(config_instance.window)
        self._rate_limiters[group_name] = RateLimitOperator(self.limiter, rate_limit_item, group_name)

    def get_rate_limiter(self, group_name: str) -> "RateLimitOperator":
        if group_name not in self._rate_limiters:
            self._init_group_limit(group_name)
        return self._rate_limiters[group_name]


class RateLimitOperator:
    status_2xx_cost = 2
    status_3xx_cost = 1
    status_4xx_cost = 5
    status_5xx_cost = 0

    def __init__(self, limiter: SlidingWindowCounterRateLimiter, rate_limit_item: RateLimitItem, namespace: str):
        self.limiter = limiter
        self.namespace = namespace
        self.rate_limit = rate_limit_item

    def consume_limit(self, status_code: int, user_id: str = "unauthenticated") -> None:
        if 200 <= status_code < 300:
            cost = self.status_2xx_cost
        elif 300 <= status_code < 400:
            cost = self.status_3xx_cost
        elif 400 <= status_code < 500:
            cost = self.status_4xx_cost
        elif 500 <= status_code < 600:
            cost = self.status_5xx_cost
        else:
            cost = 1  # Default cost for unexpected status codes

        self.limiter.hit(self.rate_limit, self.namespace, user_id, cost=cost)

    def check(self, user_id: str = "unauthenticated") -> bool:
        return self.limiter.test(self.rate_limit, self.namespace, user_id)

    def get_rate_limit_status(self, user_id: str = "unauthenticated"):
        window = self.limiter.get_window_stats(self.rate_limit, self.namespace, user_id)
        return {
            "limit": self.rate_limit.amount,
            "remaining": window.remaining,
            "reset_time": window.reset_time,
        }

