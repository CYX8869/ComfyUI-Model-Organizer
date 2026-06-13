"""
ComfyUI Model Organizer - Core Module
自动扫描、分类和整理ComfyUI模型文件
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import folder_paths

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
    
    def _calculate_file_hash(self, filepath: str) -> str:
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
            'loras': ['lora', 'lycoris', 'locon'],
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


# ComfyUI 节点定义
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


# 节点导出
NODE_CLASS_MAPPINGS = {
    "ModelScanner": ModelScannerNode,
    "ModelOrganizer": ModelOrganizerNode,
    "DuplicateFinder": DuplicateFinderNode,
    "EmptyDirCleaner": EmptyDirCleanerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ModelScanner": "🔍 模型扫描器",
    "ModelOrganizer": "📂 模型整理器",
    "DuplicateFinder": "🔄 重复模型查找",
    "EmptyDirCleaner": "🧹 空目录清理",
}
