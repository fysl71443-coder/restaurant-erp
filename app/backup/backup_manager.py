#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير النسخ الاحتياطي
Backup Manager
"""

import os
import shutil
import gzip
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import zipfile
from flask import current_app
from app import db
from app.models.system_monitoring import SystemLog
import schedule
import threading

logger = logging.getLogger('accounting_system')

class BackupManager:
    """مدير النسخ الاحتياطي"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """تهيئة مدير النسخ الاحتياطي"""
        self.app = app
        
        # إعداد مجلدات النسخ الاحتياطي
        self.backup_dir = Path(app.config.get('BACKUP_DIR', 'backups'))
        self.backup_dir.mkdir(exist_ok=True)
        
        # مجلدات فرعية
        self.db_backup_dir = self.backup_dir / 'database'
        self.files_backup_dir = self.backup_dir / 'files'
        self.full_backup_dir = self.backup_dir / 'full'
        
        for dir_path in [self.db_backup_dir, self.files_backup_dir, self.full_backup_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # إعدادات النسخ الاحتياطي
        self.max_backups = app.config.get('MAX_BACKUPS', 30)
        self.compression_level = app.config.get('BACKUP_COMPRESSION_LEVEL', 6)
        
        # جدولة النسخ الاحتياطي التلقائي
        self._schedule_automatic_backups()
    
    def create_database_backup(self, backup_name=None):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        try:
            if not backup_name:
                backup_name = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_file = self.db_backup_dir / f"{backup_name}.sql.gz"
            
            # الحصول على معلومات قاعدة البيانات
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            
            if db_uri.startswith('sqlite'):
                # نسخ احتياطي لـ SQLite
                db_path = db_uri.replace('sqlite:///', '')
                return self._backup_sqlite(db_path, backup_file)
            
            elif db_uri.startswith('postgresql'):
                # نسخ احتياطي لـ PostgreSQL
                return self._backup_postgresql(db_uri, backup_file)
            
            elif db_uri.startswith('mysql'):
                # نسخ احتياطي لـ MySQL
                return self._backup_mysql(db_uri, backup_file)
            
            else:
                raise ValueError(f"Unsupported database type: {db_uri}")
        
        except Exception as e:
            logger.error(f"Database backup failed: {str(e)}")
            return False
    
    def _backup_sqlite(self, db_path, backup_file):
        """نسخ احتياطي لقاعدة بيانات SQLite"""
        try:
            # نسخ ملف قاعدة البيانات
            with open(db_path, 'rb') as f_in:
                with gzip.open(backup_file, 'wb', compresslevel=self.compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # تسجيل النسخة الاحتياطية
            self._log_backup('database', backup_file, os.path.getsize(backup_file))
            
            logger.info(f"SQLite backup created: {backup_file}")
            return True
        
        except Exception as e:
            logger.error(f"SQLite backup failed: {str(e)}")
            return False
    
    def _backup_postgresql(self, db_uri, backup_file):
        """نسخ احتياطي لقاعدة بيانات PostgreSQL"""
        try:
            # استخراج معلومات الاتصال
            from urllib.parse import urlparse
            parsed = urlparse(db_uri)
            
            # تشغيل pg_dump
            cmd = [
                'pg_dump',
                '-h', parsed.hostname or 'localhost',
                '-p', str(parsed.port or 5432),
                '-U', parsed.username,
                '-d', parsed.path[1:],  # إزالة الشرطة المائلة الأولى
                '--no-password'
            ]
            
            # تشغيل الأمر وضغط النتيجة
            with gzip.open(backup_file, 'wb', compresslevel=self.compression_level) as f_out:
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if process.returncode == 0:
                    f_out.write(process.stdout)
                    self._log_backup('database', backup_file, os.path.getsize(backup_file))
                    logger.info(f"PostgreSQL backup created: {backup_file}")
                    return True
                else:
                    logger.error(f"pg_dump failed: {process.stderr.decode()}")
                    return False
        
        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {str(e)}")
            return False
    
    def _backup_mysql(self, db_uri, backup_file):
        """نسخ احتياطي لقاعدة بيانات MySQL"""
        try:
            # استخراج معلومات الاتصال
            from urllib.parse import urlparse
            parsed = urlparse(db_uri)
            
            # تشغيل mysqldump
            cmd = [
                'mysqldump',
                '-h', parsed.hostname or 'localhost',
                '-P', str(parsed.port or 3306),
                '-u', parsed.username,
                f'-p{parsed.password}' if parsed.password else '',
                parsed.path[1:]  # إزالة الشرطة المائلة الأولى
            ]
            
            # تشغيل الأمر وضغط النتيجة
            with gzip.open(backup_file, 'wb', compresslevel=self.compression_level) as f_out:
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if process.returncode == 0:
                    f_out.write(process.stdout)
                    self._log_backup('database', backup_file, os.path.getsize(backup_file))
                    logger.info(f"MySQL backup created: {backup_file}")
                    return True
                else:
                    logger.error(f"mysqldump failed: {process.stderr.decode()}")
                    return False
        
        except Exception as e:
            logger.error(f"MySQL backup failed: {str(e)}")
            return False
    
    def create_files_backup(self, backup_name=None):
        """إنشاء نسخة احتياطية من الملفات"""
        try:
            if not backup_name:
                backup_name = f"files_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_file = self.files_backup_dir / f"{backup_name}.zip"
            
            # مجلدات الملفات المهمة
            important_dirs = [
                'app/static/uploads',
                'app/static/reports',
                'logs',
                'config'
            ]
            
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for dir_name in important_dirs:
                    dir_path = Path(dir_name)
                    if dir_path.exists():
                        for file_path in dir_path.rglob('*'):
                            if file_path.is_file():
                                arcname = str(file_path.relative_to('.'))
                                zipf.write(file_path, arcname)
            
            # تسجيل النسخة الاحتياطية
            self._log_backup('files', backup_file, os.path.getsize(backup_file))
            
            logger.info(f"Files backup created: {backup_file}")
            return True
        
        except Exception as e:
            logger.error(f"Files backup failed: {str(e)}")
            return False
    
    def create_full_backup(self, backup_name=None):
        """إنشاء نسخة احتياطية كاملة"""
        try:
            if not backup_name:
                backup_name = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # إنشاء نسخة احتياطية من قاعدة البيانات
            db_success = self.create_database_backup(f"{backup_name}_db")
            
            # إنشاء نسخة احتياطية من الملفات
            files_success = self.create_files_backup(f"{backup_name}_files")
            
            if db_success and files_success:
                # إنشاء ملف معلومات النسخة الاحتياطية
                backup_info = {
                    'name': backup_name,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'full',
                    'database_backup': f"{backup_name}_db.sql.gz",
                    'files_backup': f"{backup_name}_files.zip",
                    'app_version': current_app.config.get('APP_VERSION', '1.0.0'),
                    'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
                }
                
                info_file = self.full_backup_dir / f"{backup_name}_info.json"
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_info, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Full backup created: {backup_name}")
                return True
            else:
                logger.error("Full backup failed: database or files backup failed")
                return False
        
        except Exception as e:
            logger.error(f"Full backup failed: {str(e)}")
            return False
    
    def restore_database_backup(self, backup_file):
        """استعادة نسخة احتياطية من قاعدة البيانات"""
        try:
            backup_path = self.db_backup_dir / backup_file
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            # الحصول على معلومات قاعدة البيانات
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            
            if db_uri.startswith('sqlite'):
                return self._restore_sqlite(backup_path)
            elif db_uri.startswith('postgresql'):
                return self._restore_postgresql(backup_path, db_uri)
            elif db_uri.startswith('mysql'):
                return self._restore_mysql(backup_path, db_uri)
            else:
                raise ValueError(f"Unsupported database type: {db_uri}")
        
        except Exception as e:
            logger.error(f"Database restore failed: {str(e)}")
            return False
    
    def _restore_sqlite(self, backup_file):
        """استعادة قاعدة بيانات SQLite"""
        try:
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            db_path = db_uri.replace('sqlite:///', '')
            
            # إنشاء نسخة احتياطية من قاعدة البيانات الحالية
            current_backup = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_path, current_backup)
            
            # استعادة النسخة الاحتياطية
            with gzip.open(backup_file, 'rb') as f_in:
                with open(db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"SQLite database restored from: {backup_file}")
            return True
        
        except Exception as e:
            logger.error(f"SQLite restore failed: {str(e)}")
            return False
    
    def get_backup_list(self, backup_type='all'):
        """الحصول على قائمة النسخ الاحتياطية"""
        backups = []
        
        try:
            if backup_type in ['all', 'database']:
                for backup_file in self.db_backup_dir.glob('*.sql.gz'):
                    backups.append({
                        'name': backup_file.stem.replace('.sql', ''),
                        'type': 'database',
                        'file': backup_file.name,
                        'size': backup_file.stat().st_size,
                        'created': datetime.fromtimestamp(backup_file.stat().st_mtime),
                        'path': str(backup_file)
                    })
            
            if backup_type in ['all', 'files']:
                for backup_file in self.files_backup_dir.glob('*.zip'):
                    backups.append({
                        'name': backup_file.stem,
                        'type': 'files',
                        'file': backup_file.name,
                        'size': backup_file.stat().st_size,
                        'created': datetime.fromtimestamp(backup_file.stat().st_mtime),
                        'path': str(backup_file)
                    })
            
            if backup_type in ['all', 'full']:
                for info_file in self.full_backup_dir.glob('*_info.json'):
                    with open(info_file, 'r', encoding='utf-8') as f:
                        backup_info = json.load(f)
                    
                    backups.append({
                        'name': backup_info['name'],
                        'type': 'full',
                        'file': info_file.name,
                        'size': info_file.stat().st_size,
                        'created': datetime.fromisoformat(backup_info['timestamp']),
                        'path': str(info_file),
                        'info': backup_info
                    })
            
            # ترتيب حسب التاريخ (الأحدث أولاً)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get backup list: {str(e)}")
        
        return backups
    
    def delete_backup(self, backup_name, backup_type):
        """حذف نسخة احتياطية"""
        try:
            if backup_type == 'database':
                backup_file = self.db_backup_dir / f"{backup_name}.sql.gz"
            elif backup_type == 'files':
                backup_file = self.files_backup_dir / f"{backup_name}.zip"
            elif backup_type == 'full':
                # حذف جميع ملفات النسخة الاحتياطية الكاملة
                info_file = self.full_backup_dir / f"{backup_name}_info.json"
                db_file = self.db_backup_dir / f"{backup_name}_db.sql.gz"
                files_file = self.files_backup_dir / f"{backup_name}_files.zip"
                
                for file_path in [info_file, db_file, files_file]:
                    if file_path.exists():
                        file_path.unlink()
                
                logger.info(f"Full backup deleted: {backup_name}")
                return True
            else:
                raise ValueError(f"Invalid backup type: {backup_type}")
            
            if backup_file.exists():
                backup_file.unlink()
                logger.info(f"Backup deleted: {backup_file}")
                return True
            else:
                logger.warning(f"Backup file not found: {backup_file}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to delete backup: {str(e)}")
            return False
    
    def cleanup_old_backups(self):
        """تنظيف النسخ الاحتياطية القديمة"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.max_backups)
            deleted_count = 0
            
            # تنظيف نسخ قاعدة البيانات
            for backup_file in self.db_backup_dir.glob('*.sql.gz'):
                if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            
            # تنظيف نسخ الملفات
            for backup_file in self.files_backup_dir.glob('*.zip'):
                if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            
            # تنظيف النسخ الكاملة
            for info_file in self.full_backup_dir.glob('*_info.json'):
                if datetime.fromtimestamp(info_file.stat().st_mtime) < cutoff_date:
                    # حذف جميع ملفات النسخة الاحتياطية
                    backup_name = info_file.stem.replace('_info', '')
                    self.delete_backup(backup_name, 'full')
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Backup cleanup failed: {str(e)}")
            return 0
    
    def _log_backup(self, backup_type, backup_file, file_size):
        """تسجيل النسخة الاحتياطية في قاعدة البيانات"""
        try:
            SystemLog.log_event(
                level='INFO',
                logger_name='backup_manager',
                message=f"Backup created: {backup_type} - {backup_file.name}",
                extra_data={
                    'backup_type': backup_type,
                    'backup_file': str(backup_file),
                    'file_size': file_size,
                    'timestamp': datetime.now().isoformat()
                }
            )
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to log backup: {str(e)}")
    
    def _schedule_automatic_backups(self):
        """جدولة النسخ الاحتياطي التلقائي"""
        # نسخة احتياطية يومية لقاعدة البيانات
        schedule.every().day.at("02:00").do(self.create_database_backup)
        
        # نسخة احتياطية أسبوعية للملفات
        schedule.every().sunday.at("03:00").do(self.create_files_backup)
        
        # نسخة احتياطية شهرية كاملة
        schedule.every().month.do(self.create_full_backup)
        
        # تنظيف النسخ القديمة أسبوعياً
        schedule.every().sunday.at("04:00").do(self.cleanup_old_backups)
        
        # تشغيل المجدول في خيط منفصل
        def run_scheduler():
            while True:
                schedule.run_pending()
                import time
                time.sleep(60)  # فحص كل دقيقة
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("Automatic backup scheduler started")

# إنشاء مثيل مدير النسخ الاحتياطي
backup_manager = BackupManager()
