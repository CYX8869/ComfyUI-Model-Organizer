# GitHub 上传手把手教程 / GitHub Upload Step-by-Step Guide

<div align="center">

🇨🇳 中文 | 🇺🇸 English

</div>

---

## 🇨🇳 中文教程

### 📋 准备工作

#### 1. 注册 GitHub 账号
1. 访问 https://github.com
2. 点击右上角 "Sign up"
3. 填写邮箱、密码、用户名
4. 验证邮箱完成注册

#### 2. 安装 Git
**Windows:**
- 下载：https://git-scm.com/download/win
- 双击安装，全部默认选项即可

**Mac:**
```bash
brew install git
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install git
```

#### 3. 配置 Git
打开命令行（CMD / Terminal），执行：
```bash
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的GitHub注册邮箱"
```

---

### 🚀 第一步：创建 GitHub 仓库

1. 登录 GitHub，点击右上角 **+** → **New repository**
2. 填写仓库信息：
   - **Repository name**: `ComfyUI-Model-Organizer`
   - **Description**: `ComfyUI plugin for automatic model organization and management`
   - 选择 **Public**（公开，推荐开源）
   - ❌ **不要勾选** "Initialize this repository with a README"
   - ❌ **不要勾选** "Add .gitignore"
   - ❌ **不要勾选** "Choose a license"
3. 点击 **Create repository**

---

### 📂 第二步：上传项目文件

#### 方法一：命令行上传（推荐）

1. **进入项目文件夹**
```bash
cd /path/to/ComfyUI-Model-Organizer
```

2. **初始化 Git 仓库**
```bash
git init
```

3. **添加所有文件**
```bash
git add .
```

4. **提交更改**
```bash
git commit -m "Initial commit: ComfyUI Model Organizer v1.0.0"
```

5. **关联远程仓库**
   （将下面的 URL 替换为你自己的仓库地址）
```bash
git remote add origin https://github.com/你的用户名/ComfyUI-Model-Organizer.git
```

6. **推送到 GitHub**
```bash
git branch -M main
git push -u origin main
```

7. **输入 GitHub 账号密码**
   - 用户名：你的 GitHub 用户名
   - 密码：建议使用 Personal Access Token（见下文）

#### 方法二：GitHub Desktop（图形界面）

1. 下载 GitHub Desktop：https://desktop.github.com
2. 安装并登录你的 GitHub 账号
3. 点击 **File** → **Add Local Repository**
4. 选择项目文件夹
5. 点击 **Create a repository**
6. 填写信息后点击 **Publish repository**

---

### 🔐 创建 Personal Access Token (PAT)

从 2021 年起，GitHub 不再支持密码登录，需要使用 Token：

1. GitHub 右上角点击头像 → **Settings**
2. 左侧菜单 → **Developer settings**
3. 左侧 → **Personal access tokens** → **Tokens (classic)**
4. 点击 **Generate new token** → **Generate new token (classic)**
5. 填写：
   - Note: `Git upload token`
   - Expiration: `No expiration`（或选择有效期）
   - Select scopes: ✅ 勾选 `repo`
6. 点击 **Generate token**
7. **复制并保存这个 token**（只显示一次！）
8. 推送时，密码处粘贴这个 token

---

### ✅ 第三步：验证上传成功

1. 刷新你的 GitHub 仓库页面
2. 确认所有文件都已上传：
   - `__init__.py`
   - `model_organizer.py`
   - `README.md`
   - `LICENSE`
   - `CONTRIBUTING.md`
   - `CHANGELOG.md`
   - `.gitignore`
   - `pyproject.toml`
   - `.github/` 文件夹
3. 检查 README 是否正常显示

---

### 📝 后续更新代码

当你修改了代码，按以下步骤更新：

```bash
# 1. 查看修改的文件
git status

# 2. 添加修改的文件
git add .

# 3. 提交修改
git commit -m "描述你做了什么修改"

# 4. 推送到 GitHub
git push
```

---

### 🎯 仓库优化建议

1. **添加 Topics**:
   - 在仓库主页右侧点击 ⚙️ Manage topics
   - 添加：`comfyui`, `comfyui-plugin`, `stable-diffusion`, `ai-art`, `model-management`

2. **设置 Social preview**:
   - Settings → General → Social preview
   - 上传一张项目 Logo 或截图

3. **启用 Discussions**:
   - Settings → General → Features
   - 勾选 ✅ Discussions

---

---

## 🇺🇸 English Tutorial

