"""Scan a PyTorch checkpoint for NaN/Inf tensors.

This utility is intentionally generic. It does not contain model files or
dataset paths and should be run only on a local, authorized checkpoint.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    args = parser.parse_args()

    payload = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    tensors = payload if isinstance(payload, dict) else {"checkpoint": payload}
    checked = 0
    bad: list[str] = []

    def visit(value: object, name: str) -> None:
        nonlocal checked
        if isinstance(value, torch.Tensor):
            if value.is_floating_point() or value.is_complex():
                checked += 1
                if not torch.isfinite(value).all().item():
                    bad.append(name)
        elif isinstance(value, dict):
            for key, child in value.items():
                visit(child, f"{name}.{key}")
        elif isinstance(value, (list, tuple)):
            for index, child in enumerate(value):
                visit(child, f"{name}[{index}]")

    visit(tensors, "root")
    print(f"checked_floating_tensors={checked}")
    if bad:
        print("nonfinite_tensors:")
        print("\n".join(bad))
        return 2
    print("status=finite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
