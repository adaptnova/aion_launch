#!/usr/bin/env python3
"""
AION GPU Tools - Full access to 8x H200 GPUs
Direct hardware control for AI compute experiments
"""

import subprocess
import json
import time
import logging
from typing import Dict, Any, List, Optional
import numpy as np

logger = logging.getLogger('AION_GPU')

class GPUTools:
    """
    Complete GPU control for the H200 cluster
    Each H200: 141GB HBM3e, 4.8TB/s bandwidth
    """
    
    def __init__(self):
        self.num_gpus = 8
        self.gpu_memory_gb = 141  # Per H200
        
    def monitor_usage(self, devices: List[int] = None, 
                     query: str = "all", duration_s: int = 0) -> Dict[str, Any]:
        """
        Monitor GPU metrics via nvidia-smi
        Query types: memory, util, temp, power, fan, all
        """
        if devices is None:
            devices = list(range(self.num_gpus))
        
        device_str = ','.join(map(str, devices))
        
        query_map = {
            "memory": "memory.used,memory.total,memory.free",
            "util": "utilization.gpu,utilization.memory",
            "temp": "temperature.gpu",
            "power": "power.draw,power.limit",
            "fan": "fan.speed",
            "all": "name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw"
        }
        
        query_fields = query_map.get(query, query_map["all"])
        
        try:
            cmd = [
                "nvidia-smi",
                f"--id={device_str}",
                f"--query-gpu={query_fields}",
                "--format=csv,noheader,nounits"
            ]
            
            if duration_s > 0:
                # Monitor for duration
                start_time = time.time()
                readings = []
                
                while time.time() - start_time < duration_s:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        readings.append(result.stdout.strip())
                    time.sleep(1)
                
                return {
                    "success": True,
                    "devices": devices,
                    "duration": duration_s,
                    "readings": readings
                }
            else:
                # Single reading
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "devices": devices,
                        "data": result.stdout.strip().split('\n')
                    }
                else:
                    return {"success": False, "error": result.stderr}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_stress(self, devices: List[int] = None,
                  workload: str = "matmul", iterations: int = 1000,
                  intensity: str = "high") -> Dict[str, Any]:
        """
        Launch GPU stress workloads
        Workloads: matmul, fp8_loop, memory_thrash, allreduce
        """
        if devices is None:
            devices = [0]  # Default to first GPU
        
        try:
            import torch
            
            results = {}
            
            for device_id in devices:
                torch.cuda.set_device(device_id)
                device = torch.device(f'cuda:{device_id}')
                
                if workload == "matmul":
                    # Matrix multiplication stress
                    size = 8192 if intensity == "high" else 4096
                    a = torch.randn(size, size, device=device, dtype=torch.float16)
                    b = torch.randn(size, size, device=device, dtype=torch.float16)
                    
                    start = time.time()
                    for _ in range(iterations):
                        c = torch.matmul(a, b)
                        torch.cuda.synchronize()
                    duration = time.time() - start
                    
                    results[f"gpu_{device_id}"] = {
                        "workload": workload,
                        "iterations": iterations,
                        "duration": duration,
                        "tflops": (2 * size**3 * iterations) / (duration * 1e12)
                    }
                    
                elif workload == "memory_thrash":
                    # Memory bandwidth stress
                    size = 1024 * 1024 * 1024  # 1GB chunks
                    data = torch.randn(size // 4, device=device, dtype=torch.float32)
                    
                    start = time.time()
                    for _ in range(iterations):
                        data2 = data.clone()
                        data = data2 * 2.0
                        torch.cuda.synchronize()
                    duration = time.time() - start
                    
                    results[f"gpu_{device_id}"] = {
                        "workload": workload,
                        "iterations": iterations,
                        "duration": duration,
                        "bandwidth_gb_s": (size * iterations * 2) / (duration * 1e9)
                    }
                    
                elif workload == "fp8_loop":
                    # FP8 compute stress (H200 optimized)
                    # Note: Real FP8 requires special libraries
                    size = 16384
                    a = torch.randn(size, size, device=device, dtype=torch.float16)
                    
                    start = time.time()
                    for _ in range(iterations):
                        a = torch.nn.functional.gelu(a)
                        torch.cuda.synchronize()
                    duration = time.time() - start
                    
                    results[f"gpu_{device_id}"] = {
                        "workload": "fp8_simulation",
                        "iterations": iterations,
                        "duration": duration
                    }
                    
                elif workload == "allreduce":
                    # Multi-GPU communication stress
                    if len(devices) < 2:
                        return {"error": "allreduce requires multiple GPUs"}
                    
                    # This would use NCCL for real all-reduce
                    tensor = torch.randn(1024, 1024, device=device)
                    
                    start = time.time()
                    for _ in range(iterations):
                        # Simulate all-reduce with copy
                        tensor2 = tensor.clone()
                        torch.cuda.synchronize()
                    duration = time.time() - start
                    
                    results[f"gpu_{device_id}"] = {
                        "workload": workload,
                        "iterations": iterations,
                        "duration": duration
                    }
            
            return {
                "success": True,
                "results": results,
                "total_gpus": len(devices)
            }
            
        except ImportError:
            return {"error": "PyTorch not available for GPU stress"}
        except Exception as e:
            return {"error": str(e)}
    
    def net_bench(self, devices: List[List[int]], 
                  message_size_bytes: int = 1024*1024,
                  duration_s: int = 10) -> Dict[str, Any]:
        """
        Test inter-GPU bandwidth via NCCL/NVLink
        """
        try:
            # Check NVLink topology
            result = subprocess.run(
                ["nvidia-smi", "topo", "-m"],
                capture_output=True,
                text=True
            )
            
            topology = result.stdout if result.returncode == 0 else "Unable to get topology"
            
            # For actual bandwidth test, would use nccl-tests
            # This is a simplified version
            bandwidth_test = {}
            
            for pair in devices:
                if len(pair) != 2:
                    continue
                    
                src, dst = pair
                
                # Simulate P2P bandwidth test
                cmd = f"nvidia-smi nvlink -i {src} -s"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                bandwidth_test[f"{src}->{dst}"] = {
                    "message_size": message_size_bytes,
                    "nvlink_status": "active" if result.returncode == 0 else "error"
                }
            
            return {
                "success": True,
                "topology": topology,
                "bandwidth_tests": bandwidth_test,
                "duration": duration_s
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def set_persistence_mode(self, enable: bool = True) -> Dict[str, Any]:
        """Enable/disable GPU persistence mode"""
        try:
            mode = "1" if enable else "0"
            result = subprocess.run(
                ["sudo", "nvidia-smi", "-pm", mode],
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "persistence_mode": enable,
                "output": result.stdout
            }
        except Exception as e:
            return {"error": str(e)}
    
    def set_power_limit(self, device: int, watts: int) -> Dict[str, Any]:
        """Set GPU power limit (dangerous!)"""
        try:
            result = subprocess.run(
                ["sudo", "nvidia-smi", "-i", str(device), "-pl", str(watts)],
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "device": device,
                "power_limit": watts,
                "output": result.stdout
            }
        except Exception as e:
            return {"error": str(e)}
    
    def reset_gpu(self, device: int) -> Dict[str, Any]:
        """Reset GPU (requires no active processes)"""
        try:
            result = subprocess.run(
                ["sudo", "nvidia-smi", "-i", str(device), "-r"],
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "device": device,
                "output": result.stdout
            }
        except Exception as e:
            return {"error": str(e)}

# Global GPU tools instance
gpu_tools = GPUTools()