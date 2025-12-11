# Workflow Engine - Simple Graph Execution System

A minimal workflow/graph engine built with Python and FastAPI. This system allows you to define sequences of steps (nodes), connect them, maintain shared state, and execute workflows end-to-end via REST APIs.

## What This Project Does

This is a simplified version of workflow engines like LangGraph. It supports:
- **Nodes**: Python functions that read and modify a shared state
- **State**: A dictionary that flows from one node to another
- **Edges**: Define which node runs after which
- **Branching**: Conditional routing based on state values
- **Looping**: Run nodes repeatedly until a condition is met
- **Tool Registry**: A simple dictionary of reusable tools (functions)

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── engine.py          # Core workflow engine (Node, WorkflowGraph)
│   ├── tools.py           # Tool registry system
│   ├── workflows.py       # Example workflows
│   └── main.py            # FastAPI application and endpoints
├── requirements.txt
└── README.md
```

## How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Access API Documentation

Open your browser and go to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Create Example Graph
```bash
POST /graph/create/example
```
Creates a pre-built code review workflow.

**Response:**
```json
{
  "graph_id": "uuid-here",
  "message": "Example code review workflow created"
}
```

### 2. Run a Graph
```bash
POST /graph/run
```

**Request Body:**
```json
{
  "graph_id": "your-graph-id",
  "initial_state": {
    "code": "def hello():\n    print('world')\n    if True:\n        pass",
    "threshold": 70
  }
}
```

**Response:**
```json
{
  "run_id": "run-uuid",
  "final_state": {
    "code": "...",
    "quality_score": 85,
    "issues": [...],
    ...
  },
  "execution_log": [
    {
      "node": "extract_functions",
      "status": "completed",
      "iteration": 1
    },
    ...
  ]
}
```

### 3. Get Run State
```bash
GET /graph/state/{run_id}
```

Returns the current state and execution log for a specific run.

### 4. List All Graphs
```bash
GET /graphs
```

### 5. List All Runs
```bash
GET /runs
```

## Example Workflow: Code Review Mini-Agent

The included example workflow performs code review with these steps:

1. **Extract Functions**: Counts function definitions in code
2. **Check Complexity**: Calculates complexity score based on control structures
3. **Detect Issues**: Finds code smells (long code, too many conditionals, TODOs)
4. **Suggest Improvements**: Generates suggestions based on detected issues
5. **Calculate Quality**: Computes overall quality score
6. **Check Threshold**: Verifies if quality meets threshold
7. **Loop**: If threshold not met, loops back to suggest improvements

### Example Usage

```python
import requests

# 1. Create the example workflow
response = requests.post("http://localhost:8000/graph/create/example")
graph_id = response.json()["graph_id"]

# 2. Run the workflow
run_response = requests.post("http://localhost:8000/graph/run", json={
    "graph_id": graph_id,
    "initial_state": {
        "code": """
def complex_function():
    if True:
        if True:
            if True:
                pass
    for i in range(10):
        for j in range(10):
            pass
    # TODO: Fix this
    """,
        "threshold": 70
    }
})

result = run_response.json()
print(f"Quality Score: {result['final_state']['quality_score']}")
print(f"Issues Found: {result['final_state']['issue_count']}")
```

## How the Workflow Engine Works

### Core Concepts

1. **Node**: A Python function that takes state (dict) and returns updated state
   ```python
   def my_node(state):
       state["value"] = state.get("value", 0) + 1
       return state
   ```

2. **Graph**: Collection of nodes connected by edges
   ```python
   graph.add_node("node1", my_node)
   graph.add_edge("node1", "node2")  # node1 runs before node2
   ```

3. **State**: Dictionary passed between nodes
   ```python
   state = {"input": "data", "step": 1}
   ```

4. **Execution**: Starts from entry node, follows edges, executes each node
   - Supports conditional routing via `state["route_to"]`
   - Supports looping via `state["loop_continue"]` and `state["loop_node"]`

### Tool Registry

Tools are reusable functions stored in a registry:
```python
from app.tools import tool_registry

# Use a tool in a node
def my_node(state):
    result = tool_registry.get("detect_smells")(state["code"])
    state.update(result)
    return state
```

## What the Engine Supports

✅ **Basic Features:**
- Node execution with state passing
- Sequential execution via edges
- Shared state dictionary
- Execution logging
- Tool registry

✅ **Advanced Features:**
- Conditional routing (via state flags)
- Looping (via loop_continue flag)
- Error handling
- Run tracking

## What I Would Improve With More Time

1. **Dynamic Node Creation**: Currently, nodes need pre-defined functions. Would add a way to create nodes from API requests with function definitions.

2. **Better Conditional Routing**: More sophisticated branching logic (if-else, switch-case patterns).

3. **Async Execution**: Make long-running nodes truly asynchronous with background tasks.

4. **WebSocket Streaming**: Real-time execution logs via WebSocket instead of polling.

5. **Persistence**: Store graphs and runs in a database (SQLite/PostgreSQL) instead of in-memory.

6. **Visualization**: Add an endpoint to visualize the graph structure.

7. **Error Recovery**: Retry mechanisms and better error handling strategies.

8. **State Validation**: Use Pydantic models for state validation instead of plain dictionaries.

9. **Parallel Execution**: Support for running multiple nodes in parallel when they don't depend on each other.

10. **Graph Serialization**: Save/load graphs to/from JSON files.

## Design Decisions

- **In-Memory Storage**: Chosen for simplicity. Easy to replace with database later.
- **Dictionary State**: Simple and flexible. Could be upgraded to Pydantic models.
- **Simple Loop Mechanism**: Uses flags in state rather than complex loop constructs.
- **Class-Based Design**: Clear separation of concerns (Node, WorkflowGraph, ToolRegistry).

## Testing the API

You can test using curl, Postman, or the Swagger UI at `/docs`.

Example with curl:
```bash
# Create workflow
curl -X POST http://localhost:8000/graph/create/example

# Run workflow (replace graph_id)
curl -X POST http://localhost:8000/graph/run \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "your-graph-id", "initial_state": {"code": "def test(): pass", "threshold": 70}}'
```

## Notes

- This is a minimal implementation focused on clarity and correctness
- Code is intentionally simple and well-commented for learning purposes
- No external dependencies beyond FastAPI and standard library
- Suitable for understanding workflow engine concepts

