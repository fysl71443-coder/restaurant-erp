#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الأمان المتقدم
Advanced Security System
"""

from app.security.decorators import (
    permission_required,
    role_required,
    rate_limit,
    audit_log,
    csrf_protect,
    secure_headers
)

from app.security.validators import (
    validate_password_strength,
    validate_email_format,
    validate_phone_number,
    sanitize_input,
    check_sql_injection,
    check_xss_attempt
)

from app.security.encryption import (
    encrypt_sensitive_data,
    decrypt_sensitive_data,
    hash_password,
    verify_password,
    generate_secure_token,
    generate_csrf_token
)

from app.security.monitoring import (
    SecurityMonitor,
    detect_suspicious_activity,
    log_security_event,
    check_ip_reputation,
    rate_limit_exceeded
)

__all__ = [
    # Decorators
    'permission_required',
    'role_required', 
    'rate_limit',
    'audit_log',
    'csrf_protect',
    'secure_headers',
    
    # Validators
    'validate_password_strength',
    'validate_email_format',
    'validate_phone_number',
    'sanitize_input',
    'check_sql_injection',
    'check_xss_attempt',
    
    # Encryption
    'encrypt_sensitive_data',
    'decrypt_sensitive_data',
    'hash_password',
    'verify_password',
    'generate_secure_token',
    'generate_csrf_token',
    
    # Monitoring
    'SecurityMonitor',
    'detect_suspicious_activity',
    'log_security_event',
    'check_ip_reputation',
    'rate_limit_exceeded'
]
