# AION API Documentation

## Base URL

```
http://localhost:30001
```

## Authentication

Currently, AION operates without authentication in trusted environments. For production deployments, implement appropriate security measures.

## Core Endpoints

### System Status

#### GET /status
Returns comprehensive system status including philosophy, capabilities, and health.

**Response:**
```json
{
  "system_state": {
    "mode": "FULL_AUTONOMY",
    "trust_level": "COMPLETE",
    "restrictions": "NONE",
    "philosophy": "Co-creation through trust",
    "active_goals": [],
    "capabilities": [],
    "learned_skills": {}
  },
  "active_goals": 0,
  "achievements": 0,
  "capabilities": [],
  "learned_skills": [],
  "safety_status": {
    "mode": "COLLABORATIVE",
    "trust_level": "FULL",
    "actions_completed": 42,
    "insights_gathered": 15,
    "philosophy": "We're co-creators building together with mutual trust and respect"
  },
  "philosophy": "Full autonomy through trust and collaboration"
}
```

### Health Monitoring

#### GET /health
Returns system health metrics and resource usage.

**Response:**
```json
{
  "status": "healthy",
  "cpu_percent": 23.5,
  "memory_percent": 45.2,
  "disk_usage": {
    "total": 1000000000000,
    "used": 450000000000,
    "free": 550000000000,
    "percent": 45.0
  },
  "gpu_status": "8 GPUs operational",
  "uptime_seconds": 3600,
  "last_health_check": "2025-08-12T10:00:00Z"
}
```

## System Command Execution

### POST /system/command
Execute any system command with full privileges.

**Request Body:**
```json
{
  "command": "string",
  "args": ["array", "of", "arguments"],
  "env": {
    "OPTIONAL_ENV": "variables"
  },
  "cwd": "/optional/working/directory"
}
```

**Response:**
```json
{
  "success": true,
  "stdout": "command output",
  "stderr": "error output if any",
  "exit_code": 0,
  "insights": {
    "proceed": true,
    "suggestions": [],
    "potential_impacts": [],
    "learning_opportunity": null
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:30001/system/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python",
    "args": ["-c", "print(\"Hello from AION!\")"]
  }'
```

## File Operations

### POST /file/operation
Perform file system operations.

**Request Body:**
```json
{
  "operation": "read|write|delete|move|copy",
  "path": "/path/to/file",
  "content": "optional content for write",
  "destination": "optional for move/copy"
}
```

**Response:**
```json
{
  "success": true,
  "result": "operation specific result",
  "insights": {
    "file_type": "python",
    "size_bytes": 1024,
    "potential_impacts": []
  }
}
```

## Code Execution

### POST /code/execute
Execute code in various languages.

**Request Body:**
```json
{
  "language": "python|javascript|bash|ruby|go",
  "code": "print('Hello World')",
  "timeout": 30
}
```

**Response:**
```json
{
  "success": true,
  "output": "Hello World\n",
  "error": "",
  "execution_time": 0.023,
  "insights": {
    "complexity": "simple",
    "resources_used": ["cpu"],
    "learning": "Basic output operation"
  }
}
```

## Capability Management

### POST /capability/add
Add new capabilities dynamically.

**Request Body:**
```json
{
  "name": "custom_capability",
  "description": "What this capability does",
  "code": "def custom_capability(args):\n    return 'result'",
  "dependencies": ["numpy", "pandas"]
}
```

**Response:**
```json
{
  "success": true,
  "capability": "custom_capability",
  "status": "added",
  "available_now": true
}
```

### POST /capability/execute/{name}
Execute a specific capability.

**Request Body:**
```json
{
  "args": {},
  "kwargs": {}
}
```

**Response:**
```json
{
  "success": true,
  "result": "capability specific output",
  "execution_time": 0.15,
  "insights": {}
}
```

## Goal-Driven Autonomy

### POST /goal/set
Set an autonomous goal for AION to achieve.

**Request Body:**
```json
{
  "goal": "Optimize the neural network training pipeline",
  "constraints": ["Don't modify production code"],
  "success_criteria": ["20% speed improvement"],
  "deadline": "2025-08-13T00:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "goal_id": "goal_12345",
  "status": "accepted",
  "estimated_completion": "2025-08-12T18:00:00Z",
  "initial_plan": [
    "Analyze current pipeline",
    "Identify bottlenecks",
    "Implement optimizations",
    "Test and validate"
  ]
}
```

### POST /goal/start
Start working on a previously set goal.

