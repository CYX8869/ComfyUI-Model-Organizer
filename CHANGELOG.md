# Changelog / 更新日志

All notable changes to this project will be documented in this file.

本项目所有重要变更都将记录在此文件中。

---

## [1.1.0] - 2024-06-14 ✨ 重大功能更新

### 🎉 三大全新功能

#### 📥 【功能一】下载文件夹自动监控
- ✅ 后台守护线程实时监控指定下载目录
- ✅ 智能检测文件下载完成（大小稳定检测）
- ✅ 自动忽略临时文件（.tmp、.crdownload、.part、.download）
- ✅ 控制台实时日志提示新模型发现
- ✅ 可选"自动整理"开关（下载完成自动移动到对应目录）
- ✅ 支持自定义监控路径（默认系统下载目录）
- ✅ 一键启停监控服务

#### 🌐 【功能二】CivitAI元数据自动拉取
- ✅ 根据模型文件SHA256哈希值自动查询CivitAI
- ✅ 自动获取：模型名称、版本名称、类型、基础模型
- ✅ 自动获取：描述、标签、预览图URL、模型ID
- ✅ 自动修正识别错误的模型类型
- ✅ 本地缓存机制（7天有效期），避免重复API请求
- ✅ 失败结果也缓存，避免重复查询不存在的模型
- ✅ 友好的User-Agent标识，遵守CivitAI API规范

#### ✨ 【功能三】重复模型智能去重
- ✅ SHA256哈希精确识别完全相同的文件
- ✅ 智能算法识别相似模型（同一模型不同命名/版本）
- ✅ 文件名相似度匹配（去除版本号、日期、哈希后缀）
- ✅ 文件大小相近度分组（±2MB容差）
- ✅ 三种保留策略：最新版/最大文件/手动选择
- ✅ 🛡️ 安全删除机制：先移到回收站而非直接删除
- ✅ 回收站支持恢复和自动清理（30天自动删除）
- ✅ 删除操作完整日志记录

### 🔧 核心改进
- ✅ 新增 `requests` 依赖用于CivitAI API调用
- ✅ 新增 `threading` 多线程支持（后台监控不阻塞）
- ✅ 优化模型类型识别，新增 DoRA 支持
- ✅ 所有静态方法重构优化
- ✅ 完善的异常处理和错误日志

### 🆕 新增ComfyUI节点
| 节点名称 | 功能 |
|---------|------|
| 📥 DownloadMonitor | 下载文件夹监控 |
| 🌐 CivitAIMetadata | CivitAI元数据查询 |
| ✨ SmartDeduplicate | 智能去重 |

---

## [1.0.0] - 2024-06-14

### ✨ Added / 新增
- 🎉 Initial release of ComfyUI Model Organizer
- 🔍 **ModelScanner Node** - Scan and statistics all model files
- 📂 **ModelOrganizer Node** - Auto-organize models to correct directories
- 🔄 **DuplicateFinder Node** - Detect duplicate models using SHA256 hash
- 🧹 **EmptyDirCleaner Node** - Clean up empty model directories
- ⚡ Smart model type detection based on path and filename
- 🛡️ Dry-run preview mode for safe operation
- 💾 Caching system for improved performance
- 📝 Bilingual documentation (Chinese/English)

### 🔧 Features / 功能特性
- Supports all major model types: checkpoints, vae, loras, embeddings, controlnet, upscale_models, hypernetworks
- Automatic filename conflict resolution
- Comprehensive statistics reporting
- Cross-platform compatibility (Windows/Linux/Mac)

---

## [Unreleased] / [待发布]

### Planned Features / 计划功能
- 🎯 Model metadata extraction (preview model info)
- 🏷️ Custom tagging and categorization system
- 🔍 Model search with filtering
- 📊 Disk usage analytics dashboard
- 🔄 Batch rename functionality
- 📦 Model backup/export feature
- 🌐 Web UI interface for management

---

## Versioning / 版本说明

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version: Incompatible API changes
- **MINOR** version: Add functionality in backward compatible manner
- **PATCH** version: Backward compatible bug fixes

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)：
- **主版本号**：不兼容的 API 变更
- **次版本号**：向后兼容的功能性新增
- **修订号**：向后兼容的问题修正
