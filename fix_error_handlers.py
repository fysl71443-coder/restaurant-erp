#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إصلاح معالجات الأخطاء في app.py
Fix Error Handlers in app.py
"""

import re

def fix_error_handlers():
    """إصلاح جميع معالجات الأخطاء في app.py"""
    
    print("🔧 بدء إصلاح معالجات الأخطاء...")
    
    # قراءة الملف
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن جميع معالجات الأخطاء وإصلاحها
    patterns_to_fix = [
        # نمط: except Exception as e: (بدون استخدام e)
        (r'except Exception as e:\s*\n(\s*)# ([^\n]+)\n(\s*)flash\(([^\n]+)\)\n(\s*)db\.session\.rollback\(\)',
         r'except Exception as e:\n\1# \2\n\1logger.error(f"خطأ: {str(e)}")\n\3flash(\4)\n\5db.session.rollback()'),
        
        (r'except Exception as e:\s*\n(\s*)flash\(([^\n]+)\)\n(\s*)db\.session\.rollback\(\)',
         r'except Exception as e:\n\1logger.error(f"خطأ: {str(e)}")\n\1flash(\2)\n\3db.session.rollback()'),
        
        (r'except Exception as e:\s*\n(\s*)# ([^\n]+)\n(\s*)return render_template\(([^\n]+)\)',
         r'except Exception as e:\n\1# \2\n\1logger.error(f"خطأ: {str(e)}")\n\3return render_template(\4)'),
        
        (r'except Exception as e:\s*\n(\s*)return render_template\(([^\n]+)\)',
         r'except Exception as e:\n\1logger.error(f"خطأ: {str(e)}")\n\1return render_template(\2)'),
        
        (r'except Exception as e:\s*\n(\s*)flash\(([^\n]+)\)\n(\s*)return redirect\(([^\n]+)\)',
         r'except Exception as e:\n\1logger.error(f"خطأ: {str(e)}")\n\1flash(\2)\n\3return redirect(\4)'),
    ]
    
    # تطبيق الإصلاحات
    fixed_count = 0
    for pattern, replacement in patterns_to_fix:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            fixed_count += len(matches)
            print(f"✅ تم إصلاح {len(matches)} معالج خطأ من النوع: {pattern[:50]}...")
    
    # إصلاح الحالات الخاصة
    special_fixes = [
        # إصلاح متغير notes غير المستخدم
        (r'notes = request\.form\.get\(\'notes\'\)\s*\n\s*new_invoice = Invoice\(',
         'new_invoice = Invoice('),
        
        # إضافة notes للفاتورة إذا كان موجوداً
        (r'new_invoice = Invoice\(\s*customer_name=customer_name,\s*total_amount=total_amount,\s*date=datetime\.strptime\(invoice_date, \'%Y-%m-%d\'\) if invoice_date else datetime\.now\(\)\s*\)',
         '''notes = request.form.get('notes')
            new_invoice = Invoice(
                customer_name=customer_name,
                total_amount=total_amount,
                date=datetime.strptime(invoice_date, '%Y-%m-%d') if invoice_date else datetime.now(),
                notes=notes
            )'''),
    ]
    
    for pattern, replacement in special_fixes:
        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            fixed_count += 1
            print(f"✅ تم إصلاح حالة خاصة")
    
    # حفظ الملف المُحدث
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🎉 تم إصلاح {fixed_count} معالج خطأ في app.py")
    return fixed_count

if __name__ == "__main__":
    fix_error_handlers()
