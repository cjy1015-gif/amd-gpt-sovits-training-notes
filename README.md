# GitHub 发布预览 / GitHub Publication Preview

> 这是发布前预览，不代表已经创建或公开 GitHub 仓库。
>
> This is a pre-publication preview. It does not mean that a GitHub repository has been created or made public.

## 项目名称 / Project

# AMD/ROCm TTS 完整试错排障实录

一份面向低内存设备的 GPT-SoVITS V2Pro 实验记录：总结如何在 16GB 系统内存、16GB AMD 显卡、Windows 11、WSL2 和 ROCm 环境下，构建稳定、可暂停、可续训、可验证的训练流程。

An experimental training and troubleshooting record for GPT-SoVITS V2Pro on constrained hardware. It documents how to build a stable, pauseable, resumable, and verifiable workflow with 16GB host memory, a 16GB AMD GPU, Windows 11, WSL2, and ROCm.

**本项目公开的是通用训练方法和实验记录，不公开任何商业游戏语音、台词、数据集、角色权重或训练成果文件。**

**This project publishes general training methods and experiment notes only. It does not publish commercial game voices, scripts, datasets, character weights, or trained-result files.**

## 非商业使用声明 / Non-commercial notice

**本项目仅限个人学习、研究和非商业用途。不得将本项目用于未经授权的声音复制、身份冒用、骚扰、欺诈、商业服务或任何违反法律、平台规则及第三方权利的行为。使用者必须自行确认训练数据、参考音频和输出内容拥有合法来源或明确授权。**

**For personal learning, research, and non-commercial use only. Do not use this project for unauthorized voice replication, impersonation, harassment, fraud, commercial services, or any activity that violates applicable law, platform rules, or third-party rights. Users are responsible for confirming that training data, reference audio, and generated outputs are lawfully sourced or explicitly authorized.**

## 项目范围 / Scope

本项目关注“在有限硬件上把训练跑稳”的工程问题，而不是发布某个具体人物或角色的语音模型。

This project focuses on making training reliable on constrained hardware, not on releasing a voice model for any specific person or character.

## 公开内容 / Included

- AMD ROCm 环境检查与版本记录 / AMD ROCm environment checks and version notes
- 16GB 系统内存下的数据管线优化 / Data-pipeline tuning for 16GB host memory
- FP32、batch size 1、单 GPU 的稳定训练配置 / Stable single-GPU configuration using FP32 and batch size 1
- AdamW、固定学习率和数学 SDPA 等训练取舍 / Training trade-offs such as AdamW, fixed learning rates, and mathematical SDPA
- NaN/Inf 检测、梯度裁剪和非有限梯度跳过 / NaN/Inf detection, gradient clipping, and non-finite-gradient skipping
- 精确断点续训设计 / Exact checkpoint and resume design
- 检查点有限值扫描、严格加载和实际推理验收 / Finite-value scanning, strict loading, and inference acceptance checks
- 脱敏配置模板、空白数据格式和实验日志模板 / Sanitized config templates, empty dataset schemas, and experiment-log templates
- 中英双语复现说明 / Chinese-English reproduction notes

## 不公开内容 / Excluded

- 商业游戏或其他第三方的原始语音 / Original voices from commercial games or other third parties
- 台词、字幕、转写文本和完整数据集 / Scripts, subtitles, transcripts, and complete datasets
- 角色专属 GPT、SoVITS、说话人特征或其他模型权重 / Character-specific GPT, SoVITS, speaker embeddings, or other model weights
- 训练输出、可下载音频和推理成果 / Training outputs, downloadable audio, and inference artifacts
- 本机绝对路径、账号信息、Cookie、日志中的私人信息 / Absolute local paths, account information, cookies, or private information in logs

## 硬件与软件环境 / Hardware and software

