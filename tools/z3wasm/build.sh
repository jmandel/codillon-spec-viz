#!/usr/bin/env bash
# Reproducible single-threaded (no pthreads, no SharedArrayBuffer) Z3 -> wasm build.
# Usage: ./build.sh [O2|Os] [jobs]
#   Builds build-<opt>/libz3.a and out-<opt>/{z3w.js,z3w.wasm}.
# Prereqs: cmake, ninja, git, python3. Everything else is fetched under this directory.
set -euo pipefail
OPT="${1:-Os}"
JOBS="${2:-6}"
Z3_TAG="z3-5.3.1"
EMSDK_VERSION="${EMSDK_VERSION:-latest}"   # this build used emscripten 6.0.13
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# --- sources --------------------------------------------------------------
[ -d z3-src ] || git clone --depth 1 --branch "$Z3_TAG" https://github.com/Z3Prover/z3 z3-src
if [ ! -d emsdk ]; then
  git clone --depth 1 https://github.com/emscripten-core/emsdk.git
  (cd emsdk && ./emsdk install "$EMSDK_VERSION" && ./emsdk activate "$EMSDK_VERSION")
fi
# shellcheck disable=SC1091
source emsdk/emsdk_env.sh >/dev/null 2>&1

# --- patches (none currently required; see README "Patches") ---------------
for p in "$ROOT"/patches/*.patch; do
  [ -e "$p" ] || continue
  if patch -d z3-src -p1 --dry-run -N -s < "$p" >/dev/null 2>&1; then
    echo "applying $(basename "$p")"; patch -d z3-src -p1 -N -s < "$p"
  fi
done

# --- configure + build libz3.a ---------------------------------------------
EH="-fwasm-exceptions"          # native wasm EH (legacy encoding: Chrome 95+, Firefox 100+, Safari 15.2+, Node 17+)
BUILD="build-$OPT"
emcmake cmake -G Ninja -S z3-src -B "$BUILD" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="$EH" -DCMAKE_CXX_FLAGS="$EH" \
  -DCMAKE_C_FLAGS_RELEASE="-$OPT -DNDEBUG" -DCMAKE_CXX_FLAGS_RELEASE="-$OPT -DNDEBUG" \
  -DZ3_BUILD_LIBZ3_SHARED=OFF \
  -DZ3_SINGLE_THREADED=ON \
  -DZ3_POLLING_TIMER=ON \
  -DZ3_BUILD_EXECUTABLE=OFF -DZ3_BUILD_TEST_EXECUTABLES=OFF \
  -DZ3_BUILD_PYTHON_BINDINGS=OFF -DZ3_BUILD_JAVA_BINDINGS=OFF -DZ3_BUILD_DOTNET_BINDINGS=OFF \
  -DZ3_BUILD_JULIA_BINDINGS=OFF -DZ3_BUILD_OCAML_BINDINGS=OFF -DZ3_BUILD_GO_BINDINGS=OFF \
  -DZ3_BUILD_DOCUMENTATION=OFF -DZ3_ENABLE_EXAMPLE_TARGETS=OFF \
  -DZ3_INCLUDE_GIT_HASH=OFF -DZ3_INCLUDE_GIT_DESCRIBE=OFF \
  -DZ3_LINK_TIME_OPTIMIZATION=OFF
ninja -C "$BUILD" -j"$JOBS" libz3

# --- link shim + libz3.a -> z3w.js / z3w.wasm --------------------------------
OUT="out-$OPT"
mkdir -p "$OUT"
em++ -std=c++20 "-$OPT" $EH -I z3-src/src/api \
  src/z3w_shim.cpp "$BUILD/libz3.a" \
  -o "$OUT/z3w.js" \
  -sMODULARIZE=1 -sEXPORT_ES6=1 -sEXPORT_NAME=z3wModule \
  -sENVIRONMENT=web,worker,node \
  -sALLOW_MEMORY_GROWTH=1 -sINITIAL_MEMORY=64MB -sMAXIMUM_MEMORY=4GB \
  -sSTACK_SIZE=16MB \
  -sFILESYSTEM=0 \
  -sEXPORTED_FUNCTIONS=_z3w_new,_z3w_eval,_z3w_reset,_z3w_free,_z3w_version,_malloc,_free \
  -sEXPORTED_RUNTIME_METHODS=UTF8ToString,stringToUTF8,lengthBytesUTF8 \
  --extern-post-js src/z3w_api.js
ls -l "$OUT"
