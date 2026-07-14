#!/usr/bin/env bash
set -euo pipefail

VENDOR_DIR="vendor/av_hubert"

if [ ! -d "$VENDOR_DIR" ]; then
  echo "Cloning AV-HuBERT repository..."
  git clone --depth 1 https://github.com/facebookresearch/av_hubert.git "$VENDOR_DIR"
else
  echo "AV-HuBERT vendor directory already exists, skipping clone."
fi

# omegaconf<2.1 has broken PyYAML>=5.1.* spec rejected by pip>=24.1
# Install 2.1+ (clean spec). Install hydra-core/fairseq with --no-deps
# to bypass their <2.1 constraint on omegaconf.
pip install "numpy>=1.21.3"
pip install "antlr4-python3-runtime==4.8"
pip install "omegaconf>=2.1,<2.2"
pip install --no-deps "hydra-core>=1.0.7,<1.1"
pip install --no-deps git+https://github.com/facebookresearch/fairseq.git
