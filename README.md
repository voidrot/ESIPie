# ESIPie
![GitHub License](https://img.shields.io/github/license/voidrot/esipie)
![PyPI Version](https://img.shields.io/pypi/v/esipie)
![Build Status](https://img.shields.io/github/actions/workflow/status/voidrot/esipie/test.yaml)



A lightweight ESI client for EVE Online, adapted from [Django-ESI](https://gitlab.com/allianceauth/django-esi) without Django dependencies. Provides response caching, dynamic operation generation, and automatic rate limit handling.

## Features

- Response caching by default
- Dynamic operation generation
- Stubbed response models (Pydantic)
- Respects ESI rate limits (error rate limit and sliding window request limit)
- Cache busting
- Optional operation and/or tag pruning

### Future Features

- Client caching

## Installation
Requires Python >= 3.11

Install via `pip`:
```bash
pip install esipie
```

Or using `uv`:
```bash
uv add esipie
```

## Quick Start

Initialize the client and make a basic ESI call:

```python
from esipie import EsiClientProvider

# Fat/Full provider
# without passing a list of tags or operation names the entire ESI spec if generated
full_provider = EsiClientProvider()

# lightweight provider for the Status operations
# by passing a list of tags the ESI spec is pruned down to just the operations 
# related to the passed tags
provider = EsiClientProvider(tags=["Status"])

# The client is a singleton and can be retrieved as many times as needed without
# needing to regenerate the client each time
client = provider.client

response = client.Status.GetStatus().result()

print(response.players)
```

## License

This project is licensed under the GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later). See [LICENSE](LICENSE) for details.

This project includes adapted code from:

- **Django-ESI** — https://gitlab.com/allianceauth/django-esi
  - Copyright (c) allianceauth
  - Licensed under GNU GENERAL PUBLIC LICENSE

