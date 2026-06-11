#!/bin/bash
# Genesis env bootstrap: uv + Python 3.12 + torch (MPS) + genesis (editable, base deps)
set -e -o pipefail
cd /Users/lucafrattini/dev/genesis

echo "=== [1/5] Install uv ==="
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
uv --version

echo "=== [2/5] Install Python 3.12 ==="
uv python install 3.12

echo "=== [3/5] Create venv (.venv) ==="
uv venv --python 3.12 .venv
VENV_PY="/Users/lucafrattini/dev/genesis/.venv/bin/python"

echo "=== [4/5] Install PyTorch (Apple Silicon / MPS) ==="
uv pip install --python "$VENV_PY" torch

echo "=== [5/5] Install Genesis (editable, base deps) ==="
uv pip install --python "$VENV_PY" -e .

echo "=== DONE: versions ==="
"$VENV_PY" -c "import torch, genesis; print('torch', torch.__version__, 'mps', torch.backends.mps.is_available()); print('genesis', genesis.__version__)"
echo "=== SETUP_COMPLETE_OK ==="
