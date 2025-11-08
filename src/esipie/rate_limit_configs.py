# Auto-generated rate limit dataclasses
# Do not edit manually
from dataclasses import dataclass


class RateLimitConfig:
    group_name: str
    limit: int
    window: str


# Unofficial default rate limit
@dataclass(frozen=True)
class GeneralRateLimit(RateLimitConfig):
    group_name: str = "general"
    limit: int = 1000
    window: str = "1000 per 15 minutes"


# Unofficial market rate limit
@dataclass(frozen=True)
class MarketRateLimit(RateLimitConfig):
    group_name: str = "market"
    limit: int = 300
    window: str = "300 per 1 minutes"

    def __init__(self):
        raise TypeError("MarketRateLimit class cannot be instantiated")


# Unofficial Character Corp rate limit
@dataclass(frozen=True)
class CharCorpRateLimit(RateLimitConfig):
    group_name: str = "char-corp"
    limit: int = 300
    window: str = "300 per 1 minutes"

    def __init__(self):
        raise TypeError("CharCorpRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class CharLocationRateLimit(RateLimitConfig):
    group_name: str = "char-location"
    limit: int = 1200
    window: str = "1200 per 15 minutes"

    def __init__(self):
        raise TypeError("CharLocationRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class FittingRateLimit(RateLimitConfig):
    group_name: str = "fitting"
    limit: int = 150
    window: str = "150 per 15 minutes"

    def __init__(self):
        raise TypeError("FittingRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class FleetRateLimit(RateLimitConfig):
    group_name: str = "fleet"
    limit: int = 1800
    window: str = "1800 per 15 minutes"

    def __init__(self):
        raise TypeError("FleetRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class FactionalWarfareRateLimit(RateLimitConfig):
    group_name: str = "factional-warfare"
    limit: int = 150
    window: str = "150 per 15 minutes"

    def __init__(self):
        raise TypeError("FactionalWarfareRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class CharKillmailRateLimit(RateLimitConfig):
    group_name: str = "char-killmail"
    limit: int = 30
    window: str = "30 per 15 minutes"

    def __init__(self):
        raise TypeError("CharKillmailRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class CharNotificationRateLimit(RateLimitConfig):
    group_name: str = "char-notification"
    limit: int = 15
    window: str = "15 per 15 minutes"

    def __init__(self):
        raise TypeError("CharNotificationRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class CorpKillmailRateLimit(RateLimitConfig):
    group_name: str = "corp-killmail"
    limit: int = 30
    window: str = "30 per 15 minutes"

    def __init__(self):
        raise TypeError("CorpKillmailRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class IncursionRateLimit(RateLimitConfig):
    group_name: str = "incursion"
    limit: int = 150
    window: str = "150 per 15 minutes"

    def __init__(self):
        raise TypeError("IncursionRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class IndustryRateLimit(RateLimitConfig):
    group_name: str = "industry"
    limit: int = 150
    window: str = "150 per 15 minutes"

    def __init__(self):
        raise TypeError("IndustryRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class InsuranceRateLimit(RateLimitConfig):
    group_name: str = "insurance"
    limit: int = 150
    window: str = "150 per 15 minutes"

    def __init__(self):
        raise TypeError("InsuranceRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class KillmailRateLimit(RateLimitConfig):
    group_name: str = "killmail"
    limit: int = 3600
    window: str = "3600 per 15 minutes"

    def __init__(self):
        raise TypeError("KillmailRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class SovereigntyRateLimit(RateLimitConfig):
    group_name: str = "sovereignty"
    limit: int = 600
    window: str = "600 per 15 minutes"

    def __init__(self):
        raise TypeError("SovereigntyRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class StatusRateLimit(RateLimitConfig):
    group_name: str = "status"
    limit: int = 600
    window: str = "600 per 15 minutes"

    def __init__(self):
        raise TypeError("StatusRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class UiRateLimit(RateLimitConfig):
    group_name: str = "ui"
    limit: int = 900
    window: str = "900 per 15 minutes"

    def __init__(self):
        raise TypeError("UiRateLimit class cannot be instantiated")
