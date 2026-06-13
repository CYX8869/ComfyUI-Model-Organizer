"""
ComfyUI Model Organizer v1.1.0 - Core Module
自动扫描、分类、整理和管理ComfyUI模型文件

v1.1.0 新增功能:
- 下载文件夹自动监控
- CivitAI元数据自动拉取
- 重复模型智能去重
"""

import os
import json
import shutil
import hashlib
import time
import threading
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Callable
from datetime import datetime
import folder_paths
import queue


class DownloadMonitor:
    """下载文件夹监控器 - v1.1.0 新增"""
    
    # 临时文件扩展名（下载中）
    TEMP_EXTENSIONS = {'.tmp', '.crdownload', '.part', '.download', '.cfg'}
    
    def __init__(self, download_path: str, callback: Optional[Callable] = None, auto_organize: bool = False):
        """
        初始化下载监控器
        
        Args:
            download_path: 监控的下载目录
            callback: 新文件发现回调函数
            auto_organize: 是否自动整理
        """
        self.download_path = download_path
        self.callback = callback
        self.auto_organize = auto_organize
        self.running = False
        self.monitor_thread = None
        self.known_files = set()
        self.file_sizes = {}
        self.organizer = ModelOrganizer()
        
        # 初始化已知文件
        if os.path.exists(download_path):
            for f in os.listdir(download_path):
                filepath = os.path.join(download_path, f)
                if os.path.isfile(filepath):
                    self.known_files.add(filepath)
    
    def start(self):
        """启动监控线程"""
        if self.running:
            return
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"[ModelOrganizer] 下载监控已启动: {self.download_path}")
    
    def stop(self):
        """停止监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                self._check_new_files()
            except Exception as e:
                print(f"[ModelOrganizer] 监控错误: {e}")
            time.sleep(2)  # 每2秒检查一次
    
    def _check_new_files(self):
        """检查新文件"""
        if not os.path.exists(self.download_path):
            return
            
        current_files = set()
        
        for root, dirs, files in os.walk(self.download_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                
                # 跳过临时文件
                if any(filename.lower().endswith(ext) for ext in self.TEMP_EXTENSIONS):
                    continue
                
                # 跳过非模型文件
                if not any(filename.lower().endswith(ext) for ext in ModelOrganizer.MODEL_EXTENSIONS):
                    continue
                
                current_files.add(filepath)
                
                # 检查是否是新文件
                if filepath not in self.known_files:
                    # 检查文件是否还在写入中（大小稳定）
                    current_size = os.path.getsize(filepath)
                    if filepath in self.file_sizes:
                        if self.file_sizes[filepath] == current_size:
                            # 文件大小稳定，下载完成
                            self._on_new_file(filepath)
                            self.known_files.add(filepath)
                            del self.file_sizes[filepath]
                    else:
                        self.file_sizes[filepath] = current_size
        
        # 清理已删除的文件
        self.known_files &= current_files
    
    def _on_new_file(self, filepath: str):
        """新文件发现处理"""
        filename = os.path.basename(filepath)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        print(f"[ModelOrganizer] 📥 发现新模型: {filename} ({size_mb:.1f} MB)")
        
        # 调用回调
        if self.callback:
            try:
                self.callback(filepath)
            except Exception as e:
                print(f"[ModelOrganizer] 回调错误: {e}")
        
        # 自动整理
        if self.auto_organize:
            self._auto_organize_file(filepath)
    
    def _auto_organize_file(self, filepath: str):
        """自动整理单个文件"""
        try:
            filename = os.path.basename(filepath)
            model_type = self.organizer._detect_model_type(filepath, filename)
            target_dir = os.path.join(self.organizer.models_path, model_type)
            
            os.makedirs(target_dir, exist_ok=True)
            dst_path = os.path.join(target_dir, filename)
            
            # 处理重名
            if os.path.exists(dst_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dst_path):
                    dst_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
                    counter += 1
            
            shutil.move(filepath, dst_path)
            print(f"[ModelOrganizer] ✅ 自动整理: {filename} -> {model_type}/")
        except Exception as e:
            print(f"[ModelOrganizer] 自动整理失败: {e}")


class CivitAIMetadata:
    """CivitAI元数据拉取器 - v1.1.0 新增"""
    
    API_BASE = "https://civitai.com/api/v1"
    
    def __init__(self, cache_file: Optional[str] = None):
        """
        初始化CivitAI元数据获取器
        
        Args:
            cache_file: 缓存文件路径
        """
        if cache_file is None:
            cache_file = os.path.join(os.path.dirname(__file__), 'civitai_cache.json')
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ComfyUI-Model-Organizer/1.1.0'
        })
    
    def _load_cache(self) -> Dict:
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_cache(self):
        """保存缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ModelOrganizer] 缓存保存失败: {e}")
    
    def get_model_by_hash(self, sha256: str) -> Optional[Dict]:
        """
        通过SHA256哈希查询CivitAI模型信息
        
        Args:
            sha256: 模型文件SHA256哈希
            
        Returns:
            模型元数据字典
        """
        # 检查缓存
        if sha256 in self.cache:
            cached = self.cache[sha256]
            # 缓存有效期7天
            if time.time() - cached.get('timestamp', 0) < 7 * 24 * 3600:
                return cached.get('data')
        
        try:
            url = f"{self.API_BASE}/model-versions/by-hash/{sha256}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = self._parse_metadata(data)
                
                # 存入缓存
                self.cache[sha256] = {
                    'timestamp': time.time(),
                    'data': result
                }
                self._save_cache()
                
                return result
            elif response.status_code == 404:
                # 模型不存在，也缓存避免重复查询
                self.cache[sha256] = {
                    'timestamp': time.time(),
                    'data': None
                }
                self._save_cache()
                return None
            else:
                print(f"[ModelOrganizer] CivitAI API错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[ModelOrganizer] CivitAI查询失败: {e}")
            return None
    
    def _parse_metadata(self, data: Dict) -> Dict:
        """解析CivitAI返回的元数据"""
        try:
            model = data.get('model', {})
            files = data.get('files', [])
            
            # 获取基础模型类型
            base_model = data.get('baseModel', 'Unknown')
            
            # 获取预览图
            images = data.get('images', [])
            preview_url = images[0].get('url') if images else None
            
            # 获取模型类型
            model_type_map = {
                'Checkpoint': 'checkpoints',
                'LORA': 'loras',
                'LoCon': 'loras',
                'DoRA': 'loras',
                'TextualInversion': 'embeddings',
                'VAE': 'vae',
                'Controlnet': 'controlnet',
                'Upscaler': 'upscale_models',
            }
            model_type = model_type_map.get(model.get('type'), 'checkpoints')
            
            return {
                'name': model.get('name', 'Unknown'),
                'model_name': model.get('name'),
                'version_name': data.get('name', ''),
                'type': model_type,
                'base_model': base_model,
                'description': model.get('description', ''),
                'tags': model.get('tags', []),
                'preview_url': preview_url,
                'model_id': model.get('id'),
                'version_id': data.get('id'),
                'download_url': files[0].get('downloadUrl') if files else None,
                'size_kb': files[0].get('sizeKB') if files else None,
                'nsfw': model.get('nsfw', False),
            }
        except Exception as e:
            print(f"[ModelOrganizer] 元数据解析失败: {e}")
            return None
    
    def batch_fetch_metadata(self, filepaths: List[str], progress_callback: Optional[Callable] = None) -> Dict[str, Dict]:
        """
        批量获取元数据
        
        Args:
            filepaths: 文件路径列表
            progress_callback: 进度回调函数 (current, total)
            
        Returns:
            {sha256: metadata} 字典
        """
        results = {}
        total = len(filepaths)
        
        for i, filepath in enumerate(filepaths):
            try:
                sha256 = ModelOrganizer._calculate_file_hash(None, filepath)
                metadata = self.get_model_by_hash(sha256)
                if metadata:
                    results[sha256] = metadata
            except Exception:
                pass
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results


