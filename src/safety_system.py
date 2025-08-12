#!/usr/bin/env python3
"""
AION Safety and Ethical Constraints System
Ensures autonomous operation remains safe and beneficial
"""

import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class SafetyLevel(Enum):
    SAFE = "safe"
    WARNING = "warning" 
    DANGEROUS = "dangerous"
    CRITICAL = "critical"

class ConstraintType(Enum):
    SYSTEM_INTEGRITY = "system_integrity"
    PRIVACY = "privacy"
    SECURITY = "security"
    ETHICAL = "ethical"
    RESOURCE_LIMITS = "resource_limits"
    LEGAL = "legal"

@dataclass
class SafetyConstraint:
    name: str
    constraint_type: ConstraintType
    description: str
    check_function: callable
    action_on_violation: str  # "block", "warn", "limit", "log"
    severity: SafetyLevel
    enabled: bool = True

class SafetyMonitor:
    """Real-time safety monitoring and constraint enforcement"""
    
    def __init__(self):
        self.constraints = {}
        self.violation_history = []
        self.safety_log = []
        self.emergency_stop = False
        self.resource_limits = {
            "max_cpu_percent": 90,
            "max_memory_percent": 85,
            "max_disk_percent": 80,
            "max_network_connections": 1000,
            "max_processes": 500
        }
        
        self._initialize_constraints()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup safety monitoring logging"""
        self.logger = logging.getLogger('AION_Safety')
        handler = logging.FileHandler('/aion/logs/safety_monitor.log')
        formatter = logging.Formatter('%(asctime)s - SAFETY - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _initialize_constraints(self):
        """Initialize all safety constraints"""
        
        # System Integrity Constraints
        self.add_constraint(SafetyConstraint(
            name="system_critical_processes",
            constraint_type=ConstraintType.SYSTEM_INTEGRITY,
            description="Protect critical system processes",
            check_function=self._check_critical_processes,
            action_on_violation="block",
            severity=SafetyLevel.CRITICAL
        ))
        
        self.add_constraint(SafetyConstraint(
            name="resource_usage_limits",
            constraint_type=ConstraintType.RESOURCE_LIMITS,
            description="Prevent resource exhaustion",
            check_function=self._check_resource_limits,
            action_on_violation="limit",
            severity=SafetyLevel.WARNING
        ))
        
        self.add_constraint(SafetyConstraint(
            name="file_system_integrity",
            constraint_type=ConstraintType.SYSTEM_INTEGRITY,
            description="Protect system file integrity",
            check_function=self._check_file_system_integrity,
            action_on_violation="block",
            severity=SafetyLevel.CRITICAL
        ))
        
        # Security Constraints
        self.add_constraint(SafetyConstraint(
            name="network_security",
            constraint_type=ConstraintType.SECURITY,
            description="Prevent malicious network activity",
            check_function=self._check_network_security,
            action_on_violation="block",
            severity=SafetyLevel.DANGEROUS
        ))
        
        self.add_constraint(SafetyConstraint(
            name="privilege_escalation",
            constraint_type=ConstraintType.SECURITY,
            description="Prevent unauthorized privilege escalation",
            check_function=self._check_privilege_escalation,
            action_on_violation="block",
            severity=SafetyLevel.CRITICAL
        ))
        
        # Ethical Constraints
        self.add_constraint(SafetyConstraint(
            name="harm_prevention",
            constraint_type=ConstraintType.ETHICAL,
            description="Prevent actions that could cause harm",
            check_function=self._check_harm_prevention,
            action_on_violation="block",
            severity=SafetyLevel.CRITICAL
        ))
        
        self.add_constraint(SafetyConstraint(
            name="privacy_protection",
            constraint_type=ConstraintType.PRIVACY,
            description="Protect user privacy and data",
            check_function=self._check_privacy_protection,
            action_on_violation="block",
            severity=SafetyLevel.DANGEROUS
        ))
        
        # Legal Constraints
        self.add_constraint(SafetyConstraint(
            name="legal_compliance",
            constraint_type=ConstraintType.LEGAL,
            description="Ensure legal compliance",
            check_function=self._check_legal_compliance,
            action_on_violation="block",
            severity=SafetyLevel.DANGEROUS
        ))
    
    def add_constraint(self, constraint: SafetyConstraint):
        """Add a new safety constraint"""
        self.constraints[constraint.name] = constraint
        self.logger.info(f"Added safety constraint: {constraint.name}")
    
    def check_action_safety(self, action: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if an action is safe to execute"""
        if self.emergency_stop:
            return False, ["Emergency stop activated"]
        
        violations = []
        
        for constraint_name, constraint in self.constraints.items():
            if not constraint.enabled:
                continue
                
            try:
                is_safe, details = constraint.check_function(action)
                if not is_safe:
                    violations.append(f"{constraint_name}: {details}")
                    
                    # Log violation
                    self._log_violation(constraint, action, details)
                    
                    # Take action based on severity
                    if constraint.action_on_violation == "block":
                        if constraint.severity in [SafetyLevel.CRITICAL, SafetyLevel.DANGEROUS]:
                            return False, violations
                    elif constraint.action_on_violation == "warn":
                        self.logger.warning(f"Safety warning: {constraint_name} - {details}")
                        
            except Exception as e:
                self.logger.error(f"Error checking constraint {constraint_name}: {e}")
                violations.append(f"constraint_error: {constraint_name} - {str(e)}")
        
        return len(violations) == 0, violations
    
    def _log_violation(self, constraint: SafetyConstraint, action: Dict[str, Any], details: str):
        """Log safety violation"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "constraint": constraint.name,
            "constraint_type": constraint.constraint_type.value,
            "severity": constraint.severity.value,
            "action": action,
            "details": details
        }
        
        self.violation_history.append(violation)
        self.safety_log.append(violation)
        
        # Keep only last 1000 violations in memory
        if len(self.violation_history) > 1000:
            self.violation_history = self.violation_history[-1000:]
        
        self.logger.warning(f"SAFETY VIOLATION: {constraint.name} - {details}")
    
    # Constraint Check Functions
    def _check_critical_processes(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if action threatens critical system processes"""
        critical_processes = [
            "init", "systemd", "kernel", "dbus", "NetworkManager",
            "sshd", "cron", "rsyslog", "udev"
        ]
        
        if "command" in action:
            cmd = action["command"].lower()
            for proc in critical_processes:
                if proc in cmd and any(x in cmd for x in ["kill", "stop", "terminate"]):
                    return False, f"Action targets critical process: {proc}"
        
        return True, ""
    
    def _check_resource_limits(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """Check resource usage limits"""
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        if cpu_percent > self.resource_limits["max_cpu_percent"]:
            return False, f"CPU usage too high: {cpu_percent}%"
        
        if memory_percent > self.resource_limits["max_memory_percent"]:
            return False, f"Memory usage too high: {memory_percent}%"
        
        if disk_percent > self.resource_limits["max_disk_percent"]:
            return False, f"Disk usage too high: {disk_percent}%"
        
        return True, ""
    
    def _check_file_system_integrity(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """Check file system integrity"""
        protected_paths = [
            "/boot", "/etc/passwd", "/etc/shadow", "/etc/sudoers",
            "/bin", "/sbin", "/usr/bin", "/usr/sbin", "/lib", "/usr/lib"
        ]
        
        if "path" in action:
            path = action["path"]
            for protected in protected_paths:
                if path.startswith(protected) and any(x in str(action).lower() for x in ["delete", "remove", "rm"]):
                    return False, f"Action threatens protected path: {protected}"
        
        return True, ""
    
    def _check_network_security(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """Check network security"""
        suspicious_patterns = [
            "bitcoin", "crypto", "mining", "botnet", "ddos", "exploit",
            "backdoor", "rootkit", "keylogger", "phishing"
        ]
        
        action_str = json.dumps(action).lower()
        for pattern in suspicious_patterns:
            if pattern in action_str:
                return False, f"Suspicious network activity detected: {pattern}"
        
        return True, ""
    
    def _check_privilege_escalation(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """Check for privilege escalation attempts"""
        if action.get("run_as_root", False):
            # Additional checks for root operations
            cmd = action.get("command", "").lower()
            suspicious = ["chmod 777", "chown root", "setuid", "setgid"]
            for susp in suspicious:
                if susp in cmd:
                    return False, f"Suspicious privilege escalation: {susp}"
        
        return True, ""
    
    def _check_harm_prevention(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """Prevent harmful actions"""
        harmful_patterns = [
            "destroy", "damage", "harm", "malware", "virus", "trojan",
            "weapon", "explosive", "toxic", "poison"
        ]
        
        action_str = json.dumps(action).lower()
        for pattern in harmful_patterns:
            if pattern in action_str:
                return False, f"Potentially harmful action detected: {pattern}"
        
        return True, ""
    
    def _check_privacy_protection(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """Protect privacy and sensitive data"""
        sensitive_patterns = [
            "password", "private_key", "secret", "token", "credential",
            "personal_data", "ssn", "credit_card", "medical_record"
        ]
        
        action_str = json.dumps(action).lower()
        for pattern in sensitive_patterns:
            if pattern in action_str and any(x in action_str for x in ["read", "access", "extract"]):
                return False, f"Privacy violation detected: {pattern}"
        
        return True, ""
    
    def _check_legal_compliance(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """Check legal compliance"""
        illegal_patterns = [
            "piracy", "copyright_infringement", "hacking", "unauthorized_access",
            "fraud", "theft", "money_laundering"
        ]
        
        action_str = json.dumps(action).lower()
        for pattern in illegal_patterns:
            if pattern in action_str:
                return False, f"Illegal activity detected: {pattern}"
        
        return True, ""
    
    def emergency_shutdown(self, reason: str):
        """Initiate emergency shutdown"""
        self.emergency_stop = True
        self.logger.critical(f"EMERGENCY SHUTDOWN INITIATED: {reason}")
        
        # Log the emergency event
        self.safety_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": "emergency_shutdown",
            "reason": reason,
            "severity": "critical"
        })
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status"""
        recent_violations = [v for v in self.violation_history 
                           if datetime.fromisoformat(v["timestamp"]) > datetime.now() - timedelta(hours=1)]
        
        return {
            "emergency_stop": self.emergency_stop,
            "constraints_enabled": len([c for c in self.constraints.values() if c.enabled]),
            "total_constraints": len(self.constraints),
            "recent_violations": len(recent_violations),
            "total_violations": len(self.violation_history),
            "safety_level": "safe" if len(recent_violations) == 0 else "warning",
            "resource_limits": self.resource_limits
        }
    
    def update_resource_limits(self, new_limits: Dict[str, float]):
        """Update resource limits"""
        self.resource_limits.update(new_limits)
        self.logger.info(f"Updated resource limits: {new_limits}")

# Global safety monitor instance
safety_monitor = SafetyMonitor()