#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إدارة الترجمات
Translation Management Script
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# إضافة مسار التطبيق
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from flask_babel import Babel

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/translations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TranslationManager:
    """مدير الترجمات"""
    
    def __init__(self, app):
        self.app = app
        self.babel = Babel(app)
        self.base_dir = Path(app.root_path).parent
        self.translations_dir = self.base_dir / 'app' / 'translations'
        
    def extract_messages(self):
        """استخراج الرسائل القابلة للترجمة"""
        logger.info("استخراج الرسائل القابلة للترجمة...")
        
        try:
            # تشغيل pybabel extract
            cmd = [
                'pybabel', 'extract',
                '-F', str(self.base_dir / 'babel.cfg'),
                '-k', '_l',
                '-o', str(self.base_dir / 'messages.pot'),
                str(self.base_dir / 'app')
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                logger.info("تم استخراج الرسائل بنجاح")
                return True
            else:
                logger.error(f"فشل في استخراج الرسائل: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في استخراج الرسائل: {str(e)}")
            return False
    
    def init_language(self, language):
        """تهيئة لغة جديدة"""
        logger.info(f"تهيئة اللغة: {language}")
        
        try:
            # إنشاء مجلد اللغة
            lang_dir = self.translations_dir / language / 'LC_MESSAGES'
            lang_dir.mkdir(parents=True, exist_ok=True)
            
            # تشغيل pybabel init
            cmd = [
                'pybabel', 'init',
                '-i', str(self.base_dir / 'messages.pot'),
                '-d', str(self.translations_dir),
                '-l', language
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                logger.info(f"تم تهيئة اللغة {language} بنجاح")
                return True
            else:
                logger.error(f"فشل في تهيئة اللغة {language}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تهيئة اللغة {language}: {str(e)}")
            return False
    
    def update_translations(self):
        """تحديث جميع الترجمات"""
        logger.info("تحديث جميع الترجمات...")
        
        try:
            # تشغيل pybabel update
            cmd = [
                'pybabel', 'update',
                '-i', str(self.base_dir / 'messages.pot'),
                '-d', str(self.translations_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                logger.info("تم تحديث الترجمات بنجاح")
                return True
            else:
                logger.error(f"فشل في تحديث الترجمات: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تحديث الترجمات: {str(e)}")
            return False
    
    def compile_translations(self):
        """تجميع الترجمات"""
        logger.info("تجميع الترجمات...")
        
        try:
            # تشغيل pybabel compile
            cmd = [
                'pybabel', 'compile',
                '-d', str(self.translations_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                logger.info("تم تجميع الترجمات بنجاح")
                return True
            else:
                logger.error(f"فشل في تجميع الترجمات: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تجميع الترجمات: {str(e)}")
            return False
    
    def create_js_translations(self, language):
        """إنشاء ملف ترجمات JavaScript"""
        logger.info(f"إنشاء ترجمات JavaScript للغة: {language}")
        
        try:
            import polib
            import json
            
            # قراءة ملف .po
            po_file = self.translations_dir / language / 'LC_MESSAGES' / 'messages.po'
            
            if not po_file.exists():
                logger.warning(f"ملف الترجمة غير موجود: {po_file}")
                return False
            
            po = polib.pofile(str(po_file))
            
            # تحويل إلى JSON
            translations = {}
            for entry in po:
                if entry.msgstr:
                    translations[entry.msgid] = entry.msgstr
            
            # حفظ ملف JSON
            js_file = self.translations_dir / language / 'LC_MESSAGES' / 'messages.json'
            with open(js_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم إنشاء ملف JavaScript: {js_file}")
            return True
            
        except ImportError:
            logger.error("مكتبة polib غير مثبتة. يرجى تثبيتها: pip install polib")
            return False
        except Exception as e:
            logger.error(f"خطأ في إنشاء ترجمات JavaScript: {str(e)}")
            return False
    
    def validate_translations(self):
        """التحقق من صحة الترجمات"""
        logger.info("التحقق من صحة الترجمات...")
        
        issues = []
        
        for lang_code in self.app.config['LANGUAGES'].keys():
            lang_dir = self.translations_dir / lang_code / 'LC_MESSAGES'
            po_file = lang_dir / 'messages.po'
            
            if not po_file.exists():
                issues.append(f"ملف الترجمة مفقود: {po_file}")
                continue
            
            try:
                import polib
                po = polib.pofile(str(po_file))
                
                # فحص الترجمات المفقودة
                untranslated = [entry.msgid for entry in po.untranslated_entries()]
                if untranslated:
                    issues.append(f"ترجمات مفقودة في {lang_code}: {len(untranslated)} رسالة")
                
                # فحص الترجمات الضبابية
                fuzzy = [entry.msgid for entry in po.fuzzy_entries()]
                if fuzzy:
                    issues.append(f"ترجمات ضبابية في {lang_code}: {len(fuzzy)} رسالة")
                
            except ImportError:
                logger.warning("مكتبة polib غير متوفرة للتحقق المتقدم")
            except Exception as e:
                issues.append(f"خطأ في فحص {lang_code}: {str(e)}")
        
        if issues:
            logger.warning("مشاكل في الترجمات:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("جميع الترجمات صحيحة")
        
        return len(issues) == 0
    
    def get_translation_stats(self):
        """الحصول على إحصائيات الترجمة"""
        logger.info("جمع إحصائيات الترجمة...")
        
        stats = {}
        
        for lang_code, lang_name in self.app.config['LANGUAGES'].items():
            lang_dir = self.translations_dir / lang_code / 'LC_MESSAGES'
            po_file = lang_dir / 'messages.po'
            
            if not po_file.exists():
                stats[lang_code] = {
                    'name': lang_name,
                    'total': 0,
                    'translated': 0,
                    'untranslated': 0,
                    'fuzzy': 0,
                    'percentage': 0
                }
                continue
            
            try:
                import polib
                po = polib.pofile(str(po_file))
                
                total = len(po)
                translated = len(po.translated_entries())
                untranslated = len(po.untranslated_entries())
                fuzzy = len(po.fuzzy_entries())
                percentage = (translated / total * 100) if total > 0 else 0
                
                stats[lang_code] = {
                    'name': lang_name,
                    'total': total,
                    'translated': translated,
                    'untranslated': untranslated,
                    'fuzzy': fuzzy,
                    'percentage': round(percentage, 1)
                }
                
            except ImportError:
                logger.warning("مكتبة polib غير متوفرة للإحصائيات المتقدمة")
                stats[lang_code] = {
                    'name': lang_name,
                    'total': 0,
                    'translated': 0,
                    'untranslated': 0,
                    'fuzzy': 0,
                    'percentage': 0
                }
            except Exception as e:
                logger.error(f"خطأ في جمع إحصائيات {lang_code}: {str(e)}")
        
        return stats
    
    def full_update(self):
        """تحديث كامل للترجمات"""
        logger.info("🚀 بدء التحديث الكامل للترجمات...")
        
        success = True
        
        # 1. استخراج الرسائل
        if not self.extract_messages():
            success = False
        
        # 2. تحديث الترجمات
        if not self.update_translations():
            success = False
        
        # 3. تجميع الترجمات
        if not self.compile_translations():
            success = False
        
        # 4. إنشاء ترجمات JavaScript
        for lang_code in self.app.config['LANGUAGES'].keys():
            if not self.create_js_translations(lang_code):
                success = False
        
        # 5. التحقق من الترجمات
        self.validate_translations()
        
        # 6. عرض الإحصائيات
        stats = self.get_translation_stats()
        logger.info("\n📊 إحصائيات الترجمة:")
        for lang_code, stat in stats.items():
            logger.info(f"  {stat['name']} ({lang_code}): {stat['translated']}/{stat['total']} ({stat['percentage']}%)")
        
        if success:
            logger.info("✅ تم التحديث الكامل للترجمات بنجاح!")
        else:
            logger.error("❌ فشل في بعض خطوات التحديث!")
        
        return success

def main():
    """الدالة الرئيسية"""
    import argparse
    
    parser = argparse.ArgumentParser(description='إدارة ترجمات نظام المحاسبة')
    parser.add_argument('action', choices=['extract', 'init', 'update', 'compile', 'validate', 'stats', 'full'], 
                       help='الإجراء المطلوب')
    parser.add_argument('--language', '-l', help='رمز اللغة (للإجراءات المحددة)')
    
    args = parser.parse_args()
    
    # إنشاء التطبيق
    app = create_app()
    
    # إنشاء مدير الترجمات
    manager = TranslationManager(app)
    
    with app.app_context():
        if args.action == 'extract':
            manager.extract_messages()
        
        elif args.action == 'init':
            if not args.language:
                print("يرجى تحديد اللغة باستخدام --language")
                sys.exit(1)
            manager.init_language(args.language)
        
        elif args.action == 'update':
            manager.update_translations()
        
        elif args.action == 'compile':
            manager.compile_translations()
        
        elif args.action == 'validate':
            manager.validate_translations()
        
        elif args.action == 'stats':
            stats = manager.get_translation_stats()
            print("\n📊 إحصائيات الترجمة:")
            for lang_code, stat in stats.items():
                print(f"  {stat['name']} ({lang_code}): {stat['translated']}/{stat['total']} ({stat['percentage']}%)")
        
        elif args.action == 'full':
            manager.full_update()

if __name__ == '__main__':
    # إنشاء مجلد السجلات إذا لم يكن موجود
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    main()