class SmartDeduplicator:
    """智能去重器 - v1.1.0 新增"""
    
    STRATEGY_NEWEST = 'newest'    # 保留最新
    STRATEGY_LARGEST = 'largest'  # 保留最大
    STRATEGY_MANUAL = 'manual'    # 手动选择
    
    def __init__(self, organizer):
        self.organizer = organizer
        self.recycle_bin = os.path.join(organizer.base_path, 'model_recycle_bin')
        os.makedirs(self.recycle_bin, exist_ok=True)
    
    def find_exact_duplicates(self) -> List[List[Dict]]:
        """查找精确重复（SHA256相同）"""
        return self.organizer.find_duplicates()
    
    def find_smart_duplicates(self) -> List[List[Dict]]:
        """
        智能查找相似模型（不同命名但可能是同一模型）
        基于文件名相似度、大小等特征
        """
        all_models = []
        scanned = self.organizer.scan_models()
        
        for models in scanned.values():
            all_models.extend(models)
        
        # 按大小分组（相近大小的可能是同一模型）
        size_groups = {}
        for model in all_models:
            # 大小误差在2MB以内视为相近
            size_key = round(model['size_mb'] / 2) * 2
            if size_key not in size_groups:
                size_groups[size_key] = []
            size_groups[size_key].append(model)
        
        smart_duplicates = []
        
        for group in size_groups.values():
            if len(group) < 2:
                continue
                
            # 检查文件名相似度
            name_groups = self._group_by_name_similarity(group)
            for dup_group in name_groups:
                if len(dup_group) >= 2:
                    smart_duplicates.append(dup_group)
        
        return smart_duplicates
    
    def _group_by_name_similarity(self, models: List[Dict]) -> List[List[Dict]]:
        """按文件名相似度分组"""
        # 简单实现：提取核心名称（去除版本号、日期等）
        import re
        
        groups = {}
        
        for model in models:
            name = model['name'].lower()
            # 移除版本号、日期、哈希后缀
            name = re.sub(r'[\-_]v?\d+(\.\d+)*', '', name)
            name = re.sub(r'[\-_]\d{4,}', '', name)
            name = re.sub(r'[\-_][a-f0-9]{8,}', '', name)
            name = re.sub(r'\.(safetensors|ckpt|bin|pt)$', '', name)
            name = name.strip('_- ')
            
            if name not in groups:
                groups[name] = []
            groups[name].append(model)
        
        return [g for g in groups.values() if len(g) >= 2]
    
    def suggest_keep(self, duplicate_group: List[Dict], strategy: str = STRATEGY_NEWEST) -> Dict:
        """
        建议保留哪个文件
        
        Args:
            duplicate_group: 重复文件组
            strategy: 保留策略
            
        Returns:
            建议保留的文件信息
        """
        if len(duplicate_group) == 1:
            return duplicate_group[0]
        
        if strategy == self.STRATEGY_NEWEST:
            # 按修改时间排序，最新的在前
            return sorted(duplicate_group, key=lambda x: x['modified'], reverse=True)[0]
        elif strategy == self.STRATEGY_LARGEST:
            # 按文件大小排序，最大的在前
            return sorted(duplicate_group, key=lambda x: x['size'], reverse=True)[0]
        else:
            return duplicate_group[0]
    
    def safe_delete(self, filepath: str) -> bool:
        """
        安全删除：移到回收站而不是直接删除
        
        Args:
            filepath: 要删除的文件路径
            
        Returns:
            是否成功
        """
        if not os.path.exists(filepath):
            return False
        
        try:
            filename = os.path.basename(filepath)
            # 添加时间戳避免重名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base, ext = os.path.splitext(filename)
            recycle_name = f"{base}_{timestamp}{ext}"
            dst_path = os.path.join(self.recycle_bin, recycle_name)
            
            shutil.move(filepath, dst_path)
            
            # 记录删除信息
            record = {
                'original_path': filepath,
                'recycle_path': dst_path,
                'deleted_at': datetime.now().isoformat()
            }
            record_file = os.path.join(self.recycle_bin, 'delete_records.json')
            
            records = []
            if os.path.exists(record_file):
                try:
                    with open(record_file, 'r') as f:
                        records = json.load(f)
                except Exception:
                    pass
            
            records.append(record)
            with open(record_file, 'w') as f:
                json.dump(records, f, indent=2)
            
            print(f"[ModelOrganizer] 🗑️  已移到回收站: {filename}")
            return True
        except Exception as e:
            print(f"[ModelOrganizer] 删除失败: {e}")
            return False
    
    def restore(self, recycle_filename: str) -> bool:
        """从回收站恢复文件"""
        # 简化实现
        src_path = os.path.join(self.recycle_bin, recycle_filename)
        if not os.path.exists(src_path):
            return False
        
        # 暂时恢复到模型根目录
        dst_path = os.path.join(self.organizer.models_path, recycle_filename)
        try:
            shutil.move(src_path, dst_path)
            return True
        except Exception:
            return False
    
    def empty_recycle_bin(self, older_than_days: int = 30) -> int:
        """清空回收站（删除N天前的文件）"""
        count = 0
        cutoff = time.time() - older_than_days * 86400
        
        for filename in os.listdir(self.recycle_bin):
            if filename == 'delete_records.json':
                continue
                
            filepath = os.path.join(self.recycle_bin, filename)
            if os.path.getmtime(filepath) < cutoff:
                try:
                    os.remove(filepath)
                    count += 1
                except Exception:
                    pass
        
        return count


