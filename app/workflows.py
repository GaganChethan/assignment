"""
Example Workflows
This file contains pre-built workflow examples
"""

from app.engine import WorkflowGraph
from app.tools import tool_registry


def create_code_review_workflow() -> WorkflowGraph:
    """
    Create a Code Review Mini-Agent workflow
    
    Steps:
    1. Extract functions
    2. Check complexity
    3. Detect basic issues
    4. Suggest improvements
    5. Loop until quality_score >= threshold
    """
    graph = WorkflowGraph("code_review_workflow")
    
    # Define node functions
    def extract_functions(state):
        """Extract functions from code"""
        code = state.get("code", "")
        # Simple extraction: count function definitions
        function_count = code.count("def ")
        state["function_count"] = function_count
        state["extracted"] = True
        return state
    
    def check_complexity_node(state):
        """Check code complexity"""
        code = state.get("code", "")
        result = tool_registry.get("check_complexity")(code)
        state.update(result)
        return state
    
    def detect_issues_node(state):
        """Detect code issues"""
        code = state.get("code", "")
        result = tool_registry.get("detect_smells")(code)
        state.update(result)
        return state
    
    def suggest_improvements(state):
        """Suggest improvements based on issues"""
        issues = state.get("issues", [])
        suggestions = []
        
        for issue in issues:
            if "too long" in issue.lower():
                suggestions.append("Consider breaking into smaller functions")
            elif "conditionals" in issue.lower():
                suggestions.append("Consider using switch/case or polymorphism")
            elif "TODO" in issue:
                suggestions.append("Remove TODO comments before production")
        
        state["suggestions"] = suggestions
        return state
    
    def calculate_quality(state):
        """Calculate quality score"""
        result = tool_registry.get("calculate_quality_score")(state)
        state.update(result)
        return state
    
    def check_threshold(state):
        """Check if quality score meets threshold"""
        quality_score = state.get("quality_score", 0)
        threshold = state.get("threshold", 70)
        
        if quality_score >= threshold:
            state["quality_met"] = True
            state["loop_continue"] = False  # Stop looping
        else:
            state["quality_met"] = False
            # Suggest improvements and loop back
            state["loop_continue"] = True
            state["loop_node"] = "suggest_improvements"  # Loop back to improvements
        
        return state
    
    # Add nodes to graph
    graph.add_node("extract_functions", extract_functions)
    graph.add_node("check_complexity", check_complexity_node)
    graph.add_node("detect_issues", detect_issues_node)
    graph.add_node("suggest_improvements", suggest_improvements)
    graph.add_node("calculate_quality", calculate_quality)
    graph.add_node("check_threshold", check_threshold)
    
    # Define edges (execution flow)
    graph.add_edge("extract_functions", "check_complexity")
    graph.add_edge("check_complexity", "detect_issues")
    graph.add_edge("detect_issues", "suggest_improvements")
    graph.add_edge("suggest_improvements", "calculate_quality")
    graph.add_edge("calculate_quality", "check_threshold")
    # Loop: if threshold not met, go back to suggest_improvements
    # (handled by loop_continue flag in check_threshold node)
    
    return graph

