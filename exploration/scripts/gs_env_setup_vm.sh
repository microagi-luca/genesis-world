#!/bin/bash
# Set up Genesis on the VM: uv + py3.12 + torch (cu128, Blackwell sm_120) + genesis editable.
exec > /tmp/gs_env.log 2>&1
set -x
echo "START $(date)"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version

# clone genesis at the same commit as the Mac (v1.1.1 / 8de7e456) for a fair comparison
cd "$HOME"
[ -d genesis-world ] || git clone https://github.com/Genesis-Embodied-AI/genesis-world.git
cd genesis-world
git checkout 8de7e456 2>/dev/null || echo "checkout skipped (using main HEAD)"

# python + venv
uv python install 3.12
uv venv --python 3.12 .venv
VPY="$HOME/genesis-world/.venv/bin/python"

# PyTorch with CUDA 12.8 (Blackwell sm_120)
uv pip install --python "$VPY" torch --index-url https://download.pytorch.org/whl/cu128

# Genesis (editable, base deps)
uv pip install --python "$VPY" -e .

echo "=== versions ==="
"$VPY" -c "import torch,genesis; print('torch',torch.__version__,'cuda_avail',torch.cuda.is_available(),'cuda',torch.version.cuda); print('genesis',genesis.__version__); print('gpu', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'); print('arch_list', torch.cuda.get_arch_list())"
echo "ENV_SETUP_COMPLETE $(date)"