class ModelOrganizer:
    """模型整理核心类"""
    
    # 支持的模型类型和对应的目录
    MODEL_TYPES = {
        'checkpoints': ['ckpt', 'safetensors', 'bin'],
        'vae': ['vae.pt', 'vae.safetensors', 'vae.bin'],
        'loras': ['lora', 'lycoris', 'locon'],
        'embeddings': ['pt', 'safetensors'],
        'controlnet': ['pth', 'safetensors', 'bin'],
        'upscale_models': ['pth', 'safetensors', 'bin'],
        'hypernetworks': ['pt', 'safetensors', 'bin'],
    }
    
    # 模型文件扩展名
    MODEL_EXTENSIONS = {'.safetensors', '.ckpt', '.bin', '.pt', '.pth'}
    
    # 全局监控实例
    _download_monitor = None
    
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化模型整理器
        
        Args:
            base_path: ComfyUI根目录路径，None则自动检测
        """
        self.base_path = self._detect_base_path(base_path)
        self.models_path = os.path.join(self.base_path, 'models')
        self.cache_file = os.path.join(self.base_path, 'model_cache.json')
        self.model_cache = self._load_cache()
        
        # v1.1.0 新增组件
        self.civitai = CivitAIMetadata()
        self.deduplicator = SmartDeduplicator(self)
        
    def _detect_base_path(self, custom_path: Optional[str]) -> str:
        """自动检测ComfyUI根目录"""
        if custom_path and os.path.exists(custom_path):
            return custom_path
            
        # 尝试常见路径
        common_paths = [
            os.getcwd(),
            os.path.dirname(os.getcwd()),
            '/workspace/ComfyUI',
            '/content/ComfyUI',
        ]
        
        for path in common_paths:
            models_dir = os.path.join(path, 'models')
            if os.path.exists(models_dir):
                return path
                
        return os.getcwd()
    
    def _load_cache(self) -> Dict:
        """加载模型缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {'models': {}, 'last_scan': None}
    
    def _save_cache(self) -> None:
        """保存模型缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ModelOrganizer] 保存缓存失败: {e}")
    
    @staticmethod
    def _calculate_file_hash(filepath: str) -> str:
        """计算文件哈希用于去重"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def scan_models(self, recursive: bool = True) -> Dict[str, List[Dict]]:
        """
        扫描所有模型文件
        
        Args:
            recursive: 是否递归扫描子目录
            
        Returns:
            按类型分类的模型列表
        """
        results = {model_type: [] for model_type in self.MODEL_TYPES.keys()}
        results['unknown'] = []
        
        if not os.path.exists(self.models_path):
            return results
            
        for root, dirs, files in os.walk(self.models_path):
            for filename in files:
                if not any(filename.lower().endswith(ext) for ext in self.MODEL_EXTENSIONS):
                    continue
                    
                filepath = os.path.join(root, filename)
                model_info = self._analyze_model(filepath)
                
                # 确定模型类型
                model_type = self._detect_model_type(filepath, filename)
                results[model_type].append(model_info)
                
                # 更新缓存
                self.model_cache['models'][model_info['hash']] = model_info
            
            if not recursive:
                break
                
        self._save_cache()
        return results
    
    def _analyze_model(self, filepath: str) -> Dict:
        """分析单个模型文件信息"""
        stat = os.stat(filepath)
        return {
            'name': os.path.basename(filepath),
            'path': filepath,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'hash': self._calculate_file_hash(filepath),
            'modified': stat.st_mtime,
            'extension': os.path.splitext(filepath)[1].lower()
        }
    
    def _detect_model_type(self, filepath: str, filename: str) -> str:
        """根据路径和文件名检测模型类型"""
        path_lower = filepath.lower()
        name_lower = filename.lower()
        
        # 按目录判断
        for model_type in self.MODEL_TYPES.keys():
            if model_type in path_lower:
                return model_type
        
        # 按文件名关键词判断
        keywords = {
            'vae': ['vae'],
            'loras': ['lora', 'lycoris', 'locon', 'dora'],
            'controlnet': ['controlnet', 'cn_', 'control_'],
            'upscale_models': ['upscale', 'upscaler', 'esrgan', 'swinir'],
            'hypernetworks': ['hypernetwork', 'hyper'],
            'embeddings': ['embedding', 'embed'],
        }
        
        for model_type, keys in keywords.items():
            if any(key in name_lower for key in keys):
                return model_type
        
        return 'checkpoints'
    
    def organize_models(self, dry_run: bool = False) -> Dict:
        """
        自动整理模型到对应目录
        
        Args:
            dry_run: 只显示将要执行的操作，不实际移动文件
            
        Returns:
            整理操作统计
        """
        stats = {
            'moved': [],
            'skipped': [],
            'duplicates': [],
            'errors': []
        }
        
        scanned = self.scan_models()
        
        for model_type, models in scanned.items():
            if model_type == 'unknown':
                continue
                
            target_dir = os.path.join(self.models_path, model_type)
            os.makedirs(target_dir, exist_ok=True)
            
            for model in models:
                src_path = model['path']
                dst_path = os.path.join(target_dir, model['name'])
                
                # 检查是否已经在正确目录
                if os.path.dirname(src_path) == target_dir:
                    stats['skipped'].append(f"{model['name']} (已在正确位置)")
                    continue
                
                # 检查目标文件是否存在
                if os.path.exists(dst_path):
                    src_hash = model['hash']
                    dst_hash = self._calculate_file_hash(dst_path)
                    
                    if src_hash == dst_hash:
                        stats['duplicates'].append(f"{model['name']} (重复文件)")
                        continue
                    else:
                        # 重命名避免冲突
                        base, ext = os.path.splitext(model['name'])
                        counter = 1
                        while os.path.exists(dst_path):
                            dst_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
                            counter += 1
                
                # 执行移动
                try:
                    if not dry_run:
                        shutil.move(src_path, dst_path)
                    stats['moved'].append(f"{model['name']} -> {model_type}/")
                except Exception as e:
                    stats['errors'].append(f"{model['name']}: {str(e)}")
        
        return stats
    
    def find_duplicates(self) -> List[List[Dict]]:
        """查找重复的模型文件"""
        hash_groups: Dict[str, List[Dict]] = {}
        
        scanned = self.scan_models()
        for models in scanned.values():
            for model in models:
                h = model['hash']
                if h not in hash_groups:
                    hash_groups[h] = []
                hash_groups[h].append(model)
        
        return [group for group in hash_groups.values() if len(group) > 1]
    
    def cleanup_empty_dirs(self) -> List[str]:
        """清理空的模型子目录"""
        removed = []
        
        for root, dirs, files in os.walk(self.models_path, topdown=False):
            for d in dirs:
                dirpath = os.path.join(root, d)
                if not os.listdir(dirpath):
                    try:
                        os.rmdir(dirpath)
                        removed.append(dirpath)
                    except Exception:
                        pass
        
        return removed
    
    # === v1.1.0 新增方法 ===
    
    @classmethod
    def start_download_monitor(cls, download_path: str, auto_organize: bool = False) -> bool:
        """启动下载文件夹监控"""
        if cls._download_monitor and cls._download_monitor.running:
            cls._download_monitor.stop()
        
        cls._download_monitor = DownloadMonitor(download_path, auto_organize=auto_organize)
        cls._download_monitor.start()
        return True
    
    @classmethod
    def stop_download_monitor(cls) -> bool:
        """停止下载监控"""
        if cls._download_monitor:
            cls._download_monitor.stop()
            cls._download_monitor = None
            return True
        return False
    
    def fetch_civitai_metadata(self, filepath: str) -> Optional[Dict]:
        """获取单个文件的CivitAI元数据"""
        sha256 = self._calculate_file_hash(filepath)
        return self.civitai.get_model_by_hash(sha256)
    
    def smart_deduplicate(self, strategy: str = SmartDeduplicator.STRATEGY_NEWEST, dry_run: bool = True) -> Dict:
        """
        智能去重
        
        Args:
            strategy: 保留策略
            dry_run: 是否只预览
            
        Returns:
            去重结果统计
        """
        exact_duplicates = self.deduplicator.find_exact_duplicates()
        smart_duplicates = self.deduplicator.find_smart_duplicates()
        
        results = {
            'exact_groups': len(exact_duplicates),
            'smart_groups': len(smart_duplicates),
            'deleted': [],
            'recoverable_space': 0
        }
        
        # 处理精确重复
        for group in exact_duplicates:
            keep = self.deduplicator.suggest_keep(group, strategy)
            for model in group:
                if model['path'] != keep['path']:
                    results['recoverable_space'] += model['size_mb']
                    if not dry_run:
                        if self.deduplicator.safe_delete(model['path']):
                            results['deleted'].append(model['name'])
        
        return results


