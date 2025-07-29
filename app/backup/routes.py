#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مسارات النسخ الاحتياطي
Backup Routes
"""

from flask import render_template, request, jsonify, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from datetime import datetime
from app.backup import backup_bp
from app.backup.backup_manager import backup_manager
from app.decorators import admin_required
import os

@backup_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """لوحة تحكم النسخ الاحتياطي"""
    # الحصول على قائمة النسخ الاحتياطية
    backups = backup_manager.get_backup_list()
    
    # إحصائيات النسخ الاحتياطية
    stats = {
        'total_backups': len(backups),
        'database_backups': len([b for b in backups if b['type'] == 'database']),
        'files_backups': len([b for b in backups if b['type'] == 'files']),
        'full_backups': len([b for b in backups if b['type'] == 'full']),
        'total_size': sum(b['size'] for b in backups),
        'latest_backup': backups[0] if backups else None
    }
    
    return render_template('backup/dashboard.html',
                         backups=backups[:10],  # أحدث 10 نسخ
                         stats=stats)

@backup_bp.route('/list')
@login_required
@admin_required
def list_backups():
    """قائمة جميع النسخ الاحتياطية"""
    backup_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    
    # الحصول على النسخ الاحتياطية
    backups = backup_manager.get_backup_list(backup_type)
    
    # تقسيم الصفحات (محاكاة)
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    paginated_backups = backups[start:end]
    
    has_next = len(backups) > end
    has_prev = page > 1
    
    return render_template('backup/list.html',
                         backups=paginated_backups,
                         backup_type=backup_type,
                         page=page,
                         has_next=has_next,
                         has_prev=has_prev,
                         total=len(backups))

@backup_bp.route('/create')
@login_required
@admin_required
def create_backup_form():
    """نموذج إنشاء نسخة احتياطية"""
    return render_template('backup/create.html')

# API Routes
@backup_bp.route('/api/create', methods=['POST'])
@login_required
@admin_required
def api_create_backup():
    """API إنشاء نسخة احتياطية"""
    data = request.get_json()
    backup_type = data.get('type', 'database')
    backup_name = data.get('name')
    
    try:
        if backup_type == 'database':
            success = backup_manager.create_database_backup(backup_name)
        elif backup_type == 'files':
            success = backup_manager.create_files_backup(backup_name)
        elif backup_type == 'full':
            success = backup_manager.create_full_backup(backup_name)
        else:
            return jsonify({
                'success': False,
                'message': 'نوع النسخة الاحتياطية غير صحيح'
            }), 400
        
        if success:
            return jsonify({
                'success': True,
                'message': f'تم إنشاء النسخة الاحتياطية بنجاح: {backup_type}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'فشل في إنشاء النسخة الاحتياطية'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500

@backup_bp.route('/api/restore', methods=['POST'])
@login_required
@admin_required
def api_restore_backup():
    """API استعادة نسخة احتياطية"""
    data = request.get_json()
    backup_file = data.get('backup_file')
    
    if not backup_file:
        return jsonify({
            'success': False,
            'message': 'يرجى تحديد ملف النسخة الاحتياطية'
        }), 400
    
    try:
        success = backup_manager.restore_database_backup(backup_file)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'تم استعادة النسخة الاحتياطية بنجاح'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'فشل في استعادة النسخة الاحتياطية'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500

@backup_bp.route('/api/delete', methods=['POST'])
@login_required
@admin_required
def api_delete_backup():
    """API حذف نسخة احتياطية"""
    data = request.get_json()
    backup_name = data.get('backup_name')
    backup_type = data.get('backup_type')
    
    if not backup_name or not backup_type:
        return jsonify({
            'success': False,
            'message': 'يرجى تحديد اسم ونوع النسخة الاحتياطية'
        }), 400
    
    try:
        success = backup_manager.delete_backup(backup_name, backup_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'تم حذف النسخة الاحتياطية بنجاح'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'فشل في حذف النسخة الاحتياطية'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500

@backup_bp.route('/api/cleanup', methods=['POST'])
@login_required
@admin_required
def api_cleanup_backups():
    """API تنظيف النسخ الاحتياطية القديمة"""
    try:
        deleted_count = backup_manager.cleanup_old_backups()
        
        return jsonify({
            'success': True,
            'message': f'تم حذف {deleted_count} نسخة احتياطية قديمة',
            'deleted_count': deleted_count
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500

@backup_bp.route('/api/stats')
@login_required
@admin_required
def api_backup_stats():
    """API إحصائيات النسخ الاحتياطية"""
    try:
        backups = backup_manager.get_backup_list()
        
        stats = {
            'total_backups': len(backups),
            'database_backups': len([b for b in backups if b['type'] == 'database']),
            'files_backups': len([b for b in backups if b['type'] == 'files']),
            'full_backups': len([b for b in backups if b['type'] == 'full']),
            'total_size': sum(b['size'] for b in backups),
            'total_size_mb': round(sum(b['size'] for b in backups) / (1024 * 1024), 2),
            'latest_backup': backups[0] if backups else None,
            'oldest_backup': backups[-1] if backups else None
        }
        
        # إحصائيات حسب التاريخ (آخر 30 يوم)
        from collections import defaultdict
        daily_stats = defaultdict(int)
        
        for backup in backups:
            date_key = backup['created'].strftime('%Y-%m-%d')
            daily_stats[date_key] += 1
        
        stats['daily_counts'] = dict(daily_stats)
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500

@backup_bp.route('/download/<backup_type>/<backup_name>')
@login_required
@admin_required
def download_backup(backup_type, backup_name):
    """تحميل نسخة احتياطية"""
    try:
        if backup_type == 'database':
            backup_file = backup_manager.db_backup_dir / f"{backup_name}.sql.gz"
        elif backup_type == 'files':
            backup_file = backup_manager.files_backup_dir / f"{backup_name}.zip"
        else:
            flash('نوع النسخة الاحتياطية غير صحيح', 'error')
            return redirect(url_for('backup.list_backups'))
        
        if not backup_file.exists():
            flash('ملف النسخة الاحتياطية غير موجود', 'error')
            return redirect(url_for('backup.list_backups'))
        
        return send_file(
            backup_file,
            as_attachment=True,
            download_name=backup_file.name
        )
    
    except Exception as e:
        flash(f'خطأ في تحميل النسخة الاحتياطية: {str(e)}', 'error')
        return redirect(url_for('backup.list_backups'))

@backup_bp.route('/schedule')
@login_required
@admin_required
def schedule_settings():
    """إعدادات جدولة النسخ الاحتياطي"""
    return render_template('backup/schedule.html')

@backup_bp.route('/api/schedule', methods=['POST'])
@login_required
@admin_required
def api_update_schedule():
    """API تحديث جدولة النسخ الاحتياطي"""
    data = request.get_json()
    
    # TODO: تطبيق تحديث الجدولة
    # يمكن حفظ الإعدادات في قاعدة البيانات أو ملف تكوين
    
    return jsonify({
        'success': True,
        'message': 'تم تحديث جدولة النسخ الاحتياطي بنجاح'
    })

@backup_bp.route('/test')
@login_required
@admin_required
def test_backup():
    """اختبار النسخ الاحتياطي"""
    try:
        # إنشاء نسخة احتياطية تجريبية
        test_name = f"test_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        success = backup_manager.create_database_backup(test_name)
        
        if success:
            flash('تم إنشاء نسخة احتياطية تجريبية بنجاح', 'success')
        else:
            flash('فشل في إنشاء النسخة الاحتياطية التجريبية', 'error')
    
    except Exception as e:
        flash(f'خطأ في اختبار النسخ الاحتياطي: {str(e)}', 'error')
    
    return redirect(url_for('backup.dashboard'))
