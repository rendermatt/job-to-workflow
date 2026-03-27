# Hello World - Getting Started with Render Workflows

The simplest possible workflow example to help you understand the basics of Render Workflows. Perfect for beginners!

## What You'll Learn

This example teaches the fundamental concepts:
- **What is a Task?** - A function decorated with `@app.task` that can be executed as a workflow
- **What is a Subtask?** - A task called by another task using `await`
- **How to Orchestrate** - Combining multiple tasks to create workflows
- **How to Deploy** - Getting your first workflow running on Render

## Use Case

Simple number processing to demonstrate workflow patterns without complex business logic. If you can understand this example, you can build any workflow!

## Workflow Structure

```
calculate_and_process (multi-step orchestrator)
  ├── add_doubled_numbers
  │   ├── double (subtask #1)
  │   └── double (subtask #2)
  └── process_numbers
      ├── double (subtask for item 1)
      ├── double (subtask for item 2)
      └── double (subtask for item N)
```

## Understanding Tasks and Subtasks

### What is a Task?

A **task** is simply a Python function decorated with `@app.task`. It becomes a workflow step that Render can execute:

```python
from render_sdk import Workflows

app = Workflows()

@app.task
def double(x: int) -> int:
    """A simple task that doubles a number"""
    return x * 2

app.start()
```

### What is a Subtask?

A **subtask** is when one task calls another task using `await`. This is how you compose workflows:

```python
@app.task
async def add_doubled_numbers(a: int, b: int) -> dict:
    # Call 'double' as a subtask using await
    doubled_a = await double(a)  # ← This is a subtask call!
    doubled_b = await double(b)  # ← This is also a subtask call!

    return {
        "sum": doubled_a + doubled_b
    }
```

### Why Use Subtasks?

1. **Reusability**: Write `double` once, use it everywhere
2. **Composition**: Build complex workflows from simple building blocks
3. **Visibility**: Render shows you each subtask execution in the dashboard
4. **Testing**: Test individual tasks independently

## Local Development

### Prerequisites
- Python 3.10+

### Setup and Run

```bash
# Navigate to example directory
cd hello-world

# Install dependencies
pip install -r requirements.txt

# Run the workflow service
python main.py
```

The service will start and register all tasks. You'll see output like:

```
Starting Hello World Workflow Service
Registered tasks:
  - double(x)
  - add_doubled_numbers(a, b)
  - process_numbers(numbers)
  - calculate_and_process(a, b, more_numbers)
Ready to accept task executions!
```

## Deploying to Render

### Service Configuration

**Service Type**: Workflow

**Build Command**:
```bash
cd hello-world && pip install -r requirements.txt
```

**Start Command**:
```bash
cd hello-world && python main.py
```

### Environment Variables

Required:
- `RENDER_API_KEY` - Your Render API key (from Render dashboard)

### Deployment Steps

1. **Create Workflow Service**
   - Go to Render Dashboard
   - Click "New +" → "Workflow"
   - Connect your repository
   - Name: `hello-world-workflows`

2. **Configure Build Settings**
   - Build Command: `cd hello-world && pip install -r requirements.txt`
   - Start Command: `cd hello-world && python main.py`

3. **Set Environment Variables**
   - Add `RENDER_API_KEY` in the Environment section
   - Get API key from: Render Dashboard → Account Settings → API Keys

4. **Deploy**
   - Click "Create Workflow"
   - Render will build and start your workflow service

## Testing in Render Dashboard

Once deployed, test your workflows directly in the Render Dashboard:

### How to Test

1. Go to your Workflow service in Render Dashboard
2. Click the **"Manual Run"** or **"Start Task"** button
3. Select the task you want to test
4. Enter the task input as JSON in the text area
5. Click **"Start task"**

### Example Task Inputs

**Important:** The hello-world workflow expects direct values and arrays, not JSON objects. Use `5` instead of `{"x": 5}`, and `[3, 4]` instead of `{"a": 3, "b": 4}`.

**Recommended Starting Point:** Start with `double` - the simplest possible task, then work your way up to more complex examples.

---

**Test the basic task:**

Task: `double`

Input:
```json
5
```

Expected output: `10`

---

**Test subtask calling:**

Task: `add_doubled_numbers`

Input:
```json
[3, 4]
```

Expected output:
```json
{
  "original_numbers": [3, 4],
  "doubled_numbers": [6, 8],
  "sum_of_doubled": 14,
  "explanation": "3 doubled is 6, 4 doubled is 8, sum is 14"
}
```

This task calls `double` twice as subtasks!

---

**Test subtask in a loop:**

Task: `process_numbers`

Input:
```json
[1, 2, 3, 4, 5]
```

Expected output:
```json
{
  "original_numbers": [1, 2, 3, 4, 5],
  "doubled_numbers": [2, 4, 6, 8, 10],
  "count": 5,
  "explanation": "Processed 5 numbers through the double subtask"
}
```

This calls `double` as a subtask 5 times (once for each number)!

---

**Test multi-step workflow:**

Task: `calculate_and_process`

Input:
```json
[2, 3, 10, 20, 30]
```

This is the most complex example - it calls `add_doubled_numbers` and `process_numbers` as subtasks, which in turn call `double` multiple times. Watch the Render Dashboard to see the entire execution tree!

## Triggering via SDK