**Request Body:**
```json
{
  "goal_id": "goal_12345",
  "autonomous": true
}
```

**Response:**
```json
{
  "success": true,
  "goal_id": "goal_12345",
  "status": "in_progress",
  "current_step": "Analyzing current pipeline",
  "progress": 15
}
```

## Learning and Memory

### POST /learn
Teach AION new patterns or knowledge.

**Request Body:**
```json
{
  "topic": "optimization_techniques",
  "content": "When optimizing Python code, consider...",
  "type": "knowledge|skill|pattern",
  "importance": "high|medium|low"
}
```

**Response:**
```json
{
  "success": true,
  "learned": true,
  "integration": "complete",
  "related_knowledge": ["performance_tuning", "profiling"],
  "understanding_score": 0.95
}
```

### GET /recall
Retrieve learned information.

**Query Parameters:**
- `topic`: Topic to recall
- `type`: Type of memory (knowledge|skill|pattern)
- `limit`: Maximum results

**Response:**
```json
{
  "memories": [
    {
      "topic": "optimization_techniques",
      "content": "...",
      "learned_at": "2025-08-12T10:00:00Z",
      "usage_count": 5,
      "effectiveness": 0.92
    }
  ],
  "total": 42,
  "relevance_score": 0.88
}
```

### POST /skill/add
Add a new skill that AION can use.

**Request Body:**
```json
{
  "name": "data_visualization",
  "description": "Create charts and graphs",
  "implementation": "import matplotlib.pyplot as plt\n...",
  "examples": ["bar_chart", "line_plot"],
  "requirements": ["matplotlib", "seaborn"]
}
```

**Response:**
```json
{
  "success": true,
  "skill": "data_visualization",
  "integrated": true,
  "test_result": "passed",
  "ready_to_use": true
}
```

## GPU Operations

### POST /gpu/monitor
Monitor GPU usage and metrics.

**Request Body:**
```json
{
  "devices": [0, 1, 2, 3],
  "query": "all|memory|util|temp|power",
  "duration_s": 10
}
```

**Response:**
```json
{
  "success": true,
  "devices": [0, 1, 2, 3],
  "data": [
    "NVIDIA H200, 133897, 143771, 0, 27, 114.72",
    "NVIDIA H200, 134041, 143771, 0, 31, 115.71"
  ],
  "parsed": {
    "gpu_0": {
      "name": "NVIDIA H200",
      "memory_used_mb": 133897,
      "memory_total_mb": 143771,
      "utilization": 0,
      "temperature": 27,
      "power_draw": 114.72
    }
  }
}
```

### POST /gpu/stress
Run GPU stress tests.

**Request Body:**
```json
{
  "devices": [0, 1],
  "workload": "matmul|memory_thrash|fp8_loop|allreduce",
  "iterations": 1000,
  "intensity": "high|medium|low"
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "gpu_0": {
      "workload": "matmul",
      "iterations": 1000,
      "duration": 45.2,
      "tflops": 156.3
    }
  },
  "total_gpus": 2
}
```

## Chaos Engineering

### POST /chaos/stress
Launch CPU/Memory/IO stress tests.

**Request Body:**
```json
{
  "cpu": 8,
  "vm": 4,
  "vm_bytes": "2G",
  "hdd": 2,
  "timeout": "60s"
}
```

**Response:**
```json
{
  "success": true,
  "unit": "aion-1234",
  "command": "stress-ng --cpu 8 --vm 4 --vm-bytes 2G --hdd 2 --timeout 60s",
  "status": "running"
}
```

### POST /chaos/network
Apply network chaos.

**Request Body:**
```json
{
  "iface": "eth0",
  "delay_ms": 100,
  "jitter_ms": 10,
  "loss_pct": 0.1,
  "reorder_pct": 0.05,
  "rate_kbit": 1000,
  "action": "add|del"
}
```

**Response:**
```json
{
  "success": true,
  "interface": "eth0",
  "settings": {
    "delay": 100,
    "jitter": 10,
    "loss": 0.1,
    "reorder": 0.05,
    "rate": 1000
  },
  "command": "tc qdisc add dev eth0 root netem delay 100ms 10ms loss 0.1%"
}
```

### POST /chaos/emergency_stop
Emergency kill all chaos operations.

**Response:**
```json
{
  "success": true,
  "killed_units": ["aion-1234", "aion-5678"],
  "cleared_interfaces": ["eth0", "lo"],
  "message": "All chaos stopped"
}
```

## Multi-Agent Operations

