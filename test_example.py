"""
Simple test script to verify the workflow engine works
Run this after starting the server with: uvicorn app.main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_workflow():
    """Test the code review workflow"""
    
    print("=" * 50)
    print("Testing Workflow Engine")
    print("=" * 50)
    
    # 1. Create example workflow
    print("\n1. Creating example workflow...")
    response = requests.post(f"{BASE_URL}/graph/create/example")
    if response.status_code == 200:
        graph_id = response.json()["graph_id"]
        print(f"   ✓ Graph created: {graph_id}")
    else:
        print(f"   ✗ Failed: {response.text}")
        return
    
    # 2. Run the workflow
    print("\n2. Running workflow...")
    test_code = """
def complex_function():
    if True:
        if True:
            if True:
                pass
    for i in range(10):
        for j in range(10):
            pass
    # TODO: Fix this
    # FIXME: This needs work
    """
    
    run_data = {
        "graph_id": graph_id,
        "initial_state": {
            "code": test_code,
            "threshold": 70
        }
    }
    
    response = requests.post(f"{BASE_URL}/graph/run", json=run_data)
    if response.status_code == 200:
        result = response.json()
        run_id = result["run_id"]
        final_state = result["final_state"]
        
        print(f"   ✓ Run completed: {run_id}")
        print(f"   ✓ Quality Score: {final_state.get('quality_score', 'N/A')}")
        print(f"   ✓ Issues Found: {final_state.get('issue_count', 0)}")
        print(f"   ✓ Complexity Score: {final_state.get('complexity_score', 'N/A')}")
        print(f"   ✓ Quality Met: {final_state.get('quality_met', False)}")
        
        if final_state.get('suggestions'):
            print(f"   ✓ Suggestions: {len(final_state['suggestions'])}")
            for suggestion in final_state['suggestions']:
                print(f"     - {suggestion}")
    else:
        print(f"   ✗ Failed: {response.text}")
        return
    
    # 3. Get run state
    print("\n3. Getting run state...")
    response = requests.get(f"{BASE_URL}/graph/state/{run_id}")
    if response.status_code == 200:
        state_data = response.json()
        print(f"   ✓ Status: {state_data['status']}")
        print(f"   ✓ Execution steps: {len(state_data['execution_log'])}")
    else:
        print(f"   ✗ Failed: {response.text}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_workflow()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server.")
        print("Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")

