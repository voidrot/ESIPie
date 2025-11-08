#!/usr/bin/env bash

# jq '
# [
#   .paths as $paths
#   | $paths
#   | to_entries[]
#   | {path: .key, methods: .value}
#   | .path as $p
#   | .methods
#   | to_entries[]
#   | select(.value["x-rate-limit"] != null)
#   | {
#       rateLimit: .value["x-rate-limit"]
#     }
# ]
# ' esi-spec.json

tmpfile=$(mktemp)

wget -qO "$tmpfile" https://esi.evetech.net/meta/openapi.json\?compatibility_date\=2025-11-06

jq '
[
  .paths as $paths
  | $paths
  | to_entries[]
  | {path: .key, methods: .value}
  | .path as $p
  | .methods
  | to_entries[]
  | select(.value["x-rate-limit"] != null)
  | .value["x-rate-limit"]
]
' "$tmpfile" | tee rate-limits.json
