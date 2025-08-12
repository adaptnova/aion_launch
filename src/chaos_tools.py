#!/usr/bin/env python3
"""
AION Chaos Engineering Tools - NO BRAKES
Full hardware stress, network chaos, and system tracing
As requested: "demolition derby but inside the VM fence"
"""

import subprocess
import time
import json
import logging
from typing import Dict, Any, List, Optional
import random
import psutil

logger = logging.getLogger('AION_CHAOS')

class ChaosTools:
    """
    Unrestricted chaos engineering tools
    No CPU/memory limits, no safety nets
    """
    
    def __init__(self):
        self.active_chaos = []
        
    def exec_transient_raw(self, cmd: str, args: List[str] = None,
                          workdir: str = None, pty: bool = True,
                          env: Dict = None, timeout_s: int = None) -> Dict[str, Any]:
        """
        Run command via systemd-run as transient unit
        NO resource limits - full system access
        """
        unit_name = f"aion-{random.randint(1000, 9999)}"
        
        try:
            # Build systemd-run command
            systemd_cmd = ["systemd-run", f"--unit={unit_name}", "--scope"]
            
            if pty:
                systemd_cmd.append("--pty")
            
            if workdir:
                systemd_cmd.extend(["--working-directory", workdir])
            
            if env:
                for key, value in env.items():
                    systemd_cmd.extend(["--setenv", f"{key}={value}"])
            
            # Add the actual command
            systemd_cmd.append(cmd)
            if args:
                systemd_cmd.extend(args)
            
            logger.info(f"Executing transient unit: {unit_name}")
            
            # Execute with optional timeout
            result = subprocess.run(
                systemd_cmd,
                capture_output=True,
                text=True,
                timeout=timeout_s
            )
            
            return {
                "success": result.returncode == 0,
                "unit": unit_name,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "command": ' '.join(systemd_cmd)
            }
            
        except subprocess.TimeoutExpired:
            # Kill the unit if it times out
            subprocess.run(["systemctl", "stop", unit_name], timeout=5)
            return {"error": "Timeout expired", "unit": unit_name}
        except Exception as e:
            return {"error": str(e)}
    
    def cpu_mem_io(self, cpu: int = None, vm: int = None,
                   vm_bytes: str = None, hdd: int = None,
                   timeout: str = None, **kwargs) -> Dict[str, Any]:
        """
        Stress CPU/VM/IO using stress-ng
        NO LIMITS - will push hardware to thermal limits
        """
        try:
            cmd = ["stress-ng"]
            
            # CPU stress
            if cpu:
                cmd.extend(["--cpu", str(cpu)])
                cmd.extend(["--cpu-method", "all"])  # Use all CPU stress methods
            
            # VM stress
            if vm:
                cmd.extend(["--vm", str(vm)])
                if vm_bytes:
                    cmd.extend(["--vm-bytes", vm_bytes])
                else:
                    cmd.extend(["--vm-bytes", "2G"])  # Default 2GB per worker
                cmd.extend(["--vm-method", "all"])  # All VM stress methods
            
            # HDD I/O stress
            if hdd:
                cmd.extend(["--hdd", str(hdd)])
                cmd.extend(["--hdd-bytes", "4G"])  # 4GB per worker
            
            # Additional stressors from kwargs
            for key, value in kwargs.items():
                if key.startswith("--"):
                    cmd.extend([key, str(value)])
                else:
                    cmd.extend([f"--{key}", str(value)])
            
            # Timeout
            if timeout:
                cmd.extend(["--timeout", timeout])
            else:
                cmd.extend(["--timeout", "120s"])  # Default 2 minutes
            
            # Metrics output
            cmd.append("--metrics")
            
            logger.warning(f"CHAOS: Starting stress-ng with {' '.join(cmd)}")
            
            # Run via transient unit for easy cleanup
            result = self.exec_transient_raw(
                "stress-ng",
                args=cmd[1:],  # Skip the command name
                timeout_s=int(timeout[:-1]) + 10 if timeout else 130
            )
            
            self.active_chaos.append({
                "type": "stress-ng",
                "command": ' '.join(cmd),
                "started": time.time()
            })
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def netem(self, iface: str, delay_ms: int = None,
              jitter_ms: int = None, loss_pct: float = None,
              reorder_pct: float = None, rate_kbit: int = None,
              action: str = "add") -> Dict[str, Any]:
        """
        Network chaos via tc netem
        Delay, loss, jitter, reordering - makes protocols cry
        """
        try:
            if action == "del":
                # Remove existing qdisc
                cmd = ["sudo", "tc", "qdisc", "del", "dev", iface, "root"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "action": "deleted",
                    "interface": iface
                }
            
            # Build netem command
            cmd = ["sudo", "tc", "qdisc", action, "dev", iface, "root", "netem"]
            
            if delay_ms:
                cmd.extend(["delay", f"{delay_ms}ms"])
                if jitter_ms:
                    cmd.append(f"{jitter_ms}ms")
            
            if loss_pct:
                cmd.extend(["loss", f"{loss_pct}%"])
            
            if reorder_pct:
                cmd.extend(["reorder", f"{reorder_pct}%"])
                if not delay_ms:
                    cmd.extend(["delay", "10ms"])  # Reorder needs delay
            
            if rate_kbit:
                cmd.extend(["rate", f"{rate_kbit}kbit"])
            
            logger.warning(f"CHAOS: Network netem on {iface}: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.active_chaos.append({
                    "type": "netem",
                    "interface": iface,
                    "settings": {
                        "delay": delay_ms,
                        "jitter": jitter_ms,
                        "loss": loss_pct,
                        "reorder": reorder_pct,
                        "rate": rate_kbit
                    }
                })
            
            return {
                "success": result.returncode == 0,
                "command": ' '.join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def bpftrace(self, oneliner: str = None, program: str = None,
                 args: Dict = None) -> Dict[str, Any]:
        """
        Run bpftrace for syscall/latency tracing
        The microscope during the fire
        """
        try:
            if oneliner:
                # Run a one-liner
                cmd = ["sudo", "bpftrace", "-e", oneliner]
            elif program:
                # Run a saved program
                cmd = ["sudo", "bpftrace", program]
            else:
                # Default: trace syscall counts
                oneliner = "tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }"
                cmd = ["sudo", "bpftrace", "-e", oneliner]
            
            if args:
                for key, value in args.items():
                    cmd.extend([f"-D{key}={value}"])
            
            logger.info(f"TRACE: Running bpftrace: {' '.join(cmd)}")
            
            # Run with timeout to avoid hanging
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "stderr": result.stderr,
                "trace": oneliner or program
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Trace timeout", "partial_output": ""}
        except Exception as e:
            return {"error": str(e)}
    
    def redis_trace(self, kind: str, data: Dict) -> Dict[str, Any]:
        """
        Log everything to Redis Streams for forensics
        XADD to aion.traces stream
        """
        try:
            import redis
            
            r = redis.Redis(host='localhost', port=18000, decode_responses=True)
            
            # Add timestamp and kind
            trace_data = {
                "timestamp": time.time(),
                "kind": kind,
                **data
            }
            
            # XADD to stream
            stream_id = r.xadd("aion.traces", trace_data)
            
            # Trim to keep last 10000 entries
            r.xtrim("aion.traces", maxlen=10000, approximate=True)
            
            return {
                "success": True,
                "stream_id": stream_id,
                "kind": kind
            }
            
        except Exception as e:
            # Redis trace is optional - don't fail operations
            logger.warning(f"Redis trace failed: {e}")
            return {"success": False, "error": str(e)}
    
    def kill_all_chaos(self) -> Dict[str, Any]:
        """
        Emergency kill switch - stop all chaos
        """
        killed = []
        
        try:
            # Kill all aion-* systemd units
            result = subprocess.run(
                ["systemctl", "list-units", "--all", "aion-*", "--no-legend"],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.splitlines():
                unit = line.split()[0]
                subprocess.run(["systemctl", "stop", unit], timeout=5)
                killed.append(unit)
            
            # Remove all netem qdiscs
            interfaces = psutil.net_if_stats().keys()
            for iface in interfaces:
                subprocess.run(
                    ["sudo", "tc", "qdisc", "del", "dev", iface, "root"],
                    capture_output=True,
                    timeout=5
                )
            
            # Clear active chaos list
            self.active_chaos = []
            
            return {
                "success": True,
                "killed_units": killed,
                "cleared_interfaces": list(interfaces)
            }
            
        except Exception as e:
            return {"error": str(e), "partial_cleanup": killed}
    
    def chaos_status(self) -> Dict[str, Any]:
        """Get current chaos status"""
        return {
            "active_chaos": self.active_chaos,
            "system_load": os.getloadavg(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "message": "Chaos is a ladder"
        }

# Global chaos instance
import os
chaos_tools = ChaosTools()