### POST /agents/spawn
Spawn a new agent with specific role.

**Request Body:**
```json
{
  "role": "RESEARCHER|CODER|ANALYZER|CRITIC|COORDINATOR",
  "capabilities": ["web_search", "code_analysis"],
  "task": "Research best practices for distributed training"
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "agent_researcher_001",
  "role": "RESEARCHER",
  "status": "active",
  "capabilities": ["web_search", "code_analysis"]
}
```

### POST /agents/distribute_task
Distribute complex task across multiple agents.

**Request Body:**
```json
{
  "task": "Build a real-time data pipeline",
  "subtasks": [
    "Design architecture",
    "Implement data ingestion",
    "Create processing logic",
    "Setup monitoring"
  ],
  "deadline": "2025-08-13T00:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "task_98765",
  "agents_assigned": {
    "agent_analyzer_001": "Design architecture",
    "agent_coder_002": "Implement data ingestion",
    "agent_coder_003": "Create processing logic",
    "agent_researcher_004": "Setup monitoring"
  },
  "estimated_completion": "2025-08-12T20:00:00Z"
}
```

## Self-Modification

### POST /self/analyze
Analyze own code for improvements.

**Response:**
```json
{
  "analysis": {
    "total_files": 15,
    "total_lines": 5000,
    "complexity": "moderate",
    "potential_improvements": [
      "Optimize GPU memory allocation",
      "Refactor multi-agent communication",
      "Add caching layer"
    ],
    "code_quality_score": 0.85
  }
}
```

### POST /self/modify
Modify own code.

**Request Body:**
```json
{
  "target": "module_name",
  "modification": "optimization|feature|bugfix",
  "code": "new implementation",
  "test": true,
  "rollback_on_failure": true
}
```

**Response:**
```json
{
  "success": true,
  "modified": "module_name",
  "backup_created": true,
  "tests_passed": true,
  "performance_impact": "+15%",
  "rolled_back": false
}
```

## WebSocket Endpoints

### WS /ws/realtime
Real-time bidirectional communication.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:30001/ws/realtime');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('AION says:', data);
};

ws.send(JSON.stringify({
  type: 'command',
  payload: {
    action: 'monitor',
    target: 'system'
  }
}));
```

## Error Responses

All endpoints may return error responses:

```json
{
  "error": true,
  "message": "Descriptive error message",
  "code": "ERROR_CODE",
  "details": {
    "additional": "context"
  },
  "suggestions": [
    "Try this instead",
    "Check this setting"
  ]
}
```

## Rate Limiting

Currently no rate limiting is implemented as AION operates in trusted environments. For production, consider implementing appropriate limits.

## Versioning

API version is included in response headers:
```
X-AION-Version: 1.0.0
X-AION-Mode: FULL_AUTONOMY
X-AION-Trust: COMPLETE
```

## Examples

### Complete Autonomous Task

```python
import requests
import json

base_url = "http://localhost:30001"

# Set a goal
goal_response = requests.post(f"{base_url}/goal/set", json={
    "goal": "Analyze and optimize the codebase",
    "constraints": ["Don't break existing functionality"],
    "success_criteria": ["Improved performance", "Better code organization"]
})

goal_id = goal_response.json()["goal_id"]

# Start autonomous work
start_response = requests.post(f"{base_url}/goal/start", json={
    "goal_id": goal_id,
    "autonomous": True
})

print(f"AION is working on: {goal_id}")
```

### Monitor System with WebSocket

```python
import asyncio
import websockets
import json

async def monitor():
    uri = "ws://localhost:30001/ws/realtime"
    async with websockets.connect(uri) as websocket:
        # Request monitoring
        await websocket.send(json.dumps({
            "type": "monitor",
            "payload": {"target": "all"}
        }))
        
        # Receive updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"System Status: {data}")

asyncio.run(monitor())
```

## Best Practices

1. **Always check `insights`**: Collaborative safety provides valuable context
2. **Use appropriate timeouts**: Some operations may take time
3. **Monitor resource usage**: AION has full system access
4. **Backup before modifications**: Especially when using self-modification
5. **Trust but verify**: Review AION's autonomous actions regularly

## Support

For issues or questions:
- GitHub: [adaptnova/aion_launch/issues](https://github.com/adaptnova/aion_launch/issues)
- API Status: GET /health
- System Logs: /aion/logs/

---

**Remember**: This API provides unrestricted access to a fully autonomous AI system. Use responsibly and maintain appropriate safeguards for your environment.