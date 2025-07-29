#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محسن الأصول الثابتة
Asset Optimizer
"""

import os
import gzip
import hashlib
import logging
from pathlib import Path
from flask import current_app
import cssmin
import jsmin

logger = logging.getLogger('accounting_system')

class AssetOptimizer:
    """محسن الأصول الثابتة"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """تهيئة محسن الأصول"""
        self.app = app
        self.static_folder = Path(app.static_folder)
        self.optimized_folder = self.static_folder / 'optimized'
        self.optimized_folder.mkdir(exist_ok=True)
        
        # إعدادات التحسين
        self.enable_minification = app.config.get('ENABLE_MINIFICATION', True)
        self.enable_gzip = app.config.get('ENABLE_GZIP', True)
        self.enable_versioning = app.config.get('ENABLE_ASSET_VERSIONING', True)
        
        # قائمة الملفات للتحسين
        self.css_files = [
            'css/bootstrap.rtl.min.css',
            'css/main.css',
            'css/dashboard.css',
            'css/forms.css',
            'css/tables.css'
        ]
        
        self.js_files = [
            'js/jquery.min.js',
            'js/bootstrap.bundle.min.js',
            'js/chart.js',
            'js/main.js',
            'js/i18n.js',
            'js/dashboard.js',
            'js/forms.js'
        ]
    
    def optimize_all_assets(self):
        """تحسين جميع الأصول"""
        try:
            results = {
                'css': self.optimize_css_files(),
                'js': self.optimize_js_files(),
                'images': self.optimize_images()
            }
            
            logger.info("Asset optimization completed")
            return results
        
        except Exception as e:
            logger.error(f"Asset optimization failed: {str(e)}")
            return None
    
    def optimize_css_files(self):
        """تحسين ملفات CSS"""
        try:
            combined_css = ""
            original_size = 0
            
            for css_file in self.css_files:
                file_path = self.static_folder / css_file
                
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                        original_size += len(css_content)
                        
                        if self.enable_minification:
                            css_content = cssmin.cssmin(css_content)
                        
                        combined_css += css_content + '\n'
            
            # حفظ الملف المدمج
            if self.enable_versioning:
                version_hash = hashlib.md5(combined_css.encode()).hexdigest()[:8]
                output_file = self.optimized_folder / f'app.{version_hash}.min.css'
            else:
                output_file = self.optimized_folder / 'app.min.css'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(combined_css)
            
            # ضغط gzip
            if self.enable_gzip:
                with open(output_file, 'rb') as f_in:
                    with gzip.open(f"{output_file}.gz", 'wb') as f_out:
                        f_out.write(f_in.read())
            
            optimized_size = len(combined_css)
            compression_ratio = (1 - optimized_size / original_size) * 100 if original_size > 0 else 0
            
            return {
                'success': True,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'compression_ratio': round(compression_ratio, 2),
                'output_file': output_file.name
            }
        
        except Exception as e:
            logger.error(f"CSS optimization failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def optimize_js_files(self):
        """تحسين ملفات JavaScript"""
        try:
            combined_js = ""
            original_size = 0
            
            for js_file in self.js_files:
                file_path = self.static_folder / js_file
                
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        js_content = f.read()
                        original_size += len(js_content)
                        
                        if self.enable_minification and not js_file.endswith('.min.js'):
                            try:
                                js_content = jsmin.jsmin(js_content)
                            except Exception as e:
                                logger.warning(f"JS minification failed for {js_file}: {str(e)}")
                        
                        combined_js += js_content + '\n'
            
            # حفظ الملف المدمج
            if self.enable_versioning:
                version_hash = hashlib.md5(combined_js.encode()).hexdigest()[:8]
                output_file = self.optimized_folder / f'app.{version_hash}.min.js'
            else:
                output_file = self.optimized_folder / 'app.min.js'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(combined_js)
            
            # ضغط gzip
            if self.enable_gzip:
                with open(output_file, 'rb') as f_in:
                    with gzip.open(f"{output_file}.gz", 'wb') as f_out:
                        f_out.write(f_in.read())
            
            optimized_size = len(combined_js)
            compression_ratio = (1 - optimized_size / original_size) * 100 if original_size > 0 else 0
            
            return {
                'success': True,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'compression_ratio': round(compression_ratio, 2),
                'output_file': output_file.name
            }
        
        except Exception as e:
            logger.error(f"JS optimization failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def optimize_images(self):
        """تحسين الصور"""
        try:
            from PIL import Image
            
            image_folder = self.static_folder / 'images'
            optimized_count = 0
            total_saved = 0
            
            if not image_folder.exists():
                return {'success': True, 'optimized_count': 0, 'total_saved': 0}
            
            for image_file in image_folder.rglob('*'):
                if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    try:
                        original_size = image_file.stat().st_size
                        
                        # فتح وتحسين الصورة
                        with Image.open(image_file) as img:
                            # تحويل إلى RGB إذا لزم الأمر
                            if img.mode in ('RGBA', 'LA', 'P'):
                                img = img.convert('RGB')
                            
                            # حفظ بجودة محسنة
                            img.save(image_file, optimize=True, quality=85)
                        
                        new_size = image_file.stat().st_size
                        saved = original_size - new_size
                        
                        if saved > 0:
                            optimized_count += 1
                            total_saved += saved
                    
                    except Exception as e:
                        logger.warning(f"Image optimization failed for {image_file}: {str(e)}")
            
            return {
                'success': True,
                'optimized_count': optimized_count,
                'total_saved': total_saved,
                'total_saved_mb': round(total_saved / (1024 * 1024), 2)
            }
        
        except ImportError:
            logger.warning("PIL not available, skipping image optimization")
            return {'success': False, 'error': 'PIL not available'}
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_asset_manifest(self):
        """إنشاء ملف manifest للأصول"""
        try:
            manifest = {}
            
            # فحص الملفات المحسنة
            for file_path in self.optimized_folder.glob('*'):
                if file_path.is_file() and not file_path.name.endswith('.gz'):
                    # حساب hash للملف
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()[:8]
                    
                    # إضافة للـ manifest
                    original_name = file_path.stem.split('.')[0]  # إزالة hash والامتداد
                    manifest[f"{original_name}.{file_path.suffix[1:]}"] = {
                        'optimized_file': file_path.name,
                        'hash': file_hash,
                        'size': file_path.stat().st_size,
                        'gzipped': (file_path.parent / f"{file_path.name}.gz").exists()
                    }
            
            # حفظ manifest
            manifest_file = self.optimized_folder / 'manifest.json'
            import json
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            return manifest
        
        except Exception as e:
            logger.error(f"Manifest generation failed: {str(e)}")
            return {}
    
    def get_optimized_asset_url(self, asset_name):
        """الحصول على رابط الأصل المحسن"""
        try:
            manifest_file = self.optimized_folder / 'manifest.json'
            
            if manifest_file.exists():
                import json
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                if asset_name in manifest:
                    return f"/static/optimized/{manifest[asset_name]['optimized_file']}"
            
            # العودة للملف الأصلي إذا لم يوجد محسن
            return f"/static/{asset_name}"
        
        except Exception as e:
            logger.error(f"Asset URL generation failed: {str(e)}")
            return f"/static/{asset_name}"
    
    def clean_old_assets(self):
        """تنظيف الأصول القديمة"""
        try:
            deleted_count = 0
            
            # حذف الملفات المحسنة القديمة (الاحتفاظ بأحدث 5 إصدارات)
            css_files = sorted(self.optimized_folder.glob('app.*.min.css'), 
                             key=lambda x: x.stat().st_mtime, reverse=True)
            js_files = sorted(self.optimized_folder.glob('app.*.min.js'), 
                            key=lambda x: x.stat().st_mtime, reverse=True)
            
            # حذف ملفات CSS القديمة
            for old_file in css_files[5:]:
                old_file.unlink()
                # حذف النسخة المضغوطة أيضاً
                gz_file = Path(f"{old_file}.gz")
                if gz_file.exists():
                    gz_file.unlink()
                deleted_count += 1
            
            # حذف ملفات JS القديمة
            for old_file in js_files[5:]:
                old_file.unlink()
                # حذف النسخة المضغوطة أيضاً
                gz_file = Path(f"{old_file}.gz")
                if gz_file.exists():
                    gz_file.unlink()
                deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old asset files")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Asset cleanup failed: {str(e)}")
            return 0
    
    def get_optimization_stats(self):
        """الحصول على إحصائيات التحسين"""
        try:
            stats = {
                'optimized_files': 0,
                'total_size': 0,
                'gzipped_files': 0,
                'last_optimization': None
            }
            
            # فحص الملفات المحسنة
            for file_path in self.optimized_folder.glob('*'):
                if file_path.is_file():
                    if file_path.name.endswith('.gz'):
                        stats['gzipped_files'] += 1
                    else:
                        stats['optimized_files'] += 1
                        stats['total_size'] += file_path.stat().st_size
                    
                    # تحديث آخر وقت تحسين
                    file_time = file_path.stat().st_mtime
                    if not stats['last_optimization'] or file_time > stats['last_optimization']:
                        stats['last_optimization'] = file_time
            
            # تحويل الوقت لتنسيق قابل للقراءة
            if stats['last_optimization']:
                from datetime import datetime
                stats['last_optimization'] = datetime.fromtimestamp(stats['last_optimization'])
            
            stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
            
            return stats
        
        except Exception as e:
            logger.error(f"Stats generation failed: {str(e)}")
            return {}

# إنشاء مثيل محسن الأصول
asset_optimizer = AssetOptimizer()
