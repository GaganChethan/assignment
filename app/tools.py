"""
Tool Registry
Simple dictionary-based registry for tools that nodes can use
"""

from typing import Dict, Callable, Any, List


class ToolRegistry:
    """Registry for storing and retrieving tools (Python functions)"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable):
        """Register a tool function"""
        self.tools[name] = func
    
    def get(self, name: str) -> Callable:
        """Get a tool by name"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self.tools[name]
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())


# Global tool registry instance
tool_registry = ToolRegistry()


# Example tools (these can be used by nodes)
def detect_smells(code: str) -> Dict[str, Any]:
    """Simple code smell detection"""
    issues = []
    if len(code) > 1000:
        issues.append("Code too long")
    if code.count("if") > 10:
        issues.append("Too many conditionals")
    if "TODO" in code or "FIXME" in code:
        issues.append("Contains TODO/FIXME")
    
    return {"issues": issues, "issue_count": len(issues)}


def check_complexity(code: str) -> Dict[str, Any]:
    """Simple complexity check"""
    complexity_score = 0
    complexity_score += code.count("if") * 2
    complexity_score += code.count("for") * 3
    complexity_score += code.count("while") * 4
    complexity_score += code.count("def") * 1
    
    return {"complexity_score": complexity_score}


def calculate_quality_score(state: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall quality score"""
    issue_count = state.get("issue_count", 0)
    complexity_score = state.get("complexity_score", 0)
    
    # Simple scoring: lower is better
    quality_score = 100 - (issue_count * 10) - (complexity_score * 2)
    quality_score = max(0, quality_score)  # Don't go below 0
    
    return {"quality_score": quality_score}


# Register example tools
tool_registry.register("detect_smells", detect_smells)
tool_registry.register("check_complexity", check_complexity)
tool_registry.register("calculate_quality_score", calculate_quality_score)

