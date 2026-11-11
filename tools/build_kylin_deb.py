#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Harness - Kylin OS .deb Package Builder
跨平台 Debian 打包器：在 macOS / Linux / CI 任何系统均可生成符合银河麒麟 (Kylin OS) 标准的 .deb 安装包。
"""

import os
import sys
import time
import shutil
import tarfile
import hashlib
import argparse
from pathlib import Path

def create_ar_header(filename: str, timestamp: int, uid: int, gid: int, mode: int, size: int) -> bytes:
    """生成符合 GNU/Debian ar 格式的 60 字节文件头"""
    name_field = f"{filename:<16}".encode('ascii')[:16]
    time_field = f"{timestamp:<12}".encode('ascii')[:12]
    uid_field = f"{uid:<6}".encode('ascii')[:6]
    gid_field = f"{gid:<6}".encode('ascii')[:6]
    mode_field = f"{oct(mode)[2:]:<8}".encode('ascii')[:8]
    size_field = f"{size:<10}".encode('ascii')[:10]
    trailer = b"`\n"
    return name_field + time_field + uid_field + gid_field + mode_field + size_field + trailer

def write_ar_archive(output_path: str, members: list):
    """
    将 members 写入 .deb (ar) 归档
    members: list of (member_name, bytes_data, mode)
    """
    with open(output_path, 'wb') as f:
        # 1. 写入 ar magic
        f.write(b"!<arch>\n")
        timestamp = int(time.time())

        for name, data, mode in members:
            size = len(data)
            header = create_ar_header(name, timestamp, 0, 0, mode, size)
            f.write(header)
            f.write(data)
            # 如果文件大小为奇数，ar 规范要求追加一个换行符作为 padding
            if size % 2 != 0:
                f.write(b"\n")

def make_tar_gz(source_dir: str, file_filter=None, transform_prefix="") -> bytes:
    """将目录打包为 tar.gz 字节流，统一保留 Linux 权限"""
    import io
    bio = io.BytesIO()
    with tarfile.open(fileobj=bio, mode='w:gz', format=tarfile.GNU_FORMAT) as tar:
        for root, dirs, files in os.walk(source_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, source_dir)
                if file_filter and not file_filter(rel_path):
                    continue
                
                arcname = os.path.join(transform_prefix, rel_path) if transform_prefix else rel_path
                ti = tar.gettarinfo(full_path, arcname=arcname)
                ti.uid = 0
                ti.gid = 0
                ti.uname = "root"
                ti.gname = "root"
                
                # 保留脚本的可执行权限
                if f in ("postinst", "postrm", "prerm", "deepseek-harness") or os.access(full_path, os.X_OK):
                    ti.mode = 0o755
                else:
                    ti.mode = 0o644
                
                with open(full_path, 'rb') as content_f:
                    tar.addfile(ti, content_f)
    return bio.getvalue()

def build_deb(project_root: Path, output_deb_path: Path, arch: str = "amd64", app_source: Path = None):
    """构建面向麒麟 OS 的 .deb 安装包"""
    print(f"[*] 开始构建 DeepSeek Harness 银河麒麟安装包 [{arch}]...")
    work_dir = project_root / "build" / f"staging_{arch}"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. 准备 staging 目录结构
    opt_dir = work_dir / "data" / "opt" / "deepseek-harness"
    apps_dir = work_dir / "data" / "usr" / "share" / "applications"
    icons_dir = work_dir / "data" / "usr" / "share" / "icons" / "hicolor" / "512x512" / "apps"
    debian_dir = work_dir / "control"

    opt_dir.mkdir(parents=True, exist_ok=True)
    apps_dir.mkdir(parents=True, exist_ok=True)
    icons_dir.mkdir(parents=True, exist_ok=True)
    debian_dir.mkdir(parents=True, exist_ok=True)

    # 2. 复制控制文件并注入当前架构
    control_template = (project_root / "debian" / "control").read_text(encoding="utf-8")
    control_content = control_template.replace("ARCH_PLACEHOLDER", arch)
    (debian_dir / "control").write_text(control_content, encoding="utf-8")

    for hook in ["postinst", "prerm", "postrm"]:
        hook_path = project_root / "debian" / hook
        if hook_path.exists():
            shutil.copy2(hook_path, debian_dir / hook)

    # 3. 复制桌面入口与图标
    shutil.copy2(project_root / "assets" / "deepseek-harness.desktop", apps_dir / "deepseek-harness.desktop")
    shutil.copy2(project_root / "assets" / "icons" / "deepseek-harness.png", icons_dir / "deepseek-harness.png")

    # 4. 复制启动脚本到 /opt/deepseek-harness/bin
    (opt_dir / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(project_root / "bin" / "deepseek-harness", opt_dir / "bin" / "deepseek-harness")

    # 5. 组装应用资源包 (resources / app.asar / runtime)
    res_target = opt_dir / "resources"
    res_target.mkdir(parents=True, exist_ok=True)

    if app_source and app_source.exists():
        print(f"[*] 注入本地应用核心资产: {app_source}")
        src_res = app_source / "Contents" / "Resources"
        if (src_res / "app.asar").exists():
            shutil.copy2(src_res / "app.asar", res_target / "app.asar")
        if (src_res / "app.asar.unpacked").exists():
            shutil.copytree(src_res / "app.asar.unpacked", res_target / "app.asar.unpacked", dirs_exist_ok=True)
        if (src_res / "runtime").exists():
            shutil.copytree(src_res / "runtime", res_target / "runtime", dirs_exist_ok=True)
    else:
        # 如果没有本地全量二进制，生成轻量引导说明
        print("[!] 未指定本地 App 源码路径，生成轻量标准占位引导...")
        (res_target / "README.txt").write_text(
            "DeepSeek Harness resources directory.\n"
            "On deployment, system electron will launch app.asar placed here.\n",
            encoding="utf-8"
        )

    # 6. 计算 md5sums
    md5_lines = []
    data_dir = work_dir / "data"
    for root, _, files in os.walk(data_dir):
        for file in files:
            p = Path(root) / file
            rel_p = p.relative_to(data_dir)
            hasher = hashlib.md5()
            with open(p, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            md5_lines.append(f"{hasher.hexdigest()}  {rel_p}")
    (debian_dir / "md5sums").write_text("\n".join(md5_lines) + "\n", encoding="utf-8")

    # 7. 构建 control.tar.gz 与 data.tar.gz
    print("[*] 压缩 control 与 data 归档...")
    control_tar_gz = make_tar_gz(str(debian_dir))
    data_tar_gz = make_tar_gz(str(data_dir))

    # 8. 合成 .deb
    debian_binary = b"2.0\n"
    members = [
        ("debian-binary", debian_binary, 0o644),
        ("control.tar.gz", control_tar_gz, 0o644),
        ("data.tar.gz", data_tar_gz, 0o644),
    ]

    output_deb_path.parent.mkdir(parents=True, exist_ok=True)
    write_ar_archive(str(output_deb_path), members)

    size_mb = output_deb_path.stat().st_size / (1024 * 1024)
    print(f"[✓] 成功生成麒麟操作系统安装包: {output_deb_path} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DeepSeek Harness Kylin OS .deb Packager")
    parser.add_argument("--arch", default="amd64", choices=["amd64", "arm64", "all"], help="目标 CPU 架构")
    parser.add_argument("--app-source", default="/Applications/DeepSeek Harness.app", help="本地 macOS App 或编译产物路径")
    parser.add_argument("--output", default=None, help="输出 .deb 路径")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    app_src = Path(args.app_source) if args.app_source else None
    
    out_path = Path(args.output) if args.output else root / "dist" / f"deepseek-harness_0.2.2_{args.arch}.deb"
    build_deb(root, out_path, arch=args.arch, app_source=app_src)
