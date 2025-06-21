# PDF Threat Hunter - Subgraph Implementation

This document explains how the PDF Threat Hunter agent has been restructured to use LangGraph subgraphs, making the static analysis component a reusable subgraph within a larger main graph.

## Architecture Overview

The system now consists of:

1. **Main Graph** (`main_graph.py`) - High-level orchestration with simple state
2. **Static Analysis Subgraph** (`static_analysis_agent.py`) - Detailed PDF analysis with complex internal state
3. **Advanced Main Graph** (`main_graph_advanced.py`) - Demonstrates multiple subgraph integration patterns

## File Structure

```
pdf-threat-hunter-agent/
├── main_graph.py                 # Simple main graph implementation
├── main_graph_advanced.py        # Advanced subgraph patterns demonstration
├── static_analysis_agent.py      # Static analysis subgraph (unchanged)
├── langgraph.json               # Updated to point to main graph
└── SUBGRAPH_IMPLEMENTATION.md   # This documentation
```

## Main Graph State Schema

The main graph uses a simplified state schema:

```python
class MainGraphState(TypedDict):
    pdf_path: str                           # Input: Path to PDF file
    static_analysis_report: Optional[str]   # Output: Generated analysis report
```

## LangGraph Dev Compatibility

All graphs have been designed to work seamlessly with `langgraph dev`:

- **No Memory/Persistence**: Graphs are compiled without checkpointers
- **No Thread ID Required**: No configuration parameters needed
- **Stateless Execution**: Each invocation is independent
- **Clean State Management**: Simple state transformations between graphs

```python
# All graphs use this pattern:
app = workflow.compile()  # No checkpointer

# Invocation without config:
result = app.invoke(input_data)  # No thread_id needed
```

## Subgraph Integration Patterns

### Pattern 1: Wrapper Function Approach (`main_graph.py`)

This is the simpler approach where the subgraph is called from within a wrapper function:

```python
def run_static_analysis_subgraph(state: MainGraphState) -> MainGraphState:
    # Transform main graph state to subgraph input format
    subgraph_input = {
        "pdf_filepath": state["pdf_path"],
        "original_user_request": f"Analyze {state['pdf_path']}...",
        # ... other subgraph-specific fields
    }
    
    # Invoke the subgraph
    result = static_analysis_subgraph.invoke(subgraph_input)
    
    # Transform result back to main graph state
    return {
        **state,
        "static_analysis_report": result.get("final_report")
    }
```

**Pros:**
- Simple to understand and implement
- Full control over state transformation
- Easy to add pre/post processing logic
- Compatible with langgraph dev out of the box

**Cons:**
- Manual state transformation required
- Subgraph execution not visible in streaming

### Pattern 2: Direct Subgraph as Node (`main_graph_advanced.py`)

This approach demonstrates more sophisticated subgraph integration:

```python
# Create a wrapper subgraph that handles state transformation
def create_subgraph_wrapper():
    def subgraph_adapter(state: MainGraphState) -> MainGraphState:
        # Handle state transformation
        # ...
    
    wrapper_graph = StateGraph(MainGraphState)
    wrapper_graph.add_node("adapter", subgraph_adapter)
    # ...
    return wrapper_graph.compile()

# Use the wrapper as a direct node
workflow.add_node("static_analysis", create_subgraph_wrapper())
```

**Pros:**
- Cleaner graph structure
- Better streaming visibility
- More modular design
- Works with langgraph dev streaming

**Cons:**
- More complex implementation
- Additional wrapper layer

## Configuration Changes

The `langgraph.json` has been updated to point to the main graph:

```json
{
    "dependencies": ["."],
    "graphs": {
      "agent": "./main_graph.py:main_app"
    },
    "env": ".env"
}
```

## Usage Examples

### Basic Usage

```python
from main_graph import main_app

# Run analysis (no config needed)
result = main_app.invoke({
    "pdf_path": "./suspicious.pdf"
})

print(result["static_analysis_report"])
```

### Advanced Usage with Streaming

```python
from main_graph_advanced import main_app_wrapper

initial_input = {"pdf_path": "./suspicious.pdf"}

# Stream with subgraph visibility (no config needed)
for chunk in main_app_wrapper.stream(initial_input, subgraphs=True):
    namespace, data = chunk
    if namespace == ():
        print(f"Main Graph: {data}")
    else:
        print(f"Subgraph [{namespace}]: {data}")
```

### LangGraph Dev Usage

```bash
# Start development server
langgraph dev

# The server will expose the main graph at:
# http://localhost:8123
```

## Key Benefits of Subgraph Architecture

1. **Modularity**: Static analysis can be reused in other graphs
2. **Separation of Concerns**: Main graph handles orchestration, subgraph handles analysis
3. **Scalability**: Easy to add more analysis types as additional subgraphs
4. **Maintainability**: Each component has clear responsibilities
5. **Testability**: Components can be tested independently
6. **LangGraph Dev Compatible**: Works seamlessly with development server

## State Transformation Patterns

When working with different state schemas between parent and subgraph:

### Input Transformation
```python
# Main graph state -> Subgraph state
subgraph_input = {
    "pdf_filepath": main_state["pdf_path"],
    "original_user_request": f"Analyze {main_state['pdf_path']}...",
    # Initialize subgraph-specific fields
    "messages": [],
    "accumulated_findings": [],
    # ...
}
```

### Output Transformation
```python
# Subgraph state -> Main graph state
return {
    **main_state,
    "static_analysis_report": subgraph_result.get("final_report")
}
```

## Future Extensions

The subgraph architecture makes it easy to add new analysis types:

1. **Dynamic Analysis Subgraph**: For runtime PDF behavior analysis
2. **ML Classification Subgraph**: For machine learning-based threat detection
3. **Report Generation Subgraph**: For customizable report formatting
4. **Integration Subgraph**: For sending results to external systems

Each can be developed independently and composed in the main graph.

## Running the Implementation

1. **Simple version**: `python main_graph.py`
2. **Advanced version**: `python main_graph_advanced.py`
3. **Static analysis only**: `python static_analysis_agent.py`
4. **Via LangGraph Dev**: `langgraph dev` (uses `langgraph.json` configuration)

## Streaming and Debugging

The subgraph architecture provides better observability:

- Main graph updates show high-level progress
- Subgraph updates show detailed analysis steps (when using advanced patterns)
- Each component can be debugged independently
- State at each level is clearly separated
- No persistence complications during development

This makes it much easier to understand what's happening during analysis and to debug issues when they occur, especially when using the LangGraph development server.
