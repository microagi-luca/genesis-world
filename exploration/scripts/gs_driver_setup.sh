#!/bin/bash
# Install NVIDIA driver (Blackwell-capable) on Debian 12 / GCP G4 (RTX PRO 6000).
# Driver only (no full CUDA toolkit) — PyTorch cu128 wheels bundle the runtime.
exec > /tmp/gs_driver.log 2>&1
set -x
echo "START $(date)"
export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -y
sudo apt-get install -y build-essential dkms curl wget gnupg ca-certificates git \
  "linux-headers-$(uname -r)" || sudo apt-get install -y linux-headers-cloud-amd64

cd /tmp
wget -q https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update -y

# cuda-drivers = latest NVIDIA driver metapackage (open kernel modules for Blackwell).
sudo apt-get install -y cuda-drivers

echo "INSTALL_DONE $(date)"
sudo modprobe nvidia || true
nvidia-smi || echo "NVIDIA_SMI_FAILED"
echo "DRIVER_SETUP_COMPLETE $(date)"