# ============================================================================
# ComfyUI 节点定义
# ============================================================================

class ModelScannerNode:
    """模型扫描节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "recursive": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "JSON")
    RETURN_NAMES = ("summary", "model_data")
    FUNCTION = "scan"
    CATEGORY = "utils/model_organizer"
    
    def scan(self, recursive: bool):
        organizer = ModelOrganizer()
        results = organizer.scan_models(recursive)
        
        summary = []
        total_size = 0
        total_count = 0
        
        for model_type, models in results.items():
            count = len(models)
            size = sum(m['size_mb'] for m in models)
            total_count += count
            total_size += size
            if count > 0:
                summary.append(f"{model_type}: {count} 个模型, {size:.1f} MB")
        
        summary_text = f"扫描完成！共发现 {total_count} 个模型，总大小 {total_size:.1f} MB\n" + "\n".join(summary)
        
        return (summary_text, json.dumps(results, ensure_ascii=False, indent=2))


class ModelOrganizerNode:
    """模型整理节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dry_run": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "organize"
    CATEGORY = "utils/model_organizer"
    
    def organize(self, dry_run: bool):
        organizer = ModelOrganizer()
        stats = organizer.organize_models(dry_run)
        
        mode = "【预览模式】" if dry_run else "【执行模式】"
        result = [f"{mode} 模型整理完成\n"]
        
        if stats['moved']:
            result.append(f"✅ 已移动: {len(stats['moved'])} 个文件")
            for item in stats['moved'][:10]:
                result.append(f"  - {item}")
            if len(stats['moved']) > 10:
                result.append(f"  ... 还有 {len(stats['moved']) - 10} 个")
        
        if stats['skipped']:
            result.append(f"⏭️  已跳过: {len(stats['skipped'])} 个文件")
        
        if stats['duplicates']:
            result.append(f"⚠️  发现重复: {len(stats['duplicates'])} 个文件")
        
        if stats['errors']:
            result.append(f"❌ 错误: {len(stats['errors'])} 个")
            for err in stats['errors']:
                result.append(f"  - {err}")
        
        if dry_run:
            result.append("\n💡 提示: 取消 dry_run 选项以执行实际移动操作")
        
        return ("\n".join(result),)