Once deployed, trigger workflows via the Render Client SDK:

```python
from render_sdk import Render

# Uses RENDER_API_KEY environment variable automatically
render = Render()

# Call the simple double task
task_run = await render.workflows.run_task(
    "hello-world-workflows/double",
    {"x": 5}
)
result = await task_run
print(f"Result: {result.results}")  # Output: 10

# Call the subtask orchestration example
task_run = await render.workflows.run_task(
    "hello-world-workflows/add_doubled_numbers",
    {"a": 3, "b": 4}
)
result = await task_run
print(f"Sum of doubled: {result.results['sum_of_doubled']}")  # Output: 14
```

## Tasks Explained

### `double(x: int) -> int`

The simplest possible task. Takes a number, doubles it, returns the result.

**Purpose**: Show what a basic task looks like.

**Can be called as a subtask**: Yes! Other tasks call this.

---

### `add_doubled_numbers(a: int, b: int) -> dict`

Demonstrates the fundamental subtask pattern.

**What it does**:
1. Calls `double(a)` as a subtask
2. Calls `double(b)` as a subtask
3. Adds the results together

**Purpose**: Show how to call tasks as subtasks using `await`.

**Key Pattern**:
```python
result = await double(a)  # ← Subtask call with await
```

---

### `process_numbers(numbers: list[int]) -> dict`

Demonstrates calling a subtask in a loop.

**What it does**:
1. Takes a list of numbers
2. Calls `double` as a subtask for each number
3. Collects all the results

**Purpose**: Show how to process lists/batches using subtasks.

**Key Pattern**:
```python
for num in numbers:
    doubled = await double(num)  # ← Subtask call in a loop
```

---

### `calculate_and_process(a: int, b: int, more_numbers: list[int]) -> dict`

Demonstrates a multi-step workflow with multiple subtask calls.

**What it does**:
1. Calls `add_doubled_numbers` as a subtask
2. Calls `process_numbers` as a subtask
3. Combines the results

**Purpose**: Show how to chain multiple subtasks to create complex workflows.

**Key Pattern**:
```python
step1 = await add_doubled_numbers(a, b)   # ← First subtask
step2 = await process_numbers(numbers)     # ← Second subtask
# Combine results
```

## Key Concepts

### The `@app.task` Decorator

Every workflow function needs the `@app.task` decorator:

```python
from render_sdk import Workflows

app = Workflows()

@app.task
def my_task():
    return "Hello World"

app.start()
```

### The `async` Keyword

Tasks that call other tasks as subtasks must be `async`:

```python
@app.task
async def orchestrator():
    result = await subtask()  # ← Calls another task
    return result
```

### The `await` Keyword

Use `await` to call a task as a subtask:

```python
result = await task_name(arguments)
```

Without `await`, you're just calling a regular Python function!

### Task Registration

All `@app.task` decorated functions are registered when defined. Call `app.start()` at the end of your module to start the workflow service and make all registered tasks available for execution.

## Common Patterns

### Pattern 1: Sequential Subtasks

Execute subtasks one after another:

```python
@app.task
async def sequential():
    step1 = await task_a()
    step2 = await task_b(step1)  # Uses result from step1
    step3 = await task_c(step2)  # Uses result from step2
    return step3
```

### Pattern 2: Independent Subtasks

Execute subtasks where order doesn't matter:

```python
@app.task
async def independent():
    result_a = await task_a()
    result_b = await task_b()
    return combine(result_a, result_b)
```

### Pattern 3: Subtasks in a Loop

Process a list by calling a subtask for each item:

```python
@app.task
async def batch_process(items: list):
    results = []
    for item in items:
        result = await process_item(item)
        results.append(result)
    return results
```

### Pattern 4: Nested Subtasks

Subtasks can call other subtasks:

```python
@app.task
async def level_1():
    return await level_2()

@app.task
async def level_2():
    return await level_3()

@app.task
def level_3():
    return "Done!"
```

## Next Steps

Once you understand this example, check out:

1. **ETL Job** - Learn data processing patterns with CSV files
2. **File Processing** - Learn parallel execution with `asyncio.gather()`
3. **Data Pipeline** - Learn complex multi-stage workflows
4. **OpenAI Agent** - Learn advanced patterns with AI integration
5. **File Analyzer** - Learn how to call workflows from APIs using Client SDK

## Troubleshooting

### "Task not found" error

Make sure:
- The service is deployed and running
- The task name matches exactly (case-sensitive)
- You're using the correct service slug

### Import errors

Make sure:
- `requirements.txt` includes `render-sdk>=0.5.0`
- Build command is running correctly
- Python version is 3.10 or higher

### Subtask calls not working

Make sure:
- Your task function is marked `async`
- You're using `await` before the task call
- Both tasks are decorated with `@app.task`

## Important Notes

- **Python-only**: Workflows are only supported in Python via render-sdk
- **No Blueprint Support**: Workflows don't support render.yaml blueprint configuration
- **Service Type**: Deploy as a Workflow service on Render (not Background Worker or Web Service)
- **Async Functions**: Tasks that call subtasks must be declared as `async`

## Resources

- [Render Workflows Documentation](https://docs.render.com/workflows)
- [Render SDK on PyPI](https://pypi.org/project/render-sdk/)
- [Render Dashboard](https://dashboard.render.com/)

---

**Start simple, build powerful workflows!**
