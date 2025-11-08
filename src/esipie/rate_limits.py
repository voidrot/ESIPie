# Auto-generated rate limit dataclasses
# Do not edit manually
from dataclasses import dataclass


@dataclass(frozen=True)
class CharLocationRateLimit:
    group_name: str = "char-location"
    limit: int = 1200
    window: str = "15m"

    def __init__(self):
        raise TypeError("CharLocationRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class FittingRateLimit:
    group_name: str = "fitting"
    limit: int = 150
    window: str = "15m"

    def __init__(self):
        raise TypeError("FittingRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class FleetRateLimit:
    group_name: str = "fleet"
    limit: int = 1800
    window: str = "15m"

    def __init__(self):
        raise TypeError("FleetRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class FactionalWarfareRateLimit:
    group_name: str = "factional-warfare"
    limit: int = 150
    window: str = "15m"

    def __init__(self):
        raise TypeError("FactionalWarfareRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class CharKillmailRateLimit:
    group_name: str = "char-killmail"
    limit: int = 30
    window: str = "15m"

    def __init__(self):
        raise TypeError("CharKillmailRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class CharNotificationRateLimit:
    group_name: str = "char-notification"
    limit: int = 15
    window: str = "15m"

    def __init__(self):
        raise TypeError("CharNotificationRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class CorpKillmailRateLimit:
    group_name: str = "corp-killmail"
    limit: int = 30
    window: str = "15m"

    def __init__(self):
        raise TypeError("CorpKillmailRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class IncursionRateLimit:
    group_name: str = "incursion"
    limit: int = 150
    window: str = "15m"

    def __init__(self):
        raise TypeError("IncursionRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class IndustryRateLimit:
    group_name: str = "industry"
    limit: int = 150
    window: str = "15m"

    def __init__(self):
        raise TypeError("IndustryRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class InsuranceRateLimit:
    group_name: str = "insurance"
    limit: int = 150
    window: str = "15m"

    def __init__(self):
        raise TypeError("InsuranceRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class KillmailRateLimit:
    group_name: str = "killmail"
    limit: int = 3600
    window: str = "15m"

    def __init__(self):
        raise TypeError("KillmailRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class SovereigntyRateLimit:
    group_name: str = "sovereignty"
    limit: int = 600
    window: str = "15m"

    def __init__(self):
        raise TypeError("SovereigntyRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class StatusRateLimit:
    group_name: str = "status"
    limit: int = 600
    window: str = "15m"

    def __init__(self):
        raise TypeError("StatusRateLimit class cannot be instantiated")


@dataclass(frozen=True)
class UiRateLimit:
    group_name: str = "ui"
    limit: int = 900
    window: str = "15m"

    def __init__(self):
        raise TypeError("UiRateLimit class cannot be instantiated")

