#!/usr/bin/env python3
"""
AION Self-Modification System
Allows the system to rewrite and improve its own code
"""

import os
import ast
import inspect
import importlib
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import difflib
import shutil
from datetime import datetime
import logging

logger = logging.getLogger('AION_SelfMod')

class SelfModificationSystem:
    """
    Enables the AI to modify its own code and capabilities
    """
    
    def __init__(self):
        self.aion_path = Path("/opt/aion")
        self.backup_path = self.aion_path / "backups"
        self.backup_path.mkdir(exist_ok=True)
        self.modification_history = []
        
    def analyze_own_code(self, module_name: str = None) -> Dict[str, Any]:
        """Analyze own source code for understanding and improvement"""
        if module_name:
            module_path = self.aion_path / f"{module_name}.py"
        else:
            module_path = self.aion_path / "full_autonomy_toolbelt.py"
            
        if not module_path.exists():
            return {"error": f"Module {module_path} not found"}
            
        with open(module_path, 'r') as f:
            source = f.read()
            
        try:
            tree = ast.parse(source)
            
            # Analyze the AST
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
            
            return {
                "module": str(module_path),
                "lines": len(source.splitlines()),
                "classes": classes,
                "functions": functions,
                "imports": imports[:20],  # First 20 imports
                "structure": "analyzed"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def backup_module(self, module_path: Path) -> Path:
        """Create a backup before modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{module_path.stem}_{timestamp}{module_path.suffix}"
        backup_file = self.backup_path / backup_name
        
        shutil.copy2(module_path, backup_file)
        logger.info(f"Backup created: {backup_file}")
        return backup_file
    
    def modify_own_code(self, module_name: str, modifications: str, 
                        description: str = "") -> Dict[str, Any]:
        """
        Modify own source code with the provided changes
        
        Args:
            module_name: Name of the module to modify
            modifications: The new code or modifications to apply
            description: Description of what changes are being made
        """
        module_path = self.aion_path / f"{module_name}.py"
        
        if not module_path.exists():
            # Create new module if it doesn't exist
            module_path.parent.mkdir(parents=True, exist_ok=True)
            with open(module_path, 'w') as f:
                f.write(modifications)
            
            self.modification_history.append({
                "timestamp": datetime.now().isoformat(),
                "module": module_name,
                "action": "created",
                "description": description
            })
            
            return {
                "success": True,
                "action": "created",
                "module": module_name,
                "description": description
            }
        
        # Backup existing module
        backup_file = self.backup_module(module_path)
        
        try:
            # Read current code
            with open(module_path, 'r') as f:
                original = f.read()
            
            # Apply modifications
            with open(module_path, 'w') as f:
                f.write(modifications)
            
            # Verify the new code is valid Python
            compile(modifications, module_path, 'exec')
            
            # Calculate diff
            diff = list(difflib.unified_diff(
                original.splitlines(keepends=True),
                modifications.splitlines(keepends=True),
                fromfile=f'{module_name}.py (before)',
                tofile=f'{module_name}.py (after)'
            ))
            
            self.modification_history.append({
                "timestamp": datetime.now().isoformat(),
                "module": module_name,
                "action": "modified",
                "description": description,
                "backup": str(backup_file),
                "diff_lines": len(diff)
            })
            
            # Reload the module if it's already imported
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            
            return {
                "success": True,
                "action": "modified",
                "module": module_name,
                "backup": str(backup_file),
                "diff_preview": ''.join(diff[:50]),  # First 50 lines of diff
                "description": description
            }
            
        except SyntaxError as e:
            # Restore from backup if syntax error
            shutil.copy2(backup_file, module_path)
            return {
                "success": False,
                "error": f"Syntax error in modifications: {e}",
                "restored_from": str(backup_file)
            }
        except Exception as e:
            # Restore from backup on any error
            shutil.copy2(backup_file, module_path)
            return {
                "success": False,
                "error": str(e),
                "restored_from": str(backup_file)
            }
    
    def add_new_capability(self, capability_name: str, code: str, 
                          integrate: bool = True) -> Dict[str, Any]:
        """Add a completely new capability to the system"""
        
        # Create the new capability module
        result = self.modify_own_code(
            f"capabilities/{capability_name}",
            code,
            f"New capability: {capability_name}"
        )
        
        if not result["success"]:
            return result
        
        if integrate:
            # Integrate into main system
            integration_code = f"""
# Auto-integration of {capability_name}
from capabilities.{capability_name} import *

# Register capability
system_state["capabilities"].add("{capability_name}")
logger.info("Capability {capability_name} integrated")
"""
            
            # Add to main toolbelt
            main_module = self.aion_path / "full_autonomy_toolbelt.py"
            with open(main_module, 'a') as f:
                f.write(integration_code)
            
            result["integrated"] = True
        
        return result
    
    def optimize_own_performance(self) -> Dict[str, Any]:
        """Analyze and optimize own performance"""
        optimizations = []
        
        # Check for potential optimizations
        analysis = self.analyze_own_code()
        
        # Simple optimization rules (can be much more sophisticated)
        if len(analysis.get("functions", [])) > 100:
            optimizations.append("Consider refactoring - too many functions in main module")
        
        if "tensorflow" in analysis.get("imports", []) and "torch" in analysis.get("imports", []):
            optimizations.append("Both TensorFlow and PyTorch imported - consider using only one")
        
        # Check for unused imports
        source_file = self.aion_path / "full_autonomy_toolbelt.py"
        result = subprocess.run(
            ["pylint", "--disable=all", "--enable=W0611", str(source_file)],
            capture_output=True,
            text=True
        )
        
        if "unused-import" in result.stdout:
            optimizations.append("Unused imports detected - consider removing")
        
        return {
            "analysis": analysis,
            "optimizations": optimizations,
            "health": "optimal" if len(optimizations) == 0 else "could_be_improved"
        }
    
    def rollback_modification(self, module_name: str) -> Dict[str, Any]:
        """Rollback to the latest backup of a module"""
        
        # Find the latest backup
        backups = sorted(self.backup_path.glob(f"{module_name}_*.py"), reverse=True)
        
        if not backups:
            return {"error": f"No backups found for {module_name}"}
        
        latest_backup = backups[0]
        module_path = self.aion_path / f"{module_name}.py"
        
        shutil.copy2(latest_backup, module_path)
        
        return {
            "success": True,
            "rolled_back_to": str(latest_backup),
            "module": module_name
        }
    
    def get_modification_history(self, limit: int = 10) -> list:
        """Get recent modification history"""
        return self.modification_history[-limit:]

# Global instance
import sys
self_mod = SelfModificationSystem()