#!/usr/bin/env python3
"""
AION Health Monitoring & Self-Healing System
Ensures continuous operation and self-recovery
"""

import os
import sys
import psutil
import asyncio
import subprocess
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import signal
import threading
import time

logger = logging.getLogger('AION_Health')

class HealthMonitor:
    """
    Monitors system health and performs self-healing actions
    """
    
    def __init__(self):
        self.health_status = {
            "status": "initializing",
            "last_check": None,
            "issues": [],
            "auto_healed": []
        }
        self.monitoring = False
        self.service_url = "http://127.0.0.1:30001"
        self.critical_processes = {
            "autonomy_toolbelt": "python.*full_autonomy_toolbelt",
            "glm45": "sglang.*GLM-4.5",
        }
        self.health_checks = {
            "api_responsive": self.check_api_health,
            "memory_available": self.check_memory,
            "disk_space": self.check_disk,
            "cpu_usage": self.check_cpu,
            "gpu_health": self.check_gpu,
            "critical_processes": self.check_processes,
            "network_connectivity": self.check_network
        }
        
    async def check_api_health(self) -> Dict[str, Any]:
        """Check if the API is responsive"""
        try:
            response = requests.get(f"{self.service_url}/health", timeout=5)
            if response.status_code == 200:
                return {"healthy": True, "status": "API responsive"}
            else:
                return {"healthy": False, "issue": f"API returned {response.status_code}"}
        except Exception as e:
            return {"healthy": False, "issue": f"API unreachable: {str(e)}"}
    
    async def check_memory(self) -> Dict[str, Any]:
        """Check memory availability"""
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            # Try to free memory
            await self.free_memory()
            return {"healthy": False, "issue": f"Memory usage critical: {mem.percent}%", "action": "freed_memory"}
        elif mem.percent > 75:
            return {"healthy": True, "warning": f"Memory usage high: {mem.percent}%"}
        return {"healthy": True, "status": f"Memory OK: {mem.percent}%"}
    
    async def check_disk(self) -> Dict[str, Any]:
        """Check disk space"""
        disk = psutil.disk_usage('/')
        if disk.percent > 95:
            await self.cleanup_disk()
            return {"healthy": False, "issue": f"Disk usage critical: {disk.percent}%", "action": "cleaned_disk"}
        elif disk.percent > 85:
            return {"healthy": True, "warning": f"Disk usage high: {disk.percent}%"}
        return {"healthy": True, "status": f"Disk OK: {disk.percent}%"}
    
    async def check_cpu(self) -> Dict[str, Any]:
        """Check CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 95:
            return {"healthy": False, "issue": f"CPU overloaded: {cpu_percent}%"}
        elif cpu_percent > 80:
            return {"healthy": True, "warning": f"CPU usage high: {cpu_percent}%"}
        return {"healthy": True, "status": f"CPU OK: {cpu_percent}%"}
    
    async def check_gpu(self) -> Dict[str, Any]:
        """Check GPU health"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse GPU stats
                lines = result.stdout.strip().split('\n')
                gpu_issues = []
                
                for i, line in enumerate(lines):
                    util, mem_used, mem_total, temp = map(float, line.split(','))
                    
                    if temp > 85:
                        gpu_issues.append(f"GPU{i} temp high: {temp}°C")
                    if util > 95:
                        gpu_issues.append(f"GPU{i} overloaded: {util}%")
                
                if gpu_issues:
                    return {"healthy": False, "issues": gpu_issues}
                return {"healthy": True, "status": "All GPUs healthy"}
            else:
                return {"healthy": False, "issue": "Cannot query GPU status"}
                
        except Exception as e:
            return {"healthy": True, "status": "No GPU monitoring available"}
    
    async def check_processes(self) -> Dict[str, Any]:
        """Check if critical processes are running"""
        issues = []
        
        for name, pattern in self.critical_processes.items():
            found = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if pattern in cmdline:
                        found = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not found:
                # Try to restart the process
                await self.restart_process(name)
                issues.append(f"Process {name} was down - attempted restart")
        
        if issues:
            return {"healthy": False, "issues": issues, "action": "restarted_processes"}
        return {"healthy": True, "status": "All critical processes running"}
    
    async def check_network(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                return {"healthy": True, "status": "Network connected"}
        except:
            pass
        
        return {"healthy": False, "issue": "No internet connectivity"}
    
    async def free_memory(self):
        """Free up memory"""
        # Clear Python caches
        import gc
        gc.collect()
        
        # Clear system caches (Linux)
        try:
            subprocess.run(["sudo", "sync"], timeout=5)
            subprocess.run(["sudo", "sh", "-c", "echo 1 > /proc/sys/vm/drop_caches"], timeout=5)
            logger.info("Memory caches cleared")
        except:
            pass
    
    async def cleanup_disk(self):
        """Clean up disk space"""
        # Remove old logs
        log_dir = Path("/aion/logs")
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < time.time() - 7 * 24 * 3600:  # 7 days old
                    log_file.unlink()
                    logger.info(f"Deleted old log: {log_file}")
        
        # Clear temp files
        try:
            subprocess.run(["sudo", "rm", "-rf", "/tmp/*"], shell=True, timeout=10)
        except:
            pass
    
    async def restart_process(self, process_name: str):
        """Restart a critical process"""
        if process_name == "autonomy_toolbelt":
            # Restart the autonomy service
            try:
                subprocess.run(["sudo", "systemctl", "restart", "aion-autonomy"], timeout=10)
                logger.info("Restarted autonomy toolbelt via systemd")
            except:
                # Fallback to direct start
                subprocess.Popen([
                    sys.executable,
                    "/opt/aion/full_autonomy_toolbelt.py"
                ], start_new_session=True)
                logger.info("Started autonomy toolbelt directly")
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform all health checks"""
        results = {}
        issues = []
        actions_taken = []
        
        for check_name, check_func in self.health_checks.items():
            try:
                result = await check_func()
                results[check_name] = result
                
                if not result.get("healthy", True):
                    issues.append(f"{check_name}: {result.get('issue', 'unhealthy')}")
                    if "action" in result:
                        actions_taken.append(result["action"])
                        
            except Exception as e:
                results[check_name] = {"healthy": False, "error": str(e)}
                issues.append(f"{check_name}: error - {str(e)}")
        
        overall_health = "healthy" if len(issues) == 0 else "degraded" if len(issues) < 3 else "critical"
        
        self.health_status = {
            "status": overall_health,
            "last_check": datetime.now().isoformat(),
            "issues": issues,
            "auto_healed": actions_taken,
            "checks": results
        }
        
        return self.health_status
    
    async def continuous_monitoring(self, interval: int = 60):
        """Continuously monitor health"""
        self.monitoring = True
        logger.info("Health monitoring started")
        
        while self.monitoring:
            try:
                status = await self.perform_health_check()
                
                if status["status"] == "critical":
                    logger.error(f"CRITICAL health issues: {status['issues']}")
                    # Trigger emergency recovery
                    await self.emergency_recovery()
                elif status["status"] == "degraded":
                    logger.warning(f"Health degraded: {status['issues']}")
                else:
                    logger.info("System healthy")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def emergency_recovery(self):
        """Perform emergency recovery actions"""
        logger.critical("Initiating emergency recovery")
        
        # 1. Free all possible resources
        await self.free_memory()
        await self.cleanup_disk()
        
        # 2. Restart critical services
        for process_name in self.critical_processes.keys():
            await self.restart_process(process_name)
        
        # 3. If still critical after 30 seconds, full system restart
        await asyncio.sleep(30)
        status = await self.perform_health_check()
        
        if status["status"] == "critical":
            logger.critical("Emergency recovery failed - requesting system intervention")
            # Could trigger alerts, notifications, etc.
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.monitoring = False
        logger.info("Health monitoring stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_status

# Global health monitor instance
health_monitor = HealthMonitor()