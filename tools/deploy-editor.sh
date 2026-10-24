#!/bin/sh
# Build the Refined Codillon fork and deploy it into editor/, preserving the examples page.
set -e
FORK=${FORK:-$HOME/hobby/codillon-refined}
REPO=$(cd "$(dirname "$0")/.." && pwd)
OUT=${OUT:-$HOME/hobby/.agent-scratch/codalon-viz/editor-dist}
DEST=${DEST:-editor}          # editor (v1, branch refined) or editor/v2 (branch proofs)
TRUNK=${TRUNK:-$HOME/hobby/.agent-scratch/codalon-viz/tool/bin/trunk}
cd "$FORK"
rm -rf "$OUT"
PATH=$HOME/.cargo/bin:$PATH RUSTFLAGS='--cfg getrandom_backend="wasm_js"' "$TRUNK" build --release --public-url /codillon-spec-viz/$DEST/ --dist "$OUT"
[ -f "$REPO/$DEST/EXAMPLES.md" ] && cp "$REPO/$DEST/EXAMPLES.md" "$OUT/EXAMPLES.md"
if [ "$DEST" = editor ]; then [ -d "$REPO/editor/v2" ] && cp -r "$REPO/editor/v2" "$OUT/v2"; fi
rm -rf "$REPO/$DEST" && mkdir -p "$(dirname "$REPO/$DEST")" && cp -r "$OUT" "$REPO/$DEST" && rm -f "$REPO/$DEST/.trunk-lock"
echo "deployed $(git -C "$FORK" rev-parse --short HEAD) ($(git -C "$FORK" branch --show-current)) to $REPO/$DEST"
