#!/usr/bin/env python
import json
from pathlib import Path


def convert_group_name_to_class_name(group_name):
    parts = group_name.replace("-", " ").replace("_", " ").split()
    class_name = "".join(part.capitalize() for part in parts)
    return class_name + "RateLimit"


def get_window_notation(limit: int, window: str) -> str:
    # Converts "15m" to "15 minutes", etc., and returns "300 per 15 minutes"
    reverse_mapping = {
        "s": "seconds",
        "m": "minutes",
        "h": "hours",
        "d": "days",
    }
    if not window or len(window) < 2:
        raise ValueError(f"Invalid window notation: {window}")
    number = window[:-1]
    unit = window[-1]
    if unit not in reverse_mapping:
        raise ValueError(f"Unknown time unit: {unit}")
    try:
        int(number)
    except ValueError:
        raise ValueError(f"Invalid number in window: {number}") from None
    full_unit = reverse_mapping[unit]
    return f"{limit} per {number} {full_unit}"


def build_rate_limit_dataclass(group, limit, window):
    class_name = convert_group_name_to_class_name(group)
    template = f"""
@dataclass(frozen=True)
class {class_name}(RateLimitConfig):
    group_name: str = "{group}"
    limit: int = {limit}
    window: str = "{get_window_notation(limit, window)}"

    def __init__(self):
        raise TypeError("{class_name} class cannot be instantiated")

"""
    return template


if __name__ == "__main__":
    results = {}
    with Path("rate-limits.json").open("r") as f:
        limits_data = json.load(f)
        for entry in limits_data:
            group = entry.get("group")
            limit = entry.get("max-tokens")
            window = entry.get("window-size")
            if group not in results:
                results[group] = {"limit": limit, "window": window}

    template = """# Auto-generated rate limit dataclasses
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

    def __init__(self):
        raise TypeError("GeneralRateLimit class cannot be instantiated")


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

"""

    for k, v in results.items():
        code_snippet = build_rate_limit_dataclass(k, v["limit"], v["window"])
        template += code_snippet

    with Path("src/esipie/rate_limit_configs.py").open("w") as f:
        f.write(template)