| 项目 / Item | 实测配置 / Tested configuration |
| --- | --- |
| 主机内存 / Host memory | 16GB |
| GPU | AMD Radeon RX 9070 XT, 16GB VRAM |
| 系统 / OS | Windows 11 + WSL2 Ubuntu 24.04 |
| GPU 栈 / GPU stack | ROCm / HIP |
| PyTorch | 2.12.0 + ROCm 7.14 |
| 训练精度 / Precision | FP32 |
| GPU 数量 / GPUs | Single GPU |

这些版本和结果只代表本次实测组合，不代表所有 16GB AMD 显卡都能得到相同结果。

These versions and results apply only to the tested combination and do not guarantee identical behavior on every 16GB AMD GPU.

## 核心方法 / Core method

### GPT 模块 / GPT module

- batch size 1，每批更新 / Batch size 1 with per-batch updates
- FP32 计算 / FP32 computation
- AdamW 优化器 / AdamW optimizer
- 固定的低学习率 / Fixed low learning rate
- 数学 SDPA 路径 / Mathematical SDPA path
- 真实梯度裁剪 / Actual gradient clipping
- 非有限梯度检测与跳过 / Non-finite gradient detection and skipping

### SoVITS 模块 / SoVITS module

- `num_workers=0`
- `pin_memory=false`
- 关闭预取和常驻 worker / Disable prefetching and persistent workers
- 关闭非必要 TensorBoard 和训练图片日志 / Disable unnecessary TensorBoard and training-image logging
- 禁用 DDP，保持单 GPU / Disable DDP and use one GPU
- 保存生成器、判别器、优化器、epoch、批次位置和 global step / Save generator, discriminator, optimizers, epoch, batch position, and global step

## 完整试错排障实录 / Full troubleshooting record

本项目纳入了 AMD/ROCm TTS 的完整试错排障记录，而不是只保留最终成功配置。公开版将每次故障脱敏为“现象 → 误判 → 根因 → 修改 → 验证 → 可复用经验”，不包含原始素材、模型权重或私人路径。

This project includes the complete AMD/ROCm TTS troubleshooting record rather than only the final working configuration. The public version reduces each incident to “symptom → misleading hypothesis → root cause → change → verification → reusable lesson” and excludes source assets, model weights, and private paths.

### 35 个故障条目的公开摘要 / Public summary of 35 incidents

| 阶段 / Area | 典型问题 / Typical failure | 根因与修复思路 / Root cause and repair pattern | 验证 / Verification |
| --- | --- | --- | --- |
| 环境复用 / Environment reuse | 准备重装 ROCm 或复制环境 | 先确认真实解释器、ABI、包路径和缓存；Windows/WSL 环境隔离 | 在实际项目解释器中检查 Torch、HIP 和 GPU |
| Docker GPU / Docker GPU | 容器能启动但 AMD GPU 不可用 | 容器假设 `/dev/kfd`、`/dev/dri`，而当前 WSL 设备模型不同；先做最小设备探针 | 先验证设备映射，再决定是否下载大镜像 |
| Shell 与工作目录 / Shell and cwd | WSL 解释器路径为空、启动即消失、相对路径失效 | PowerShell 提前展开变量、嵌套引号和错误 cwd；改用固定路径与脚本托管 | 直接检查解释器、cwd、`PYTHONPATH` 和服务存活 |
| 依赖边界 / Dependency boundary | TorchCodec 或 IndexTTS 拉入 NVIDIA CUDA 依赖 | 当前 wheel 路线与 ROCm 不匹配；音频 I/O 改用已有 `soundfile`，禁止污染 ROCm 环境 | 分开验证模型生成、音频保存和依赖来源 |
| GPU 初始化 / GPU initialization | `hipErrorInvalidValue` 被误判为 AMD 不支持 | 用普通张量、Parameter、单层、完整模块逐级探针，排除分配器配置和初始化路径问题 | 最小迁移探针、单条前向、端到端推理 |
| 数据与 ASR / Data and ASR | ASR 有输出但参考音频效果差、行数统计不一致 | ASR 文本需人工复核；文件行数不等于记录数，读取器可能把首行当表头 | 统计非空记录、解析成功数、训练样本数并逐项对齐 |
| GPT 数值稳定性 / GPT numerical stability | AMP、梯度累积、ScaledAdam 或低精度路径产生 NaN/Inf | 逐层缩小变量，最终采用 FP32、batch 1、AdamW、math SDPA、真实裁剪和有限值保护 | 保存后扫描全部浮点张量，严格加载并实际推理 |
| SoVITS 内存 / SoVITS memory | 系统内存达到 98%，中途无法恢复 | DDP、多进程、worker、预取、锁页和日志共同造成主内存峰值 | 单进程、worker 0、关闭预取后持续监控 RSS/WSL 内存 |
| 续训机制 / Resumability | 临时 CPU 层、空日志对象、optimizer state 在 CPU | 低内存单进程路径暴露隐藏状态；显式迁移并保持日志接口 | 中断后从下一批恢复，检查不重复计算且权重有限 |
| 模型选择 / Checkpoint selection | 最后一轮不一定最像 | 训练轮数增加可能带来拟合或音色偏移；不能只按 epoch 选择 | 对多个 checkpoint 和参考片段做客观指标与人耳盲测 |

