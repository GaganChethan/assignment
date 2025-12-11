# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Start the Server

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 3: Test the API

### Option A: Using the Test Script

In a new terminal:
```bash
python test_example.py
```

### Option B: Using the Browser

1. Open `http://localhost:8000/docs` (Swagger UI)
2. Click on `POST /graph/create/example`
3. Click "Try it out" → "Execute"
4. Copy the `graph_id` from the response
5. Click on `POST /graph/run`
6. Click "Try it out"
7. Paste the `graph_id` and add initial state:
```json
{
  "graph_id": "paste-graph-id-here",
  "initial_state": {
    "code": "def test():\n    if True:\n        pass",
    "threshold": 70
  }
}
```
8. Click "Execute"
9. See the results!

### Option C: Using curl

```bash
# Create workflow
curl -X POST http://localhost:8000/graph/create/example

# Run workflow (replace YOUR_GRAPH_ID)
curl -X POST http://localhost:8000/graph/run \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "YOUR_GRAPH_ID",
    "initial_state": {
      "code": "def hello():\n    print(\"world\")",
      "threshold": 70
    }
  }'
```

## What Happens?

1. The workflow extracts functions from your code
2. Checks complexity (counts if/for/while statements)
3. Detects issues (long code, too many conditionals, TODOs)
4. Suggests improvements
5. Calculates a quality score
6. Checks if quality meets the threshold
7. Loops back if quality is too low

## Understanding the Response

The response includes:
- `run_id`: Unique ID for this execution
- `final_state`: The final state after all nodes executed
  - `quality_score`: Overall code quality (0-100)
  - `issue_count`: Number of issues found
  - `suggestions`: List of improvement suggestions
- `execution_log`: Step-by-step log of what happened

## Common Issues

**"Connection refused"**: Make sure the server is running (Step 2)

**"Graph not found"**: Make sure you copied the correct `graph_id`

**Import errors**: Make sure you installed requirements: `pip install -r requirements.txt`

