# DeepSeek Harness - 银河麒麟操作系统适配与打包套件 (Kylin OS Edition)

[![Kylin OS V10 Supported](https://img.shields.io/badge/Kylin_OS-V10_SP1%2FSP2%2FSP3-blue.svg)](https://www.kylinos.cn/)
[![openKylin Supported](https://img.shields.io/badge/openKylin-1.0%2B-cyan.svg)](https://www.openkylin.top/)
[![Arch](https://img.shields.io/badge/Arch-AMD64%20%7C%20ARM64(飞腾%2F鲲鹏)-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

本项目专门面向**银河麒麟桌面操作系统（Kylin Linux Advanced Desktop V10 / SP1 / SP2 / SP3）**与 **openKylin（开放麒麟）**，提供 **DeepSeek Harness (dsh)** 桌面智能工作台的国产化操作系统移植适配、桌面深度整合与标准化 `.deb` 打包交付体系。

---

## 🎯 麒麟操作系统专项适配特性

### 1. 银河麒麟安全中心 (KYSEC) 与内核沙箱兼容
- 银河麒麟操作系统内核默认启用了严格的安全加固策略（如限制未特权用户命名空间 `unprivileged_userns_clone=0`）。
- 本套件内置智能启动引导包装器（Launcher Wrapper），自动检测当前内核沙箱策略与权限状态，在无需用户手动干预的情况下自适应沙箱参数，彻底解决 Electron 应用在麒麟系统下的**沙箱权限拦截、启动静默闪退与白屏问题**。

### 2. 国产 CPU 架构双端全覆盖
- **ARM64 / AArch64**：全面适配信创主流芯片平台，包括**飞腾（Phytium FT-2000/4、D2000、S2500）**与**华为鲲鹏（Kunpeng 920）**。
- **AMD64 / x86_64**：适配海光（Hygon）、兆芯（Zhaoxin）以及通用 x86_64 平台。

### 3. UKUI 桌面环境原生契约
- **标准化桌面入口**：提供符合 FreeDesktop 与银河麒麟桌面规范的 `.desktop` 快捷方式，原生融入麒麟开始菜单的“开发工具 / 办公应用”分类。
- **高保真矢量与高清图标**：自动部署 512x512 高清应用图标至系统图标库（`/usr/share/icons/hicolor/`），支持 UKUI 桌面缩放自适应。
- **URL Scheme 协议注册**：自动绑定并注册 `dsh://` 协议，支持从浏览器或外部应用一键调起本地 Harness 工作台。
- **Display 协议兼容**：智能识别 UKUI 的 Wayland 与 X11 显示会话，支持 `--ozone-platform-hint=auto` 硬件加速自适应。

---

## 📦 安装指南

### 方法一：直接下载安装预编译 `.deb` 包
从本仓库的 [Releases](https://github.com/chase-xue/deepseek-harness-kylin/releases) 或本地 `dist/` 目录下载对应架构的安装包：

```bash
# 飞腾 / 鲲鹏等 ARM64 架构机器：
sudo dpkg -i deepseek-harness_0.2.2_arm64.deb

# 海光 / 兆芯 / Intel / AMD 等 x86_64 架构机器：
sudo dpkg -i deepseek-harness_0.2.2_amd64.deb

# 若提示缺少基础桌面库依赖，一键修复依赖即可：
sudo apt-get install -f -y
```

### 方法二：命令行与桌面启动
安装完成后，您可以通过以下方式启动：
1. **麒麟开始菜单**：点击左下角开始菜单 ->「所有软件」->「开发工具」->「DeepSeek Harness 智能开发工作台」。
2. **终端命令行**：在终端任意位置直接输入：
   ```bash
   deepseek-harness
   # 或简短命令别名
   dsh
   ```

---

## 🛠️ 本地构建与打包（跨平台支持）

本工程内置了纯 Python 实现的跨平台 Debian 打包引擎 `tools/build_kylin_deb.py`，**无需依赖 Linux 系统或 `dpkg-deb` 工具**，在 macOS、Linux 或 Windows 环境下均可直接打包：

### 1. 基础打包（针对指定架构）
```bash
# 构建 AMD64 安装包
python3 tools/build_kylin_deb.py --arch amd64

# 构建 ARM64 安装包 (飞腾/鲲鹏)
python3 tools/build_kylin_deb.py --arch arm64
```

### 2. 注入完整应用资产打包
若本地已安装 macOS 版或已下载解压后的应用核心资源，可直接指定 `--app-source`：
```bash
python3 tools/build_kylin_deb.py \
  --arch amd64 \
  --app-source "/Applications/DeepSeek Harness.app" \
  --output "dist/deepseek-harness_0.2.2_amd64_full.deb"
```

---

## 📂 项目目录结构

```
deepseek-harness-kylin/
├── .github/
│   └── workflows/
│       └── build-deb.yml        # GitHub Actions 自动化双架构构建流水线
├── assets/
│   ├── deepseek-harness.desktop # 银河麒麟桌面快捷方式规范文件
│   └── icons/
│       └── deepseek-harness.png # 512x512 高清应用图标
├── bin/
│   └── deepseek-harness         # 针对麒麟内核与 UKUI 优化的启动引导脚本
├── debian/
│   ├── control                  # Debian 包控制元数据（针对麒麟优化依赖）
│   ├── postinst                 # 安装后钩子：建立软链、刷新图标与桌面缓存
│   └── postrm                   # 卸载后钩子：清理软链、刷新系统状态
├── tools/
│   └── build_kylin_deb.py       # 纯 Python 跨平台 Debian 打包引擎
├── dist/                        # 产出的 .deb 安装包目录
├── README.md                    # 英文说明
└── README.zh-CN.md              # 麒麟操作系统中文适配指南
```

---

## 📄 许可证

本项目遵循 [MIT License](LICENSE)。DeepSeek Harness 原版版权归属于杭州深度求索人工智能基础技术研究有限公司。
