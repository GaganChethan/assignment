"""
Simple Workflow Engine
This is the core engine that manages nodes, state, and execution flow.
"""

from typing import Dict, List, Callable, Any, Optional
from enum import Enum


class NodeStatus(Enum):
    """Status of a node execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Node:
    """Represents a single node in the workflow"""
    
    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func
        self.status = NodeStatus.PENDING
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node function with the current state"""
        self.status = NodeStatus.RUNNING
        try:
            # Node function receives state and returns updated state
            updated_state = self.func(state)
            self.status = NodeStatus.COMPLETED
            return updated_state
        except Exception as e:
            self.status = NodeStatus.FAILED
            raise e


class WorkflowGraph:
    """Main workflow graph that manages nodes and their connections"""
    
    def __init__(self, graph_id: str):
        self.graph_id = graph_id
        self.nodes: Dict[str, Node] = {}  # node_name -> Node object
        self.edges: Dict[str, str] = {}  # from_node -> to_node
        self.entry_node: Optional[str] = None  # Starting node
    
    def add_node(self, name: str, func: Callable):
        """Add a node to the graph"""
        self.nodes[name] = Node(name, func)
        # If this is the first node, make it the entry node
        if self.entry_node is None:
            self.entry_node = name
    
    def add_edge(self, from_node: str, to_node: str):
        """Connect two nodes (from_node runs before to_node)"""
        if from_node not in self.nodes:
            raise ValueError(f"Node '{from_node}' does not exist")
        if to_node not in self.nodes:
            raise ValueError(f"Node '{to_node}' does not exist")
        self.edges[from_node] = to_node
    
    def get_next_node(self, current_node: str) -> Optional[str]:
        """Get the next node to execute after current_node"""
        return self.edges.get(current_node)
    
    def run(self, initial_state: Dict[str, Any]) -> tuple:
        """
        Execute the workflow starting from entry node
        
        Returns:
            (final_state, execution_log)
        """
        if self.entry_node is None:
            raise ValueError("No entry node defined")
        
        state = initial_state.copy()
        execution_log = []
        current_node_name = self.entry_node
        visited_nodes = set()
        
        # Simple loop detection (max iterations)
        max_iterations = 100
        iteration = 0
        
        while current_node_name and iteration < max_iterations:
            iteration += 1
            
            # Check if we've been here too many times (loop protection)
            if current_node_name in visited_nodes and iteration > 10:
                # Check if we should continue looping based on state
                # This is handled by conditional edges in the workflow
                pass
            
            node = self.nodes[current_node_name]
            
            # Execute the node
            log_entry = {
                "node": current_node_name,
                "status": "running",
                "iteration": iteration
            }
            execution_log.append(log_entry)
            
            try:
                state = node.execute(state)
                log_entry["status"] = "completed"
                log_entry["state_snapshot"] = state.copy()
            except Exception as e:
                log_entry["status"] = "failed"
                log_entry["error"] = str(e)
                execution_log.append(log_entry)
                raise e
            
            visited_nodes.add(current_node_name)
            
            # Get next node
            next_node = self.get_next_node(current_node_name)
            
            # Handle conditional routing (check state for routing decisions)
            if next_node and next_node.startswith("if_"):
                # Simple conditional: if_next_node means check condition
                # For now, we'll use a simple approach: check state for routing
                actual_next = self._evaluate_conditional(next_node, state)
                current_node_name = actual_next
            else:
                current_node_name = next_node
            
            # Check for loop conditions (if state has loop_continue flag)
            if state.get("loop_continue", False):
                # Reset to entry or specified loop node
                loop_node = state.get("loop_node", self.entry_node)
                current_node_name = loop_node
                state["loop_continue"] = False  # Reset flag
                continue
            
            # Stop if no next node
            if current_node_name is None:
                break
        
        return state, execution_log
    
    def _evaluate_conditional(self, conditional_node: str, state: Dict[str, Any]) -> Optional[str]:
        """
        Simple conditional evaluation
        If state has 'route_to' key, use that, otherwise continue normally
        """
        if "route_to" in state:
            next_node = state.pop("route_to")  # Remove after using
            return next_node if next_node in self.nodes else None
        # Default: continue to next edge
        return None