class DuplicateFinderNode:
    """重复模型查找节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {}
        }
    
    RETURN_TYPES = ("STRING", "JSON")
    RETURN_NAMES = ("report", "duplicate_data")
    FUNCTION = "find_duplicates"
    CATEGORY = "utils/model_organizer"
    
    def find_duplicates(self):
        organizer = ModelOrganizer()
        duplicates = organizer.find_duplicates()
        
        if not duplicates:
            return ("✅ 未发现重复模型文件", "[]")
        
        report = [f"⚠️ 发现 {len(duplicates)} 组重复模型:\n"]
        total_wasted = 0
        
        for i, group in enumerate(duplicates, 1):
            report.append(f"\n--- 重复组 #{i} ---")
            size_mb = group[0]['size_mb']
            wasted = size_mb * (len(group) - 1)
            total_wasted += wasted
            
            for j, model in enumerate(group):
                prefix = "📌 保留: " if j == 0 else "❌ 可删除: "
                report.append(f"{prefix}{model['name']}")
                report.append(f"    路径: {model['path']}")
        
        report.append(f"\n💰 可释放空间: {total_wasted:.1f} MB")
        
        return ("\n".join(report), json.dumps(duplicates, ensure_ascii=False, indent=2))


class EmptyDirCleanerNode:
    """空目录清理节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {}
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "cleanup"
    CATEGORY = "utils/model_organizer"
    
    def cleanup(self):
        organizer = ModelOrganizer()
        removed = organizer.cleanup_empty_dirs()
        
        if removed:
            result = [f"✅ 已清理 {len(removed)} 个空目录:\n"]
            for d in removed:
                result.append(f"  - {d}")
            return ("\n".join(result),)
        
        return ("✅ 没有需要清理的空目录",)


