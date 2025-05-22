#!/usr/bin/env bash
# Build script for PySide6 WebAssembly target
# Set up Emscripten and Qt paths and run the project generator.

set -e

# Path to Emscripten SDK
EMSDK=${EMSDK:-/path/to/emsdk}

# Path to Qt installation for WebAssembly
QT_WASM_PATH=${QT_WASM_PATH:-/path/to/Qt/wasm}
# Host Qt installation used by the build tools
QT_HOST_PATH=${QT_HOST_PATH:-/path/to/Qt/host}

# Load Emscripten environment (adds emcc to PATH)
if [ -f "$EMSDK/emsdk_env.sh" ]; then
    # shellcheck disable=SC1090
    source "$EMSDK/emsdk_env.sh"
else
    echo "emsdk_env.sh not found in $EMSDK" >&2
    exit 1
fi

# Add Qt for WebAssembly tools to PATH
export PATH="$QT_WASM_PATH/bin:$PATH"
export QT_HOST_PATH

# Generate project for WebAssembly
pyside6-project --device wasm "$@"

