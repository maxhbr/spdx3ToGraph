#!/usr/bin/env nix-shell
#! nix-shell -i bash -p entr plantuml sxiv
set -euo pipefail

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "## run $0 with $@"

if [[ "$#" -ge 1 && "$1" == "--once" ]]; then
  shift

  (set -x; nix develop --command poetry run python -m spdx3_to_graph -- -v "$@")

  spdx="$1"
  puml="$spdx.puml"
  png="$spdx.png"
  if [[ -f "$puml" ]]; then
    (set -x; PLANTUML_LIMIT_SIZE=$(( 8192 * 10 )) plantuml "$puml")
  else
    echo "$puml not found"
  fi
else
  while sleep 1; do
    set -x
    cat <<EOF | entr -dr $0 --once "$@"
$(find spdx3_to_graph/ -iname '*.py')
$1
EOF
  done
fi

# if [[ ! -f "$puml" || ! -f "$png" ]]; then
#   "$0" --once "$@"
# fi

# sxiv "$png" & 
# trap 'kill $(jobs -p)' EXIT

