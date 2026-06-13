# ComfyUI Model Organizer / ComfyUI 模型自动整理插件

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)

**自动扫描、分类、整理和去重你的 ComfyUI 模型文件**

[English](#english) | [中文](#中文)

</div>

---

## 中文

### ✨ 功能特性

- 🔍 **智能扫描** - 自动扫描所有模型文件，统计数量和大小
- 📂 **自动分类** - 根据文件名和路径自动识别模型类型
- 🔄 **一键整理** - 自动将模型移动到对应目录
- 🧹 **重复检测** - 基于文件哈希检测重复模型，释放磁盘空间
- 🗑️ **空目录清理** - 自动清理空的模型子目录
- 🛡️ **安全预览** - 支持 dry-run 预览模式，确认后再执行
- ⚡ **高性能** - 缓存机制，避免重复扫描大文件

### 🚀 安装方法

#### 方法一：Git 安装（推荐）
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yourusername/ComfyUI-Model-Organizer.git
```

#### 方法二：手动安装
1. 下载本仓库 ZIP 文件
2. 解压到 `ComfyUI/custom_nodes/` 目录
3. 重启 ComfyUI

### 📖 使用说明

安装后，在 ComfyUI 节点菜单的 `utils/model_organizer` 分类下可以找到以下节点：

#### 🔍 模型扫描器 (ModelScanner)
- 扫描所有模型文件并统计信息
- 支持递归/非递归扫描
- 输出详细的分类统计

#### 📂 模型整理器 (ModelOrganizer)
- 自动将模型移动到对应类型目录
- **默认开启 dry-run**，先预览再执行
- 自动处理文件名冲突

#### 🔄 重复模型查找 (DuplicateFinder)
- 基于 SHA256 哈希检测重复文件
- 显示可释放的磁盘空间
- 标记建议保留/删除的文件

#### 🧹 空目录清理 (EmptyDirCleaner)
- 自动发现并删除空目录
- 保持模型目录整洁

### 📁 支持的模型类型

| 类型 | 目标目录 |
|------|----------|
| 大模型 | `models/checkpoints/` |
| VAE | `models/vae/` |
| LoRA/LyCORIS | `models/loras/` |
| Embedding | `models/embeddings/` |
| ControlNet | `models/controlnet/` |
| 超分模型 | `models/upscale_models/` |
| Hypernetwork | `models/hypernetworks/` |

### ⚠️ 注意事项

1. **首次使用建议先开启 dry-run** 预览移动结果
2. 重要文件请先备份
3. 大模型库首次扫描可能需要较长时间
4. 插件不会删除任何模型文件，仅移动

---

## English

### ✨ Features

- 🔍 **Smart Scan** - Automatically scan all model files, count quantity and size
- 📂 **Auto Classification** - Auto-detect model types based on filename and path
- 🔄 **One-click Organization** - Automatically move models to corresponding directories
- 🧹 **Duplicate Detection** - Detect duplicate models based on file hash, free up disk space
- 🗑️ **Empty Directory Cleanup** - Automatically clean empty model subdirectories
- 🛡️ **Safe Preview** - Support dry-run preview mode, confirm before execution
- ⚡ **High Performance** - Caching mechanism to avoid repeated scanning of large files

### 🚀 Installation

#### Method 1: Git Installation (Recommended)
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yourusername/ComfyUI-Model-Organizer.git
```

#### Method 2: Manual Installation
1. Download the ZIP file of this repository
2. Extract to `ComfyUI/custom_nodes/` directory
3. Restart ComfyUI

### 📖 Usage

After installation, you can find the following nodes under `utils/model_organizer` category in ComfyUI:

#### 🔍 ModelScanner
- Scan all model files and statistics
- Support recursive/non-recursive scanning
- Output detailed classification statistics

#### 📂 ModelOrganizer
- Automatically move models to corresponding type directories
- **dry-run enabled by default**, preview before execution
- Auto-handle filename conflicts

#### 🔄 DuplicateFinder
- Detect duplicate files based on SHA256 hash
- Show releasable disk space
- Mark suggested keep/delete files

#### 🧹 EmptyDirCleaner
- Automatically find and delete empty directories
- Keep model directories clean

### 📁 Supported Model Types

| Type | Target Directory |
|------|------------------|
| Checkpoints | `models/checkpoints/` |
| VAE | `models/vae/` |
| LoRA/LyCORIS | `models/loras/` |
| Embedding | `models/embeddings/` |
| ControlNet | `models/controlnet/` |
| Upscale Models | `models/upscale_models/` |
| Hypernetwork | `models/hypernetworks/` |

### ⚠️ Notes

1. **Recommended to enable dry-run first** to preview move results
2. Please backup important files first
3. First scan of large model library may take a long time
4. Plugin will not delete any model files, only move

---

## 🤝 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

Issues and Pull Requests are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 许可证 / License

MIT License - see [LICENSE](LICENSE) file for details.

## 📝 更新日志 / Changelog

See [CHANGELOG.md](CHANGELOG.md)
