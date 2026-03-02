#!/bin/sh
set -eu

find $1 -name '*.json' -type f -print0 |
while IFS= read -r -d '' file; do
  tmp=$(mktemp)
  jq -f tools/convert_run_eoc_selector.jq "$file" > "$tmp" && mv "$tmp" "$file"
done