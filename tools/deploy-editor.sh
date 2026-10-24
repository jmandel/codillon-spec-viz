#!/bin/sh
# Build the Refined Codillon fork and deploy it into editor/, preserving the examples page.
set -e
FORK=${FORK:-$HOME/hobby/codillon-refined}
REPO=$(cd "$(dirname "$0")/.." && pwd)
OUT=${OUT:-$HOME/hobby/.agent-scratch/codalon-viz/editor-dist}
TRUNK=${TRUNK:-$HOME/hobby/.agent-scratch/codalon-viz/tool/bin/trunk}
cd "$FORK"
rm -rf "$OUT"
PATH=$HOME/.cargo/bin:$PATH RUSTFLAGS='--cfg getrandom_backend="wasm_js"' "$TRUNK" build --release --public-url /codillon-spec-viz/editor/ --dist "$OUT"
cp "$REPO/editor/EXAMPLES.md" "$OUT/EXAMPLES.md"
rm -rf "$REPO/editor" && cp -r "$OUT" "$REPO/editor" && rm -f "$REPO/editor/.trunk-lock"
echo "deployed $(git -C "$FORK" rev-parse --short HEAD) to $REPO/editor"
