#!/usr/bin/env bash
# Rebuild every model from its Blender script. Needs Blender 4.2+ on PATH, or BLENDER=/path/to/blender.
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER="${BLENDER:-blender}"
for script in art/scripts/town.py art/scripts/npcs.py art/scripts/sign.py; do
  echo "→ $script"
  "$BLENDER" -b --factory-startup -P "$script" >/dev/null
done
node art/optimize.mjs art/build/town.raw.glb public/models/town.glb
ls -lh public/models
