# Qwen3.8-Flash-Next 本地推理测试与性能评测

> 🚀 **最新双卡评测报告**: [AMD ROCm 10.1.0 异构双卡 (RX 7900 XT + RX 6800 XT) 联合推理与内存频率对比报告](./dual-gpu-rocm10-benchmarks/)  
> 🎨 **双卡实测动画 (40k Tokens)**: [查看双卡生成的鹈鹕骑行 2D 动画](./dual-gpu-pelican.html) ｜ [完整模型输出 Markdown](./dual-gpu-rocm10-benchmarks/qwen3.8-flash-next-dual-gpu-output.md)  
> 🌐 **在线效果直接体验 (GitHub Pages)**: [https://snow930.github.io/qwen3.8-flash-next-test/](https://snow930.github.io/qwen3.8-flash-next-test/)  
> 🌐 **备用镜像预览 (HTMLPreview)**: [点击通过 HTMLPreview 免部署预览](https://htmlpreview.github.io/?https://github.com/snow930/qwen3.8-flash-next-test/blob/main/index.html)

本仓库记录了开源大语言模型 **Qwen3.8-Flash-Next** 在本地异构计算环境下的超长上下文长文本生成测试结果、详细性能基准指标（TTFT、Prefill、Decode TPS）以及完整的生成作品。

两次真实高负载测试均为单文件纯原生矢量动画：《**鹈鹕骑自行车 · 2D 动画**》（提示词：`创建一个 HTML，内容是 SVG 绘制一个鹈鹕骑自行车的 2D 动画，你不需要任何测试。`，纯原生 SVG + CSS + JavaScript，无外部依赖，内置二连杆逆运动学 IK 算法求解与多层视差动效）。

---

## 📊 真实长文本生成任务核心指标对比 (单卡 vs 异构双卡)

| 核心度量项 | 第一次测试：单卡 (RX 7900 XT 20GB) | 第二次测试：双卡 (7900 XT + 6800 XT) | 变化与提升 |
| :--- | :--- | :--- | :--- |
| **测试模型** | `Qwen3.8-Flash-Next (IQ3_XXS)` | `Qwen3.8-Flash-Next (IQ3_XXS)` | 混合专家 (MoE) 架构模型 |
| **计算环境** | 单卡 ROCm 6.3 驱动 | **ROCm 10.1.0 异构 Fat Binary** | 架构：`gfx1100 + gfx1030` |
| **生成 Token 数量** | **59,422 tokens** | **40,277 tokens** | 单次超长上下文密集生成 |
| **解码速率 (Decode TPS)** | **60.57 tok/s** | 🔥 **80.20 tok/s** | 🚀 **大幅提速 +32.41%！** |
| **总生成耗时** | 16分 21秒 (`981s`) | ⚡ **8分 22秒 (`502.3s`)** | 时间大幅减半 |
| **首字时间 (TTFT / Prefill)** | ~2.35s | **1.32s (`1,317 ms`)** | 极速首字开箱 |
| **MTP 投机采样接受率** | ~60% ~ 70% | 🎯 **70.47%** (`25,084 / 35,593`) | 投机解码效率大幅释放 |
| **MoE 专家显存命中率** | **85.6% ~ 90.0%** | 💎 **96.2%** (`1,046.3 万次命中`) | 专家计算绝大部分封闭在显存 |
| **辅卡 (RX 6800 XT) 算力承载** | 0% (无辅卡) | **55.4%** (`1,345.3 万次专家运算`) | 辅卡接管超过一半的专家负载 |
| **KV 缓存显存驻留率** | 99.05% ~ 99.56% | **99.93%** (3.04 亿次块读取) | 极高显存驻留率 |

---

## 🖥️ 系统硬件与运行环境配置 (System Specs)

### 1. 硬件配置
- **GPU (显卡)**: AMD Radeon RX 7900 XT (XFX 海外版)
  - 核心架构: Navi 31 (`gfx1100`)
  - 显存容量: 20 GB GDDR6
  - 总线接口: PCIe 3.0 x16 (16.0 GT/s, 实测主从传输带宽 ~13.5 GB/s)
- **CPU (处理器)**: Intel(R) Xeon(R) CPU E5-2666 v3 @ 2.90GHz
  - 架构规格: 10 核心 / 20 线程, 25MB L3 Cache
  - 指令集支持: AVX2, FMA3 (无 AVX-512)
- **主板**: 华南金牌 Huananzhi X99-TF (Intel C612 / X99 芯片组)
- **系统内存 (RAM)**: 94 GiB ~ 128 GiB DDR3/DDR4
  - 分配 ~8 GB 用于会话 KV 快照缓存 (`--conversation-cache-mib 8192`)
  - 分配 ~74 GB Pinned Host RAM 用于支持 512K 超长上下文 KV 流式存储
- **操作系统**: Ubuntu 24.04.5 LTS (Linux 内核 7.0.0-38-generic x86_64)

### 2. 软件与推理引擎栈
- **驱动与底层运行环境**: AMDGPU 内核驱动 + ROCm / HIP Engine
- **算子加速**: 针对 `gfx1100` 架构启用了 `hipBLASLt` GEMM 调优算子 (tuning 26 rows)
- **推理引擎**: Strata (`engine v0.1.41`)
- **引擎启动关键参数**:
  ```bash
  ./engine/strata --serve \
    --pack Strata-data/packs/iq3_xxs \
    --native Strata-data/models/IQ3_XXS/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_XXS-00001-of-00002.gguf \
    --ple-gguf Strata-data/models/IQ3_XXS/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_XXS-00002-of-00002.gguf \
    --expert-profile Strata/data/expert-profile.bin \
    --expert-cache auto \
    --prefill auto:32768 \
    --ple-io mmap \
    --conversation-cache-mib 8192 \
    --spec 4 \
    --spec-min-p 0.5 \
    --mtp Strata-data/mtp/rt \
    --max-context 524288 \
    --rope-scaling yarn \
    --rope-scale 2 \
    --kv int8 \
    --kv-resident 32768 \
    --vram-reserve-mib 2048
  ```

---

## 📁 仓库文件结构 (Files)

```text
qwen3.8-flash-next-test/
├── README.md                                  # 本评测报告与配置说明文件
├── qwen3.8-flash-next-iq3_xxs-pelican.html    # 带有模型权重名称的 HTML 独立动效作品
├── index.html                                 # 动效作品入口（可直接用于 GitHub Pages / 浏览器预览）
└── qwen3.8-flash-next-iq3_xxs-output.md       # 模型生成的完整原始输出（Markdown 与代码说明）
```

---

## 🎨 生成作品展示：《鹈鹕自行车 · Pelican Vélocipède》

该文件完全由 `Qwen3.8-Flash-Next` 一次性生成，为一个完整的单文件 HTML（纯 SVG + CSS + 原生 JavaScript，无外部依赖）。

### 核心亮点特性：
1. **真实二连杆逆运动学 (2-Bone IK 解算)**：
   - 髋关节、膝关节与脚踏之间通过真实几何解算求解，脚踏踩动时膝盖和大腿轨迹自然跟随，完全咬合在脚踏上。
2. **机械传动系统完全联动**：
   - 后轮、前轮、牙盘、左右曲柄以严格角速度比例同步旋转，链条上下两段采用反向 `stroke-dashoffset` 滚动。
3. **多层次动态视差与环境系统**：
   - 背景包含远山、近岸丘陵、湖面水波、芦苇灌木、公路斑点、前景杂草五层视差层。
   - 包含云层漂移、微风掠过的飞鸟翅膀振动、地面扬尘与车速流线粒子系统。
4. **丰富生物微动效与交互**：
   - 鹈鹕喉囊周期性鼓胀、随机眨眼、随风波动的平滑贝塞尔围巾。
   - 提供播放/暂停、调速（0.2× ~ 2.6×）、翘前轮（Wheelie）、站立摇车（Sprint）以及车铃涟漪交互（支持键盘快捷键）。

### 在线体验与打开方式：
1. **GitHub Pages 在线直达（推荐）**：  
   👉 [https://snow930.github.io/qwen3.8-flash-next-test/](https://snow930.github.io/qwen3.8-flash-next-test/)（已正式上线，点击即可在浏览器直接体验）
2. **指定文件直达**：  
   👉 [https://snow930.github.io/qwen3.8-flash-next-test/qwen3.8-flash-next-iq3_xxs-pelican.html](https://snow930.github.io/qwen3.8-flash-next-test/qwen3.8-flash-next-iq3_xxs-pelican.html)
3. **免部署镜像预览 (HTMLPreview)**：  
   👉 [点击通过 HTMLPreview 镜像直接打开](https://htmlpreview.github.io/?https://github.com/snow930/qwen3.8-flash-next-test/blob/main/index.html)
4. **本地离线运行**：  
   克隆或下载本仓库后，直接在浏览器中双击打开 [qwen3.8-flash-next-iq3_xxs-pelican.html](qwen3.8-flash-next-iq3_xxs-pelican.html) 或 `index.html` 即可零依赖流畅运行。
