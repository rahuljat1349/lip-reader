#!/usr/bin/env bash
set -euo pipefail

VENDOR_DIR="vendor/av_hubert"

if [ ! -d "$VENDOR_DIR" ]; then
  echo "Cloning AV-HuBERT repository..."
  git clone --depth 1 https://github.com/facebookresearch/av_hubert.git "$VENDOR_DIR"
else
  echo "AV-HuBERT vendor directory already exists, skipping clone."
fi
