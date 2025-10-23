"""
License Core - Encrypted License Validation System
Provides tamper-resistant licensing with multiple verification layers
"""
import os
import sys
import hashlib
import base64
from datetime import datetime, timedelta
from qt_compat import QtCore


class LicenseCore:
    """Core license validation with encryption and anti-tampering"""
    
    # Encrypted expiry date (base64 encoded)
    # Actual date: 2026-01-31
    # Format: base64(reversed(timestamp))
    _ENCRYPTED_EXPIRY = "MDAwODc3OTY3MQ=="  # Obfuscated
    
    # Validation keys (scattered for obfuscation)
    _K1 = "4e45"
    _K2 = "4f5f"
    _K3 = "5343"
    _K4 = "5249"
    _K5 = "5054"
    
    # Additional obfuscation
    _SALT = "NEO_Script_Editor_v3_Beta_2025"
    
    def __init__(self):
        self.settings = QtCore.QSettings("NEO_Script_Editor", "license")
        self._validated = False
        self._expiry_cache = None
    
    @staticmethod
    def _decode_expiry():
        """Decode the encrypted expiry date"""
        try:
            # Multi-layer decoding
            decoded = base64.b64decode(LicenseCore._ENCRYPTED_EXPIRY).decode('utf-8')
            timestamp = int(decoded[::-1])  # Reverse the string
            expiry_date = datetime.fromtimestamp(timestamp)
            return expiry_date
        except Exception:
            # If decoding fails, something was tampered with
            return datetime.now() - timedelta(days=1)  # Already expired
    
    @staticmethod
    def _generate_validation_key():
        """Generate validation key from scattered components"""
        try:
            key_hex = LicenseCore._K1 + LicenseCore._K2 + LicenseCore._K3 + LicenseCore._K4 + LicenseCore._K5
            return bytes.fromhex(key_hex).decode('utf-8')
        except Exception:
            return ""
    
    @staticmethod
    def _check_integrity():
        """Check if critical files have been tampered with"""
        try:
            # Get the path to this file
            current_file = os.path.abspath(__file__)
            
            # Read this file's content
            with open(current_file, 'rb') as f:
                content = f.read()
            
            # Check for obvious tampering patterns  
            # Using byte patterns that won't match this file itself
            checks = [
                (b'IS_BETA', b'False'),  # Someone trying to disable beta
                (b'return', b'True', b'bypass'),  # Commented out checks
                (b'CRACK', b'ED'),  # Common crack marker
                (b'PATCH', b'ED'),  # Common patch marker
            ]
            
            for check in checks:
                combined = b''.join(check)
                if combined in content:
                    return False
            
            # Check if expiry date encryption is still intact
            if b'_ENCRYPTED_EXPIRY' not in content:
                return False
            
            return True
            
        except Exception:
            # If we can't read the file, assume tampering
            return False
    
    def _check_environment_bypass(self):
        """Check for common environment-based bypass attempts"""
        suspicious_vars = [
            'CRACK',
            'BYPASS',
            'PATCH',
            'UNLOCKED',
            'KEYGEN',
        ]
        
        for var in suspicious_vars:
            if os.environ.get(var):
                return False
        
        return True
    
    def _check_system_time(self):
        """Detect if system clock was rolled back"""
        try:
            # Store the last known timestamp
            last_check = self.settings.value("last_time_check", 0, type=int)
            current_time = int(datetime.now().timestamp())
            
            # If current time is significantly earlier than last check, clock was rolled back
            if last_check > 0 and current_time < (last_check - 86400):  # 1 day tolerance
                return False
            
            # Update last check
            self.settings.setValue("last_time_check", current_time)
            return True
            
        except Exception:
            return True  # Don't block on error
    
    def validate(self):
        """Main validation method - returns True if license is valid"""
        # Check 1: File integrity
        if not self._check_integrity():
            return False
        
        # Check 2: Environment bypass detection
        if not self._check_environment_bypass():
            return False
        
        # Check 3: System time manipulation
        if not self._check_system_time():
            return False
        
        # Check 4: Validation key
        expected_key = self._generate_validation_key()
        if expected_key != "NEO_SCRIPT":
            return False
        
        # Check 5: Expiry date
        if self._expiry_cache is None:
            self._expiry_cache = self._decode_expiry()
        
        if datetime.now() > self._expiry_cache:
            return False
        
        self._validated = True
        return True
    
    def is_expired(self):
        """Check if license has expired"""
        if self._expiry_cache is None:
            self._expiry_cache = self._decode_expiry()
        return datetime.now() > self._expiry_cache
    
    def days_remaining(self):
        """Get days remaining before expiry"""
        if self._expiry_cache is None:
            self._expiry_cache = self._decode_expiry()
        
        delta = self._expiry_cache - datetime.now()
        return max(0, delta.days)
    
    def get_expiry_date(self):
        """Get the expiry date"""
        if self._expiry_cache is None:
            self._expiry_cache = self._decode_expiry()
        return self._expiry_cache
    
    def get_expiry_string(self):
        """Get expiry date as string"""
        expiry = self.get_expiry_date()
        return expiry.strftime("%Y-%m-%d")
    
    @staticmethod
    def check_dev_mode():
        """Check if running in legitimate dev mode"""
        # Dev mode only valid if specific environment variable is set correctly
        dev_flag = os.environ.get('NEO_DEV_MODE', '0')
        dev_key = os.environ.get('NEO_DEV_KEY', '')
        
        # Require both flag AND key for dev mode
        if dev_flag == '1' and dev_key == LicenseCore._generate_dev_key():
            return True
        return False
    
    @staticmethod
    def _generate_dev_key():
        """Generate the required dev mode key"""
        # Hash-based key generation
        salt = LicenseCore._SALT
        raw_key = hashlib.sha256(salt.encode()).hexdigest()[:16]
        return raw_key


# Global instance for quick access
_license_instance = None

def get_license():
    """Get or create the global license instance"""
    global _license_instance
    if _license_instance is None:
        _license_instance = LicenseCore()
    return _license_instance


def validate_license():
    """Quick validation function"""
    return get_license().validate()


def is_dev_mode():
    """Check if running in dev mode"""
    return LicenseCore.check_dev_mode()
