#!/usr/bin/env python
import json
from pathlib import Path


def convert_group_name_to_class_name(group_name):
    parts = group_name.replace('-', ' ').replace('_', ' ').split()
    class_name = ''.join(part.capitalize() for part in parts)
    return class_name + "RateLimit"

def build_rate_limit_dataclass(group, limit, window):
    class_name = convert_group_name_to_class_name(group)
    template = f"""
@dataclass(frozen=True)
class {class_name}:
    group_name: str = "{group}"
    limit: int = {limit}
    window: str = "{window}"

    def __init__(self):
        raise TypeError("{class_name} class cannot be instantiated")

"""
    return template


if __name__ == "__main__":
    results = {}
    with Path('rate-limits.json').open('r') as f:
        limits_data = json.load(f)
        for entry in limits_data:
            group = entry.get('group')
            limit = entry.get('max-tokens')
            window = entry.get('window-size')
            if group not in results:
                results[group] = {'limit': limit, 'window': window}


    template = """# Auto-generated rate limit dataclasses
# Do not edit manually
from dataclasses import dataclass

"""

    for k, v in results.items():
        code_snippet = build_rate_limit_dataclass(k, v['limit'], v['window'])
        template += code_snippet


    with Path('src/esipie/rate_limits.py').open('w') as f:
        f.write(template)
