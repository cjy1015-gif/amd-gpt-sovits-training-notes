# Reproduction guide / 复现指南

## Tested target

- Windows 11 + WSL2 Ubuntu 24.04
- AMD GPU with 16GB VRAM
- 16GB host memory
- ROCm/HIP and a compatible PyTorch ROCm build
- One GPU, FP32, low-concurrency data loading

The exact versions in the experiment record are evidence for one tested stack, not a promise that every 16GB AMD card will behave identically.

## Safe workflow

1. Confirm the real Python interpreter and Torch backend.
2. Confirm the working directory and module search path.
3. Run the smallest tensor and layer migration probes.
4. Validate audio decoding and saving independently.
5. Run a short 20–100 batch trial.
6. Check loss, finite gradients, memory, and checkpoint writes.
7. Test interruption and exact resume.
8. Run the finite-value scan and strict load check.
9. Only then start a longer experiment.

Use only audio, text, and model components that you own or are explicitly authorized to use. This repository provides no dataset or model download link.
