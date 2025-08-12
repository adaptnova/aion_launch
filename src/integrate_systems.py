#!/usr/bin/env python3
"""
Integration script to add all autonomy systems to the main toolbelt
"""

import sys
sys.path.insert(0, '/opt/aion')

# Add these imports to the main toolbelt
integration_code = '''

# ================================
# INTEGRATED AUTONOMY SYSTEMS
# ================================

# Import all autonomy subsystems
from self_modification import self_mod
from health_monitor import health_monitor
from multi_agent import multi_agent_system, AgentRole
from scheduler import scheduler

# Start background services
import threading
import asyncio

def start_autonomy_services():
    """Start all autonomy background services"""
    
    # Start health monitoring
    asyncio.create_task(health_monitor.continuous_monitoring(interval=60))
    logger.info("Health monitoring started")
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    logger.info("All autonomy services started")

# ================================
# EXTENDED API ENDPOINTS
# ================================

@app.post("/self/analyze")
async def analyze_self(module_name: Optional[str] = None):
    """Analyze own code structure"""
    return self_mod.analyze_own_code(module_name)

@app.post("/self/modify")
async def modify_self(request: Dict[str, Any]):
    """Modify own source code"""
    return self_mod.modify_own_code(
        request["module_name"],
        request["modifications"],
        request.get("description", "")
    )

@app.post("/self/optimize")
async def optimize_self():
    """Optimize own performance"""
    return self_mod.optimize_own_performance()

@app.post("/health/check")
async def health_check():
    """Perform health check"""
    return await health_monitor.perform_health_check()

@app.get("/health/status")
async def health_status():
    """Get health status"""
    return health_monitor.get_status()

@app.post("/agents/spawn")
async def spawn_agent(request: Dict[str, Any]):
    """Spawn a new agent"""
    role = AgentRole[request["role"].upper()]
    agent = multi_agent_system.spawn_agent(
        role,
        request.get("capabilities")
    )
    return {
        "agent_id": agent.id,
        "role": agent.role.value,
        "status": agent.status
    }

@app.post("/agents/task")
async def distribute_task(request: Dict[str, Any]):
    """Distribute a complex task to agents"""
    results = await multi_agent_system.distribute_complex_task(request["task"])
    return {"results": results}

@app.get("/agents/status")
async def agents_status(agent_id: Optional[str] = None):
    """Get agent status"""
    return multi_agent_system.get_agent_status(agent_id)

@app.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler status"""
    return scheduler.get_status()

@app.post("/scheduler/add_task")
async def add_scheduled_task(request: Dict[str, Any]):
    """Add a scheduled task"""
    # This would need proper function mapping in production
    scheduler.add_cron_task(
        request["name"],
        request.get("cron", "0 * * * *"),
        request["command"]
    )
    return {"status": "task scheduled", "name": request["name"]}

@app.on_event("startup")
async def startup_event():
    """Start all services on API startup"""
    start_autonomy_services()
    logger.info("AION Full Autonomy System Online")
    logger.info("All subsystems integrated and operational")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of all services"""
    scheduler.stop()
    health_monitor.stop_monitoring()
    await multi_agent_system.shutdown()
    logger.info("AION System shutdown complete")

# Update system state
system_state["capabilities"].update([
    "self_modification",
    "health_monitoring",
    "multi_agent_coordination",
    "scheduled_tasks",
    "performance_optimization"
])

'''

# Write integration file
with open('/opt/aion/autonomy_integration.py', 'w') as f:
    f.write(integration_code)

print("✅ Integration code generated")
print("📝 Add the following line to full_autonomy_toolbelt.py:")
print("   exec(open('/opt/aion/autonomy_integration.py').read())")