### 可复用的排障顺序 / Reusable troubleshooting order

1. 确认当前终端是 PowerShell 还是 Bash / Confirm whether the shell is PowerShell or Bash.
2. 输出真实解释器、Python、Torch、HIP 和 GPU / Print the actual interpreter, Python, Torch, HIP, and GPU.
3. 检查工作目录、`PYTHONPATH`、端口和代理 / Check cwd, `PYTHONPATH`, ports, and proxy behavior.
4. 核对文件路径、字节数、哈希、主权重和辅助权重 / Verify paths, byte sizes, hashes, and all required weights.
5. 先查已有兼容环境和缓存，禁止依赖解析拉入 CUDA Torch / Check compatible environments and caches before installing; do not pull CUDA Torch into ROCm.
6. 按普通张量 → Parameter → 单层 → 完整模块 → 单条前向 → 端到端逐级探针 / Probe from tensor to module to end-to-end inference.
7. 把模型计算和音频 I/O 分开验收 / Validate model computation and audio I/O separately.
8. 长训练前先跑 20–100 批，检查 loss、梯度、内存和保存 / Run 20–100 batches before long training and inspect loss, gradients, memory, and saving.
9. 保存后扫描所有张量并严格加载 / Scan all tensors after saving and load the checkpoint strictly.
10. 只有有限值、加载、推理和可播放音频都通过，才宣布完成 / Declare success only after finite-value, load, inference, and playable-audio checks pass.

## 实验记录摘要 / Experiment record

本次实验验证了以下工程目标：

The experiment verified the following engineering goals:

- 训练检查点可以进行 NaN/Inf 有限值扫描 / Training checkpoints can be scanned for NaN/Inf values
- 指定 epoch 权重可以严格加载 / A specified epoch can be loaded strictly
- 训练可以在中断后从精确位置继续 / Training can resume from an exact position after interruption
- ROCm 环境能够完成端到端推理验收 / The ROCm environment can complete end-to-end inference validation
- 低内存数据管线比盲目提高 batch 更适合本机 / A low-memory data pipeline is more suitable for this machine than blindly increasing the batch size
- 早期 checkpoint 可能比最后一轮更适合作为候选，必须结合客观指标和人耳盲测 / An earlier checkpoint may be a better candidate than the final epoch; use objective metrics and blind listening

实验日志只公开脱敏后的配置、摘要指标和错误类型，不附带训练素材、音频、模型权重或可下载成果。

Only sanitized configurations, summary metrics, and error categories are published. Training sources, audio, model weights, and downloadable results are excluded.

## 推荐复现流程 / Recommended reproduction flow

