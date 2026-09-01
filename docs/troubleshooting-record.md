# AMD/ROCm TTS 完整试错排障实录（脱敏版）

## Purpose

This document condenses the complete private troubleshooting record into reusable public patterns. It deliberately omits all commercial-game material, speaker identities, transcripts, model weights, generated audio, absolute paths, and private logs.

本文将完整私有排障记录脱敏为可复用经验，保留“现象、误判、根因、修复、验证、经验”六个维度；商业游戏素材、说话人身份、台词、模型权重、生成音频、绝对路径和私人日志均不公开。

## Incident map

### 1. Environment and container assumptions

- **Symptom:** An existing ROCm stack appeared unavailable from a new environment.
- **Misleading hypothesis:** Reinstall ROCm or copy packages from another project.
- **Root cause:** Interpreter, ABI, OS boundary, and package search path were not yet identified.
- **Change:** Inspect the actual interpreter and reuse only compatible caches; isolate the TTS environment.
- **Verification:** Print Python, Torch, HIP, device visibility, and import paths from the runtime that will execute training.

- **Symptom:** A Docker container started but could not use the AMD GPU.
- **Misleading hypothesis:** The image or model was broken.
- **Root cause:** The Compose file assumed native Linux devices that were not present in the WSL GPU model.
- **Change:** Run a minimal device probe before downloading or building a large image; use a native WSL route when the device model does not match.
- **Verification:** Confirm device nodes, a basic tensor operation, and a one-layer migration before any large download.

- **Symptom:** A large model looked small enough by weight size or VRAM estimate but died during startup.
- **Misleading hypothesis:** The GPU lacked memory.
- **Root cause:** Conversion, masks, caches, and loader peaks exhausted WSL host memory.
- **Change:** Reduce sequence limits only as a local compatibility measure and stop when the host-memory margin remains unsafe.
- **Verification:** Monitor process RSS, WSL available memory, swap, and startup peak separately from steady-state VRAM.

### 2. Shell, path, and service failures

- PowerShell expanded variables intended for Bash, so WSL interpreter paths became empty.
- Nested quoting and Markdown escaping changed Python expressions, paths, and shell syntax.
- Bash heredocs were pasted into PowerShell and parsed as invalid redirection.
- Wrong working directories broke relative model, dictionary, module, and service paths.
- Background services disappeared when their WSL session ended.
- A local proxy produced misleading health-check errors.
- An existing service port was protected by moving TTS to a dedicated port.

**Reusable fix:** Make the shell explicit, use stable working directories, provide scripts for long commands, use absolute paths at boundaries, bypass proxies for local checks, and verify process + listening port + HTTP response.

### 3. Dependencies and audio I/O

- **Symptom:** TorchCodec or an audio save operation searched for an NVIDIA `libnvrtc` library.
- **Misleading hypothesis:** The model inference failed or CUDA had to be installed.
- **Root cause:** The selected wheel followed a CUDA-linked audio route inside a ROCm environment.
- **Change:** Keep the ROCm stack intact and use the existing `soundfile` path for reference-audio loading and WAV saving.
- **Verification:** Test waveform generation and audio serialization as separate steps.

- **Symptom:** Installing an auxiliary package prepared to download a large CUDA PyTorch build.
- **Misleading hypothesis:** Let the resolver finish because the package was needed.
- **Root cause:** A transitive dependency did not respect the project’s ROCm backend.
- **Change:** Stop resolution, use a project-specific dependency overlay, install the minimum compatible package set, and disable optional CUDA/DeepSpeed/compile paths.
- **Verification:** Confirm the installed interpreter, package origin, Torch backend, and model initialization before inference.

### 4. GPU initialization and model loading

- **Symptom:** `hipErrorInvalidValue` appeared while loading or moving a model.
- **Misleading hypothesis:** AMD was fundamentally unsupported.
- **Root cause:** An allocator setting or a particular initialization path was incompatible; later dependency errors were separate.
- **Change:** Remove unverified allocator settings and test ordinary tensors, Parameters, a single layer, a full module, and a single forward pass in sequence.
- **Verification:** Only conclude GPU incompatibility after the minimal migration ladder fails consistently.

- **Symptom:** A model file was present but initialization still failed.
- **Root cause:** Auxiliary weights or an indirect dependency were missing.
- **Change:** Verify every required file, byte count, hash, configuration, and model component independently.
- **Verification:** “Downloaded” means the complete, checksummed set is present and the intended interpreter can load it.

### 5. Data and ASR bookkeeping

- ASR output was usable as a draft but contained text errors that damaged reference conditioning.
- The number of file lines differed from the number of records because of a missing final newline.
- A training reader treated the first line as a header, so a standard-header copy was created.
- File count, non-empty record count, parsed record count, and effective training sample count were tracked separately.

**Reusable fix:** Treat automatic transcription as a prefill, require human review of reference text, preserve the original manifest, and report all four counts.

### 6. GPT numerical stability

- **Symptom:** An apparently successful multi-epoch run saved checkpoints, but every floating-point tensor contained NaN/Inf.
- **Misleading hypothesis:** The exit code, file size, or continuing loss log proved success.
- **Root causes found in sequence:** AMP, an aggressive optimizer/learning rate, gradient accumulation, ineffective clipping, low-precision matrix settings, fused attention paths, and multi-device behavior.
- **Change:** Use FP32, batch 1, per-batch updates, AdamW, fixed low learning rate, math SDPA, highest FP32 matmul precision, dropout 0, real norm clipping, non-finite detection, bad-batch skipping, and a single device.
- **Verification:** Scan every saved floating tensor, strictly load the chosen checkpoint, and run end-to-end inference.

### 7. SoVITS memory and resumability

- **Symptom:** The initial run reached roughly 98% system memory and had no recoverable mid-epoch state.
- **Misleading hypothesis:** Increase batch size to finish sooner.
- **Root cause:** DDP, workers, prefetching, pinned memory, logging, and WSL cache pressure—not simply the batch size.
- **Change:** Use a single process, batch 1, zero workers, no pinned memory, no prefetch or persistent workers, no unnecessary logs, atomic checkpoint replacement, and safe signal handling.
- **Verification:** Monitor RSS and WSL memory; stop only after the current batch finishes and the complete checkpoint pair is replaced.

Three continuation bugs were then fixed: a temporary CPU layer, a closed logger object still being called, and optimizer state tensors remaining on CPU. Resume validation confirmed the next batch and global step advanced without recomputing prior batches.

### 8. Checkpoint choice and final acceptance

The last epoch is not automatically the best epoch. Additional training can improve fit while shifting timbre or reducing objective similarity. Compare several checkpoints, reference clips, and inference settings using objective measures plus blind listening; never select a checkpoint by epoch number alone.

The final acceptance ladder is:

1. finite-value scan;
2. strict checkpoint load;
3. one controlled forward pass;
4. end-to-end inference;
5. valid, playable audio output;
6. memory and resume behavior recorded.

## Public boundary

The public repository contains only this sanitized troubleshooting logic, generic templates, and small validation utilities. It does not include copyrighted or private audio, text, datasets, speaker embeddings, character weights, training outputs, or machine-specific paths.
