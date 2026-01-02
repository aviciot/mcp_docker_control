"""
Audit Logger
============
Logs all Docker operations for security and compliance
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logger for Docker operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.audit_enabled = config.get('docker', {}).get('audit', {}).get('enabled', True)
        
        if self.audit_enabled:
            # Get audit log path
            log_path = config.get('docker', {}).get('audit', {}).get('log_path', 'logs/audit.log')
            self.log_file = Path(log_path)
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Audit logging enabled: {self.log_file}")
        else:
            self.log_file = None
            logger.info("Audit logging disabled")
    
    def log_operation(
        self,
        operation: str,
        container: Optional[str] = None,
        user: str = "system",
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Log a Docker operation
        
        Args:
            operation: Operation name (e.g., "start", "stop", "restart")
            container: Container ID or name
            user: User who performed the operation
            success: Whether the operation succeeded
            details: Additional operation details
            error: Error message if operation failed
        """
        if not self.audit_enabled:
            return
        
        # Create audit entry
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'container': container,
            'user': user,
            'success': success,
        }
        
        if details:
            entry['details'] = details
        
        if error:
            entry['error'] = error
        
        # Write to audit log
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def close(self):
        """Close audit logger"""
        if self.audit_enabled:
            logger.info("Audit logger closed")


# Global audit logger instance (initialized in server.py)
_audit_logger: Optional[AuditLogger] = None


def set_audit_logger(audit_logger: AuditLogger):
    """Set global audit logger instance"""
    global _audit_logger
    _audit_logger = audit_logger


def get_audit_logger() -> Optional[AuditLogger]:
    """Get global audit logger instance"""
    return _audit_logger


def log_audit(
    operation: str,
    container: Optional[str] = None,
    user: str = "system",
    success: bool = True,
    details: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    """Convenience function to log audit entry"""
    audit_logger = get_audit_logger()
    if audit_logger:
        audit_logger.log_operation(operation, container, user, success, details, error)
