#!/usr/bin/env python3
"""
AION Scheduler System
Cron-like scheduled tasks and periodic operations
"""

import asyncio
import schedule
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Callable, Optional
import logging
from pathlib import Path
import json
import subprocess

logger = logging.getLogger('AION_Scheduler')

class AionScheduler:
    """
    Manages scheduled and periodic tasks for autonomous operation
    """
    
    def __init__(self):
        self.tasks = {}
        self.running = False
        self.schedule_thread = None
        self.async_loop = None
        self.task_history = []
        
        # Default scheduled tasks
        self._setup_default_tasks()
    
    def _setup_default_tasks(self):
        """Setup default maintenance tasks"""
        
        # Health check every 5 minutes
        self.add_task(
            "health_check",
            self._health_check_task,
            schedule_type="interval",
            minutes=5,
            description="System health monitoring"
        )
        
        # Memory cleanup every hour
        self.add_task(
            "memory_cleanup",
            self._memory_cleanup_task,
            schedule_type="interval",
            hours=1,
            description="Free memory and clean caches"
        )
        
        # Log rotation daily at 2 AM
        self.add_task(
            "log_rotation",
            self._log_rotation_task,
            schedule_type="daily",
            time="02:00",
            description="Rotate and compress logs"
        )
        
        # Backup daily at 3 AM
        self.add_task(
            "daily_backup",
            self._backup_task,
            schedule_type="daily",
            time="03:00",
            description="Backup critical files and database"
        )
        
        # Update check weekly on Sunday at 4 AM
        self.add_task(
            "update_check",
            self._update_check_task,
            schedule_type="weekly",
            day="sunday",
            time="04:00",
            description="Check for system updates"
        )
    
    def add_task(self, name: str, func: Callable, schedule_type: str,
                 description: str = "", **schedule_params):
        """
        Add a scheduled task
        
        Args:
            name: Unique task name
            func: Function to execute
            schedule_type: 'interval', 'daily', 'weekly', 'hourly'
            description: Task description
            **schedule_params: Parameters for scheduling
        """
        
        task = {
            "name": name,
            "function": func,
            "schedule_type": schedule_type,
            "description": description,
            "params": schedule_params,
            "last_run": None,
            "next_run": None,
            "run_count": 0
        }
        
        # Schedule the task
        if schedule_type == "interval":
            if "seconds" in schedule_params:
                schedule.every(schedule_params["seconds"]).seconds.do(
                    self._run_task, name
                )
            elif "minutes" in schedule_params:
                schedule.every(schedule_params["minutes"]).minutes.do(
                    self._run_task, name
                )
            elif "hours" in schedule_params:
                schedule.every(schedule_params["hours"]).hours.do(
                    self._run_task, name
                )
                
        elif schedule_type == "daily":
            time_str = schedule_params.get("time", "00:00")
            schedule.every().day.at(time_str).do(self._run_task, name)
            
        elif schedule_type == "hourly":
            schedule.every().hour.at(f":{schedule_params.get('minute', '00')}").do(
                self._run_task, name
            )
            
        elif schedule_type == "weekly":
            day = schedule_params.get("day", "monday")
            time_str = schedule_params.get("time", "00:00")
            getattr(schedule.every(), day).at(time_str).do(self._run_task, name)
        
        self.tasks[name] = task
        logger.info(f"Scheduled task '{name}': {description}")
    
    def _run_task(self, task_name: str):
        """Execute a scheduled task"""
        if task_name not in self.tasks:
            logger.error(f"Task {task_name} not found")
            return
        
        task = self.tasks[task_name]
        
        try:
            logger.info(f"Running scheduled task: {task_name}")
            task["last_run"] = datetime.now()
            task["run_count"] += 1
            
            # Execute the task function
            result = task["function"]()
            
            # Record in history
            self.task_history.append({
                "task": task_name,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "result": str(result)[:200] if result else None
            })
            
            logger.info(f"Task {task_name} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}")
            self.task_history.append({
                "task": task_name,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
    
    def remove_task(self, name: str):
        """Remove a scheduled task"""
        if name in self.tasks:
            # Clear from schedule
            schedule.clear(name)
            del self.tasks[name]
            logger.info(f"Removed task: {name}")
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.schedule_thread = threading.Thread(target=self._scheduler_loop)
        self.schedule_thread.daemon = True
        self.schedule_thread.start()
        
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.schedule_thread:
            self.schedule_thread.join(timeout=5)
        
        logger.info("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                threading.Event().wait(1)  # Sleep for 1 second
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status and task information"""
        task_status = []
        
        for name, task in self.tasks.items():
            task_status.append({
                "name": name,
                "description": task["description"],
                "schedule_type": task["schedule_type"],
                "last_run": task["last_run"].isoformat() if task["last_run"] else None,
                "run_count": task["run_count"]
            })
        
        return {
            "running": self.running,
            "total_tasks": len(self.tasks),
            "tasks": task_status,
            "recent_history": self.task_history[-10:]  # Last 10 task executions
        }
    
    # Default task implementations
    
    def _health_check_task(self):
        """Perform system health check"""
        try:
            # Check API health
            import requests
            response = requests.get("http://127.0.0.1:30001/health", timeout=5)
            
            # Check disk space
            import psutil
            disk = psutil.disk_usage('/')
            
            # Check memory
            mem = psutil.virtual_memory()
            
            return {
                "api_status": response.status_code == 200,
                "disk_free_gb": disk.free // (1024**3),
                "memory_available_gb": mem.available // (1024**3)
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"error": str(e)}
    
    def _memory_cleanup_task(self):
        """Clean up memory"""
        try:
            import gc
            gc.collect()
            
            # Clear caches
            subprocess.run(["sync"], timeout=10)
            
            return {"status": "memory cleaned"}
        except Exception as e:
            return {"error": str(e)}
    
    def _log_rotation_task(self):
        """Rotate log files"""
        try:
            log_dir = Path("/aion/logs")
            rotated = 0
            
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_size > 100 * 1024 * 1024:  # 100MB
                    # Rotate the log
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_name = log_file.with_suffix(f".{timestamp}.log")
                    log_file.rename(new_name)
                    
                    # Compress
                    subprocess.run(["gzip", str(new_name)], timeout=30)
                    rotated += 1
            
            return {"rotated_files": rotated}
        except Exception as e:
            return {"error": str(e)}
    
    def _backup_task(self):
        """Backup critical files"""
        try:
            backup_dir = Path("/aion/backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = backup_dir / f"backup_{timestamp}.tar.gz"
            
            # Backup critical directories
            subprocess.run([
                "tar", "-czf", str(backup_name),
                "/opt/aion/*.py",
                "/aion/memory",
                "/aion/logs/*.log"
            ], timeout=300)
            
            return {"backup_created": str(backup_name)}
        except Exception as e:
            return {"error": str(e)}
    
    def _update_check_task(self):
        """Check for updates"""
        try:
            # Check for package updates
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                return {"outdated_packages": len(outdated)}
            
            return {"status": "check completed"}
        except Exception as e:
            return {"error": str(e)}
    
    def add_cron_task(self, name: str, cron_expression: str, command: str):
        """Add a cron-style task"""
        
        def cron_task():
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                return {
                    "stdout": result.stdout[:500],
                    "exit_code": result.returncode
                }
            except Exception as e:
                return {"error": str(e)}
        
        # Parse cron expression and add task
        # This is simplified - in production would use a proper cron parser
        self.add_task(
            name,
            cron_task,
            schedule_type="interval",
            minutes=60,  # Default to hourly
            description=f"Cron task: {command[:50]}"
        )

# Global scheduler instance
scheduler = AionScheduler()