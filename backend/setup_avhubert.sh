#!/usr/bin/env bash
set -euo pipefail

VENDOR_DIR="vendor/av_hubert"

if [ ! -d "$VENDOR_DIR" ]; then
  echo "Cloning AV-HuBERT repository..."
  git clone --depth 1 https://github.com/facebookresearch/av_hubert.git "$VENDOR_DIR"
else
  echo "AV-HuBERT vendor directory already exists, skipping clone."
fi

# omegaconf<2.1 has broken PyYAML>=5.1.* spec that pip 24.1+ rejects
# Install with --no-deps and add PyYAML manually
pip install --no-deps "omegaconf>=2.0.5,<2.1"
pip install "PyYAML>=5.1"
pip install "hydra-core>=1.0.7,<1.1"

# Install fairseq from GitHub (PyPI sdist missing version.txt)
pip install git+https://github.com/facebookresearch/fairseq.git
