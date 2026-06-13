# Changelog / 更新日志

All notable changes to this project will be documented in this file.

本项目所有重要变更都将记录在此文件中。

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