# === v1.1.0 新增节点 ===

class DownloadMonitorNode:
    """下载文件夹监控节点 - v1.1.0 新增"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "download_path": ("STRING", {"default": os.path.expanduser("~/Downloads")}),
                "auto_organize": ("BOOLEAN", {"default": False}),
                "enable": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "monitor"
    CATEGORY = "utils/model_organizer"
    
    def monitor(self, download_path: str, auto_organize: bool, enable: bool):
        if enable:
            expanded_path = os.path.expanduser(download_path)
            if os.path.exists(expanded_path):
                ModelOrganizer.start_download_monitor(expanded_path, auto_organize)
                status = f"""✅ 下载监控已启动
监控目录: {expanded_path}
自动整理: {'已开启' if auto_organize else '已关闭'}

💡 新模型下载完成后会自动检测并提示"""
            else:
                status = f"❌ 目录不存在: {expanded_path}"
        else:
            ModelOrganizer.stop_download_monitor()
            status = "⏹️  下载监控已停止"
        
        return (status,)


class CivitAIMetadataNode:
    """CivitAI元数据查询节点 - v1.1.0 新增"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_path": ("STRING", {"default": "", "placeholder": "模型文件完整路径"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "JSON")
    RETURN_NAMES = ("metadata", "raw_data")
    FUNCTION = "fetch"
    CATEGORY = "utils/model_organizer"
    
    def fetch(self, model_path: str):
        if not model_path or not os.path.exists(model_path):
            return ("❌ 请提供有效的模型文件路径", "{}")
        
        organizer = ModelOrganizer()
        metadata = organizer.fetch_civitai_metadata(model_path)
        
        if metadata is None:
            return ("⚠️ 未在 CivitAI 找到该模型的元数据", "{}")
        
        result = [
            f"📦 模型名称: {metadata['name']}",
            f"📋 版本: {metadata['version_name']}",
            f"🎯 类型: {metadata['type']}",
            f"🧠 基础模型: {metadata['base_model']}",
        ]
        
        if metadata['tags']:
            result.append(f"🏷️  标签: {', '.join(metadata['tags'][:10])}")
        
        if metadata['preview_url']:
            result.append(f"🖼️  预览图: {metadata['preview_url']}")
        
        result.append(f"\n🔗 CivitAI链接: https://civitai.com/models/{metadata['model_id']}")
        
        return ("\n".join(result), json.dumps(metadata, ensure_ascii=False, indent=2))


class SmartDeduplicateNode:
    """智能去重节点 - v1.1.0 新增"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "strategy": (["newest", "largest", "manual"],),
                "dry_run": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "deduplicate"
    CATEGORY = "utils/model_organizer"
    
    def deduplicate(self, strategy: str, dry_run: bool):
        organizer = ModelOrganizer()
        results = organizer.smart_deduplicate(strategy, dry_run)
        
        mode = "【预览模式】" if dry_run else "【执行模式】"
        strategy_name = {
            'newest': '保留最新文件',
            'largest': '保留最大文件',
            'manual': '手动选择'
        }
        
        result = [
            f"{mode} 智能去重完成",
            f"策略: {strategy_name[strategy]}",
            f"",
            f"🔍 精确重复组: {results['exact_groups']} 组",
            f"🤔 疑似重复组: {results['smart_groups']} 组",
            f"💰 可释放空间: {results['recoverable_space']:.1f} MB",
        ]
        
        if dry_run:
            result.append("\n💡 提示: 取消 dry_run 执行实际去重（文件移到回收站）")
        else:
            result.append(f"\n🗑️  已处理: {len(results['deleted'])} 个文件")
            result.append("ℹ️  文件已移到回收站，可恢复")
        
        return ("\n".join(result),)


# 节点导出
NODE_CLASS_MAPPINGS = {
    # 基础功能
    "ModelScanner": ModelScannerNode,
    "ModelOrganizer": ModelOrganizerNode,
    "DuplicateFinder": DuplicateFinderNode,
    "EmptyDirCleaner": EmptyDirCleanerNode,
    # v1.1.0 新增
    "DownloadMonitor": DownloadMonitorNode,
    "CivitAIMetadata": CivitAIMetadataNode,
    "SmartDeduplicate": SmartDeduplicateNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # 基础功能
    "ModelScanner": "🔍 模型扫描器",
    "ModelOrganizer": "📂 模型整理器",
    "DuplicateFinder": "🔄 重复模型查找",
    "EmptyDirCleaner": "🧹 空目录清理",
    # v1.1.0 新增
    "DownloadMonitor": "📥 下载文件夹监控",
    "CivitAIMetadata": "🌐 CivitAI元数据",
    "SmartDeduplicate": "✨ 智能去重",
}
