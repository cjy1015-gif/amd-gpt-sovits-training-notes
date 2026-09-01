#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import platform
import sys

print(f"python={sys.executable}")
print(f"python_version={platform.python_version()}")

try:
    import torch
except ImportError:
    print("torch=missing")
    raise SystemExit(2)

print(f"torch={torch.__version__}")
print(f"cuda_available={torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"device={torch.cuda.get_device_name(0)}")
    print(f"device_count={torch.cuda.device_count()}")
PY

if command -v ffmpeg >/dev/null 2>&1; then
  ffmpeg -version | head -n 1
else
  echo "ffmpeg=missing"
fi
