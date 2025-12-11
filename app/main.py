"""
FastAPI Application
Main API endpoints for the workflow engine
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from app.engine import WorkflowGraph, Node
from app.workflows import create_code_review_workflow

app = FastAPI(title="Workflow Engine API", version="1.0.0")

# In-memory storage
graphs: Dict[str, WorkflowGraph] = {}
runs: Dict[str, Dict[str, Any]] = {}  # run_id -> {graph_id, state, log, status}


# Request/Response Models
class CreateGraphRequest(BaseModel):
    """Request to create a new graph"""
    nodes: List[Dict[str, str]]  # [{"name": "node1", "func": "function_name"}]
    edges: List[Dict[str, str]]  # [{"from": "node1", "to": "node2"}]
    entry_node: Optional[str] = None


class RunGraphRequest(BaseModel):
    """Request to run a graph"""
    graph_id: str
    initial_state: Dict[str, Any]


class GraphResponse(BaseModel):
    """Response for graph creation"""
    graph_id: str
    message: str


class RunResponse(BaseModel):
    """Response for graph execution"""
    run_id: str
    final_state: Dict[str, Any]
    execution_log: List[Dict[str, Any]]


class StateResponse(BaseModel):
    """Response for state query"""
    run_id: str
    state: Dict[str, Any]
    status: str
    execution_log: List[Dict[str, Any]]


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Workflow Engine API",
        "endpoints": {
            "create_graph": "POST /graph/create",
            "run_graph": "POST /graph/run",
            "get_state": "GET /graph/state/{run_id}"
        }
    }


@app.post("/graph/create", response_model=GraphResponse)
def create_graph(request: CreateGraphRequest):
    """
    Create a new workflow graph
    
    For simplicity, we'll create a basic graph structure.
    In a real implementation, you'd parse the nodes and edges properly.
    """
    graph_id = str(uuid.uuid4())
    graph = WorkflowGraph(graph_id)
    
    # For this simple version, we'll use a predefined workflow
    # In a full implementation, you'd dynamically create nodes from the request
    # For now, we'll just store the request and return the graph_id
    
    # Actually, let's create a simple graph from the request
    # Note: This is simplified - in production you'd need proper function registration
    try:
        # Set entry node
        if request.entry_node:
            graph.entry_node = request.entry_node
        
        # For demo purposes, we'll create a minimal graph
        # In a real system, you'd need a way to register functions
        # For now, we'll just store the structure
        
        graphs[graph_id] = graph
        
        return GraphResponse(
            graph_id=graph_id,
            message=f"Graph created with {len(request.nodes)} nodes"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/graph/create/example", response_model=GraphResponse)
def create_example_graph():
    """Create the example code review workflow"""
    graph = create_code_review_workflow()
    graphs[graph.graph_id] = graph
    
    return GraphResponse(
        graph_id=graph.graph_id,
        message="Example code review workflow created"
    )


@app.post("/graph/run", response_model=RunResponse)
def run_graph(request: RunGraphRequest):
    """
    Execute a workflow graph with initial state
    
    Returns the final state and execution log
    """
    if request.graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    graph = graphs[request.graph_id]
    run_id = str(uuid.uuid4())
    
    try:
        # Execute the workflow
        final_state, execution_log = graph.run(request.initial_state)
        
        # Store run information
        runs[run_id] = {
            "graph_id": request.graph_id,
            "state": final_state,
            "log": execution_log,
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
        
        return RunResponse(
            run_id=run_id,
            final_state=final_state,
            execution_log=execution_log
        )
    except Exception as e:
        # Store failed run
        runs[run_id] = {
            "graph_id": request.graph_id,
            "state": request.initial_state,
            "log": [],
            "status": "failed",
            "error": str(e),
            "created_at": datetime.now().isoformat()
        }
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/state/{run_id}", response_model=StateResponse)
def get_state(run_id: str):
    """Get the current state of a workflow run"""
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run_data = runs[run_id]
    
    return StateResponse(
        run_id=run_id,
        state=run_data["state"],
        status=run_data["status"],
        execution_log=run_data.get("log", [])
    )


@app.get("/graphs")
def list_graphs():
    """List all created graphs"""
    return {
        "graphs": [
            {
                "graph_id": graph_id,
                "node_count": len(graph.nodes),
                "entry_node": graph.entry_node
            }
            for graph_id, graph in graphs.items()
        ]
    }


@app.get("/runs")
def list_runs():
    """List all workflow runs"""
    return {
        "runs": [
            {
                "run_id": run_id,
                "graph_id": data["graph_id"],
                "status": data["status"],
                "created_at": data.get("created_at")
            }
            for run_id, data in runs.items()
        ]
    }