### 📋 Prerequisites

#### 1. Create a GitHub Account
1. Visit https://github.com
2. Click "Sign up" in the top right
3. Enter email, password, username
4. Verify your email to complete registration

#### 2. Install Git
**Windows:**
- Download: https://git-scm.com/download/win
- Double-click to install, use all default options

**Mac:**
```bash
brew install git
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install git
```

#### 3. Configure Git
Open command line (CMD / Terminal) and run:
```bash
git config --global user.name "Your GitHub Username"
git config --global user.email "Your GitHub Email"
```

---

### 🚀 Step 1: Create GitHub Repository

1. Log in to GitHub, click **+** in top right → **New repository**
2. Fill in repository info:
   - **Repository name**: `ComfyUI-Model-Organizer`
   - **Description**: `ComfyUI plugin for automatic model organization and management`
   - Choose **Public** (recommended for open source)
   - ❌ **DO NOT CHECK** "Initialize this repository with a README"
   - ❌ **DO NOT CHECK** "Add .gitignore"
   - ❌ **DO NOT CHECK** "Choose a license"
3. Click **Create repository**

---

### 📂 Step 2: Upload Project Files

#### Method 1: Command Line (Recommended)

1. **Navigate to project folder**
```bash
cd /path/to/ComfyUI-Model-Organizer
```

2. **Initialize Git repository**
```bash
git init
```

3. **Add all files**
```bash
git add .
```

4. **Commit changes**
```bash
git commit -m "Initial commit: ComfyUI Model Organizer v1.0.0"
```

5. **Link remote repository**
   (Replace URL with your repository address)
```bash
git remote add origin https://github.com/your-username/ComfyUI-Model-Organizer.git
```

6. **Push to GitHub**
```bash
git branch -M main
git push -u origin main
```

7. **Enter GitHub credentials**
   - Username: Your GitHub username
   - Password: Use Personal Access Token (see below)

#### Method 2: GitHub Desktop (GUI)

1. Download GitHub Desktop: https://desktop.github.com
2. Install and log in to your GitHub account
3. Click **File** → **Add Local Repository**
4. Select your project folder
5. Click **Create a repository**
6. Fill in info and click **Publish repository**

---

### 🔐 Create Personal Access Token (PAT)

Since 2021, GitHub no longer supports password authentication - use a Token instead:

1. Click profile picture in top right → **Settings**
2. Left menu → **Developer settings**
3. Left → **Personal access tokens** → **Tokens (classic)**
4. Click **Generate new token** → **Generate new token (classic)**
5. Fill in:
   - Note: `Git upload token`
   - Expiration: `No expiration` (or choose validity period)
   - Select scopes: ✅ Check `repo`
6. Click **Generate token**
7. **Copy and save this token** (only shown once!)
8. When pushing, paste this token as the password

---

### ✅ Step 3: Verify Upload Success

1. Refresh your GitHub repository page
2. Confirm all files are uploaded:
   - `__init__.py`
   - `model_organizer.py`
   - `README.md`
   - `LICENSE`
   - `CONTRIBUTING.md`
   - `CHANGELOG.md`
   - `.gitignore`
   - `pyproject.toml`
   - `.github/` folder
3. Check that README displays correctly

---

### 📝 Updating Code Later

When you modify code, update with these steps:

```bash
# 1. View modified files
git status

# 2. Add modified files
git add .

# 3. Commit changes
git commit -m "Describe what you changed"

# 4. Push to GitHub
git push
```

---

### 🎯 Repository Optimization Tips

1. **Add Topics**:
   - On repository homepage, click ⚙️ Manage topics on the right
   - Add: `comfyui`, `comfyui-plugin`, `stable-diffusion`, `ai-art`, `model-management`

2. **Set Social preview**:
   - Settings → General → Social preview
   - Upload a project logo or screenshot

3. **Enable Discussions**:
   - Settings → General → Features
   - Check ✅ Discussions

---

## ❓ Troubleshooting / 常见问题

**Q: `fatal: remote origin already exists`**
```bash
git remote remove origin
git remote add origin https://github.com/your-username/ComfyUI-Model-Organizer.git
```

**Q: `error: failed to push some refs`**
```bash
git pull --rebase origin main
git push origin main
```

**Q: Permission denied**
- Double-check your token has `repo` scope
- Make sure you're using the token, not password

---

🎉 **Congratulations! Your project is now open source on GitHub!**
🎉 **恭喜！你的项目已经成功在 GitHub 上开源了！**