1. 检查 GPU、ROCm、PyTorch、音频解码和可用内存 / Check the GPU, ROCm, PyTorch, audio decoding, and available memory
2. 使用小规模试训定位算子、NaN/Inf 和内存峰值 / Run a small trial to identify operator issues, NaN/Inf, and memory peaks
3. 使用低并发配置进行稳定性验证 / Validate stability with a low-concurrency configuration
4. 启用精确断点保存和中断恢复 / Enable exact checkpointing and interruption recovery
5. 通过有限值扫描、严格加载和实际推理三层验收 / Pass finite-value, strict-load, and real-inference checks
6. 只使用拥有版权、授权或明确许可的音频进行个人测试 / Use only audio that you own, are authorized to use, or are clearly permitted to test

## 建议仓库结构 / Suggested repository layout

```text
amd-gpt-sovits-training-notes/
├─ README.md
├─ LICENSE
├─ docs/
│  ├─ amd-rocm-guide.md
│  ├─ memory-optimization.md
│  ├─ checkpoint-resume.md
│  └─ validation.md
├─ configs/
│  ├─ gpt-example.yaml
│  └─ sovits-example.yaml
├─ scripts/
│  ├─ environment-check.sh
│  ├─ finite-check.py
│  └─ validate-load.py
├─ examples/
│  └─ README.md
├─ data/
│  └─ README.md
└─ .gitignore
```

`data/`、模型输出目录和任何音频目录默认不提交；示例配置不得包含本机路径。

`data/`, model-output directories, and audio directories must not be committed by default. Example configurations must not contain local absolute paths.

## 依赖与许可证 / Dependencies and licenses

本项目参考并适配 GPT-SoVITS 的公开训练流程。GPT-SoVITS 上游项目使用 MIT License；上游版权声明和相关第三方组件许可必须保留并单独核对：

This project references and adapts the public GPT-SoVITS training workflow. The upstream GPT-SoVITS project uses the MIT License. Preserve upstream notices and review the licenses of all third-party components separately:

- <https://github.com/RVC-Boss/GPT-SoVITS>
- <https://github.com/RVC-Boss/GPT-SoVITS/blob/main/LICENSE>
- <https://pytorch.org/> 
- <https://rocm.docs.amd.com/>

本项目的原创脚本和文档许可证待发布前最终确认；不对第三方数据、音频或模型权利作任何转授权声明。

The license for original scripts and documentation will be finalized before publication. This project grants no rights to third-party data, audio, or model artifacts.

## 已知限制 / Known limitations

- ROCm 版本、PyTorch 版本和驱动变化可能导致算子或性能差异 / ROCm, PyTorch, and driver changes may affect operators or performance
- 16GB 系统内存仍然可能因音频长度、数据管线或后台进程产生压力 / 16GB host memory may still be stressed by audio length, data loading, or background processes
- 训练成功不等于输出拥有版权或声音使用授权 / Successful training does not establish copyright ownership or voice-use authorization
- 本项目不保证训练质量、收敛速度或跨设备复现结果 / No guarantee is made about quality, convergence speed, or cross-device reproducibility

## 发布清单 / Publication checklist

- [ ] 确认仓库名称和公开状态 / Confirm repository name and public visibility
- [ ] 删除语音、台词、数据集、模型权重和训练输出 / Remove voices, scripts, datasets, model weights, and training outputs
- [ ] 删除本机路径、账号信息和私人日志 / Remove local paths, account information, and private logs
- [ ] 检查 `.gitignore` 是否覆盖数据和模型目录 / Confirm `.gitignore` covers data and model directories
- [ ] 检查上游 GPT-SoVITS 和第三方依赖许可证 / Review GPT-SoVITS and third-party dependency licenses
- [ ] 使用自有或明确授权的示例数据进行复现 / Use owned or explicitly authorized example data for reproduction
- [ ] 审核中英双语免责声明 / Review the Chinese-English disclaimers
- [ ] 确认后再创建仓库并推送 / Create and push only after approval
