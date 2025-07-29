#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مسارات اللغات
Language Routes
"""

from flask import request, redirect, url_for, session, flash, current_app, jsonify
from flask_login import current_user
from flask_babel import refresh, gettext as _
from app import db
from app.language import language_bp

@language_bp.route('/set/<language>')
def set_language(language):
    """تغيير لغة الواجهة"""
    # التحقق من صحة اللغة
    if language not in current_app.config['LANGUAGES']:
        flash(_('اللغة المطلوبة غير مدعومة'), 'error')
        return redirect(request.referrer or url_for('main.index'))
    
    # حفظ اللغة في الجلسة
    session['language'] = language
    
    # إذا كان المستخدم مسجل دخول، حفظ اللغة في ملفه الشخصي
    if current_user.is_authenticated:
        try:
            current_user.preferred_language = language
            db.session.commit()
            flash(_('تم تغيير اللغة بنجاح'), 'success')
        except Exception as e:
            db.session.rollback()
            flash(_('حدث خطأ أثناء حفظ اللغة'), 'error')
    else:
        flash(_('تم تغيير اللغة مؤقتاً'), 'info')
    
    # تحديث الترجمة
    refresh()
    
    # العودة للصفحة السابقة أو الرئيسية
    return redirect(request.referrer or url_for('main.index'))

@language_bp.route('/api/set', methods=['POST'])
def api_set_language():
    """تغيير اللغة عبر API"""
    data = request.get_json()
    
    if not data or 'language' not in data:
        return jsonify({
            'success': False,
            'message': _('يرجى تحديد اللغة')
        }), 400
    
    language = data['language']
    
    # التحقق من صحة اللغة
    if language not in current_app.config['LANGUAGES']:
        return jsonify({
            'success': False,
            'message': _('اللغة المطلوبة غير مدعومة')
        }), 400
    
    # حفظ اللغة في الجلسة
    session['language'] = language
    
    # إذا كان المستخدم مسجل دخول، حفظ اللغة في ملفه الشخصي
    if current_user.is_authenticated:
        try:
            current_user.preferred_language = language
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': _('حدث خطأ أثناء حفظ اللغة')
            }), 500
    
    # تحديث الترجمة
    refresh()
    
    return jsonify({
        'success': True,
        'message': _('تم تغيير اللغة بنجاح'),
        'language': language,
        'language_name': current_app.config['LANGUAGES'][language]
    })

@language_bp.route('/api/current')
def api_current_language():
    """الحصول على اللغة الحالية"""
    from flask_babel import get_locale
    
    current_locale = str(get_locale())
    
    return jsonify({
        'current_language': current_locale,
        'current_language_name': current_app.config['LANGUAGES'].get(current_locale, 'غير معروف'),
        'available_languages': current_app.config['LANGUAGES'],
        'default_language': current_app.config['DEFAULT_LANGUAGE']
    })

@language_bp.route('/api/translations/<domain>')
def api_get_translations(domain='messages'):
    """الحصول على ترجمات JavaScript"""
    from flask_babel import get_locale
    import json
    import os
    
    current_locale = str(get_locale())
    
    # مسار ملف الترجمة
    translations_file = os.path.join(
        current_app.root_path,
        'translations',
        current_locale,
        'LC_MESSAGES',
        f'{domain}.json'
    )
    
    translations = {}
    
    # قراءة ملف الترجمة إذا كان موجود
    if os.path.exists(translations_file):
        try:
            with open(translations_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
        except Exception as e:
            current_app.logger.error(f'Error loading translations: {e}')
    
    return jsonify({
        'locale': current_locale,
        'domain': domain,
        'translations': translations
    })

@language_bp.route('/direction')
def get_text_direction():
    """الحصول على اتجاه النص للغة الحالية"""
    from flask_babel import get_locale
    
    current_locale = str(get_locale())
    
    # اللغات التي تكتب من اليمين لليسار
    rtl_languages = ['ar', 'he', 'fa', 'ur']
    
    direction = 'rtl' if current_locale in rtl_languages else 'ltr'
    
    return jsonify({
        'locale': current_locale,
        'direction': direction,
        'is_rtl': direction == 'rtl'
    })

@language_bp.context_processor
def inject_language_vars():
    """حقن متغيرات اللغة في جميع القوالب"""
    from flask_babel import get_locale
    
    current_locale = str(get_locale())
    rtl_languages = ['ar', 'he', 'fa', 'ur']
    
    return {
        'current_language': current_locale,
        'current_language_name': current_app.config['LANGUAGES'].get(current_locale, 'Unknown'),
        'available_languages': current_app.config['LANGUAGES'],
        'is_rtl': current_locale in rtl_languages,
        'text_direction': 'rtl' if current_locale in rtl_languages else 'ltr'
    }
