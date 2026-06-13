# v1.1.0 升级指南 / Upgrade Guide

[中文](#中文) | [English](#english)

---

## 中文

## 🚀 v1.1.0 重大更新

本次更新新增 **三大核心功能**，插件能力大幅提升！

---

### 📋 升级步骤

#### 方法一：全新安装（推荐）
1. 删除旧版本插件文件夹
2. 下载 v1.1.0 压缩包
3. 解压到 `ComfyUI/custom_nodes/`
4. 重启 ComfyUI

#### 方法二：覆盖升级
1. 直接覆盖所有文件
2. 删除 `__pycache__` 文件夹（如有）
3. 重启 ComfyUI

---

### ⚠️ 重要变更

#### 📦 新增依赖
本次更新新增 `requests` 库用于CivitAI API调用：

**如果启动时报错：`ModuleNotFoundError: No module named 'requests'`**

请执行：
```bash
# 在 ComfyUI 虚拟环境中执行
pip install requests
```

或者：
```bash
# Windows 用户
python_embeded\python.exe -m pip install requests

# Linux/Mac 用户
python -m pip install requests
```

---

### 🎯 三大新功能详解

#### 1️⃣ 📥 下载文件夹自动监控

**功能说明：**
- 后台线程实时监控你的下载目录
- 新模型下载完成自动提示
- 可开启"自动整理"，下载完直接归位

**使用方法：**
1. 添加 `📥 下载文件夹监控` 节点
2. 设置你的下载目录（默认：~/Downloads）
3. 开启 `enable` 开关
4. （可选）开启 `auto_organize` 自动整理

**支持的临时文件：**
- `.tmp` - 通用临时文件
- `.crdownload` - Chrome下载
- `.part` - Firefox/IDM下载
- `.download` - Safari下载

---

#### 2️⃣ 🌐 CivitAI元数据自动拉取

**功能说明：**
- 根据模型SHA256哈希自动查询CivitAI
- 获取模型名称、类型、基础模型、标签、预览图
- 自动修正识别错误的模型类型
- 本地缓存7天，避免重复请求

**使用方法：**
1. 添加 `🌐 CivitAI元数据` 节点
2. 输入模型文件的完整路径
3. 执行节点，获取详细信息

**返回信息：**
- 📦 模型名称
- 📋 版本名称
- 🎯 模型类型
- 🧠 基础模型（SD1.5/SDXL/SD3等）
- 🏷️  标签
- 🖼️  预览图URL
- 🔗 CivitAI链接

**缓存说明：**
- 查询结果自动保存到 `civitai_cache.json`
- 缓存有效期7天
- 404结果也缓存，避免重复查询不存在的模型

---

#### 3️⃣ ✨ 重复模型智能去重

**功能说明：**
- 精确去重：SHA256哈希完全相同
- 智能去重：文件名相似、大小相近
- 三种保留策略可选
- 🛡️ 安全删除：先移到回收站，可恢复

**使用方法：**
1. 添加 `✨ 智能去重` 节点
2. 选择保留策略：
   - `newest` - 保留最新修改的文件
   - `largest` - 保留文件最大的（通常更完整）
   - `manual` - 手动选择（预览模式）
3. 先用 `dry_run=True` 预览结果
4. 确认无误后 `dry_run=False` 执行

**回收站机制：**
- 删除的文件移到 `ComfyUI/model_recycle_bin/`
- 文件名添加时间戳避免重名
- 删除记录保存在 `delete_records.json`
- 30天以上文件自动清理

---

### 📊 节点对照表

| 节点图标 | 节点名称 | 新增/原有 |
|---------|---------|----------|
| 🔍 | 模型扫描器 | 原有 |
| 📂 | 模型整理器 | 原有 |
| 🔄 | 重复模型查找 | 原有 |
| 🧹 | 空目录清理 | 原有 |
| 📥 | 下载文件夹监控 | ✨ 新增 |
| 🌐 | CivitAI元数据 | ✨ 新增 |
| ✨ | 智能去重 | ✨ 新增 |

---

### 🔧 技术改进

1. **多线程支持**
   - 下载监控使用后台守护线程
   - 不阻塞 ComfyUI 主线程
   - 优雅启停机制

2. **异常处理增强**
   - 所有网络请求超时保护
   - 文件操作异常捕获
   - 详细的错误日志输出

3. **性能优化**
   - 静态方法重构
   - 缓存机制优化
   - 减少重复计算

---

### ❓ 常见问题

**Q: 下载监控为什么不工作？**
- 检查目录路径是否正确
- 确认文件确实下载完成（大小稳定）
- 查看控制台日志

**Q: CivitAI查询总是失败？**
- 检查网络连接
- 确认模型确实在CivitAI存在
- 部分私有模型无法查询

**Q: 回收站在哪里？**
- `ComfyUI/model_recycle_bin/` 目录
- 手动恢复文件即可

**Q: 可以降级回v1.0.0吗？**
- 可以，直接替换文件即可
- 新功能节点会消失

---

---

## English

## 🚀 v1.1.0 Major Update

This update adds **three core features**, significantly enhancing plugin capabilities!

---

### 📋 Upgrade Steps

#### Method 1: Fresh Install (Recommended)
1. Delete old plugin folder
2. Download v1.1.0 package
3. Extract to `ComfyUI/custom_nodes/`
4. Restart ComfyUI

#### Method 2: Overwrite Upgrade
1. Directly overwrite all files
2. Delete `__pycache__` folder (if exists)
3. Restart ComfyUI

---

### ⚠️ Important Changes

#### 📦 New Dependency
This update adds `requests` library for CivitAI API:

**If you see: `ModuleNotFoundError: No module named 'requests'`**

Run:
```bash
# In ComfyUI virtual environment
pip install requests
```

---

### 🎯 Three New Features

#### 1️⃣ 📥 Download Folder Monitor

**Features:**
- Background thread monitors your download directory
- Auto-detect when new model download completes
- Optional auto-organize on download completion

**Usage:**
1. Add `📥 DownloadMonitor` node
2. Set your download path (default: ~/Downloads)
3. Enable the `enable` switch
4. (Optional) Enable `auto_organize`

**Supported temp files:**
- `.tmp` - General temp files
- `.crdownload` - Chrome downloads
- `.part` - Firefox/IDM downloads
- `.download` - Safari downloads

---

#### 2️⃣ 🌐 CivitAI Metadata Fetcher

**Features:**
- Auto-query CivitAI by SHA256 hash
- Get model name, type, base model, tags, preview
- Auto-correct misidentified model types
- Local cache for 7 days

**Usage:**
1. Add `🌐 CivitAIMetadata` node
2. Input full model file path
3. Execute to get detailed info

**Returns:**
- 📦 Model name
- 📋 Version name
- 🎯 Model type
- 🧠 Base model (SD1.5/SDXL/SD3)
- 🏷️  Tags
- 🖼️  Preview URL
- 🔗 CivitAI link

**Caching:**
- Results saved to `civitai_cache.json`
- 7-day cache validity
- 404 results also cached

---

#### 3️⃣ ✨ Smart Deduplicator

**Features:**
- Exact match: SHA256 hash identical
- Smart match: Similar filename, similar size
- 3 retention strategies
- 🛡️ Safe delete: Move to recycle bin first

**Usage:**
1. Add `✨ SmartDeduplicate` node
2. Choose strategy:
   - `newest` - Keep newest file
   - `largest` - Keep largest file
   - `manual` - Manual selection (preview mode)
3. Preview first with `dry_run=True`
4. Execute with `dry_run=False`

**Recycle Bin:**
- Deleted files moved to `ComfyUI/model_recycle_bin/`
- Timestamp added to avoid conflicts
- Records saved in `delete_records.json`
- Auto-clean files older than 30 days

---

### 📊 Node Reference

| Icon | Node Name | Status |
|------|-----------|--------|
| 🔍 | ModelScanner | Existing |
| 📂 | ModelOrganizer | Existing |
| 🔄 | DuplicateFinder | Existing |
| 🧹 | EmptyDirCleaner | Existing |
| 📥 | DownloadMonitor | ✨ New |
| 🌐 | CivitAIMetadata | ✨ New |
| ✨ | SmartDeduplicate | ✨ New |

---

### 🔧 Technical Improvements

1. **Multi-threading Support**
   - Download monitor uses background daemon thread
   - Non-blocking ComfyUI main thread
   - Graceful start/stop mechanism

2. **Enhanced Error Handling**
   - Timeout protection for all network requests
   - File operation exception catching
   - Detailed error logging

3. **Performance Optimizations**
   - Static method refactoring
   - Optimized caching mechanism
   - Reduced redundant calculations

---

### ❓ FAQ

**Q: Why isn't download monitor working?**
- Check if directory path is correct
- Confirm file download completed (size stable)
- Check console logs

**Q: CivitAI queries always fail?**
- Check network connection
- Confirm model exists on CivitAI
- Some private models cannot be queried

**Q: Where is the recycle bin?**
- `ComfyUI/model_recycle_bin/` directory
- Manually restore files

**Q: Can I downgrade to v1.0.0?**
- Yes, just replace files
- New feature nodes will disappear
