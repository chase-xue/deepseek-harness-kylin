# DeepSeek Harness - Kylin OS Edition

[![Kylin OS V10 Supported](https://img.shields.io/badge/Kylin_OS-V10_SP1%2FSP2%2FSP3-blue.svg)](https://www.kylinos.cn/)
[![openKylin Supported](https://img.shields.io/badge/openKylin-1.0%2B-cyan.svg)](https://www.openkylin.top/)
[![Arch](https://img.shields.io/badge/Arch-AMD64%20%7C%20ARM64-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Porting, UKUI desktop integration, and standardized `.deb` packaging suite for **DeepSeek Harness (dsh)** on **Kylin Linux Advanced Desktop V10** and **openKylin**.

For Chinese documentation, please refer to [README.zh-CN.md](README.zh-CN.md).

---

## Key Features for Kylin OS

- **KYSEC & Kernel Sandbox Compatibility**: Automatic detection and compensation for unprivileged user namespace limits, preventing blank screens or crash-on-start.
- **Dual Architecture Support**: Ready for both `arm64` (Phytium FT-2000, D2000, Kunpeng 920) and `amd64` (Hygon, Zhaoxin, x86_64).
- **UKUI Native Integration**: Standardized `.desktop` menu entries, high-DPI icons, and `dsh://` URL scheme registration.
- **Cross-Platform Builder**: Built-in Python packaging engine capable of building valid `.deb` archives on macOS, Linux, and CI without external deb tools.

---

## Installation

```bash
# On Kylin OS (AMD64 / ARM64):
sudo dpkg -i deepseek-harness_0.2.2_*.deb
sudo apt-get install -f -y
```

Launch via application menu or run:
```bash
deepseek-harness
```

---

## Build

```bash
# Build amd64 package
python3 tools/build_kylin_deb.py --arch amd64

# Build arm64 package
python3 tools/build_kylin_deb.py --arch arm64
```

---

## License

MIT License. DeepSeek Harness is developed by DeepSeek AI.
