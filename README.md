# PDF Threat Hunter 🕵️‍♂️📄 *(Work‑in‑Progress)*

**PDF Threat Hunter** is an open‑source project aiming to provide multi‑agent
threat‑hunting for PDF files using LangGraph subgraph architecture.  
The first milestone – a static‑analysis agent – is **already functional**, and has been 
restructured as a reusable subgraph within a larger orchestration framework.

**🚀 LangGraph Dev Ready**: All components are designed to work seamlessly with `langgraph dev` 
without requiring memory/persistence or thread configuration.

---

## Quick Start

```bash
git clone https://github.com/your‑org/pdf-threat-hunter.git
cd pdf-threat-hunter

python -m venv .venv
source .venv/bin/activate        # Windows → .\.venv\Scripts\activate

pip install -r requirements.txt
pip install -e .

# 1) copy the sample env and add your keys
cp .env.example .env
#    then edit the file or export variables manually:
#    export OPENAI_API_KEY="sk-xxxxxxxx"
#    export LANGSMITH_PROJECT="pdf-threat-hunter"

# 2) analyse a sample file using the main graph
python main_graph.py

# 3) or run the advanced version with subgraph streaming
python main_graph_advanced.py

# 4) or use the original static analysis directly
python static_analysis_agent.py
```

For LangGraph development server:

```bash
langgraph dev
# Serves the main graph at http://localhost:8123
```

---

## Architecture Overview

The system now uses a **modular subgraph architecture**:

- **Main Graph** (`main_graph.py`) - High-level orchestration with simple state
- **Static Analysis Subgraph** (`static_analysis_agent.py`) - Detailed PDF analysis 
- **Advanced Patterns** (`main_graph_advanced.py`) - Demonstrates multiple integration approaches

### State Flow

```
Main Graph State:
├── pdf_path: str
└── static_analysis_report: Optional[str]

↓ (transforms to)

Subgraph State:
├── pdf_filepath: str
├── messages: List[BaseMessage]
├── accumulated_findings: List[str]
├── command_history: List[Dict]
└── ... (detailed internal state)
```

### LangGraph Dev Compatibility

All graphs are **stateless** and **memory-free** for seamless development:

- ✅ No checkpointers or persistence required
- ✅ No thread_id configuration needed  
- ✅ Clean state transformations between graphs
- ✅ Compatible with `langgraph dev` out of the box

---

## Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY`       | ✔︎ | main LLM backend |
| `ANTHROPIC_API_KEY`    |    | future alternate LLM |
| `LANGSMITH_API_KEY`    |    | optional tracing backend |
| `LANGSMITH_PROJECT`    |    | project name shown in LangSmith |
| `LANGSMITH_TRACING_V2` |    | set to `true` to enable tracing |

Create a `.env` from the provided **.env.example** or export variables in your shell.

---

## How It Works

### Main Graph (Orchestration Layer)
1. **Input Validation** - Ensures PDF file exists and is accessible
2. **Subgraph Invocation** - Calls the static analysis subgraph with transformed state
3. **Result Processing** - Extracts and formats the final analysis report

### Static Analysis Subgraph (Analysis Layer)
1. **SafeShell** executes only a strict allow‑list of command‑line tools
2. A **planning LLM** reasons about each tool's output and decides what to ask for next
3. **Plan → Act → Reflect** loop continues until analysis is complete
4. Detailed findings and extracted artifacts are compiled into a final report

### Subgraph Integration Patterns

**Pattern 1: Wrapper Function** (Simple)
```python
def run_static_analysis_subgraph(state: MainGraphState) -> MainGraphState:
    # Transform state, invoke subgraph, transform result
    result = static_analysis_subgraph.invoke(transformed_input)
    return {"static_analysis_report": result["final_report"]}
```

**Pattern 2: Direct Subgraph Node** (Advanced)
```python
# Add compiled subgraph directly as a node
workflow.add_node("static_analysis", subgraph_wrapper)
```

---

## File Structure

```
pdf-threat-hunter-agent/
├── main_graph.py                 # Main orchestration graph
├── main_graph_advanced.py        # Advanced subgraph patterns
├── static_analysis_agent.py      # Static analysis subgraph
├── static_analysis_prompts.py    # LLM prompts for analysis
├── langgraph.json               # LangGraph configuration
├── SUBGRAPH_IMPLEMENTATION.md   # Detailed architecture docs
├── requirements.txt             # Dependencies
└── analysis_tools/              # Command-line tools (pdfid, etc.)
```

---

## Usage Examples

### Basic Analysis
```python
from main_graph import main_app

result = main_app.invoke({"pdf_path": "./suspicious.pdf"})
print(result["static_analysis_report"])
```

### Streaming with Subgraph Visibility
```python
from main_graph_advanced import main_app_wrapper

for chunk in main_app_wrapper.stream(input_data, subgraphs=True):
    namespace, data = chunk
    if namespace == ():
        print(f"Main Graph: {data}")
    else:
        print(f"Subgraph: {data}")
```

---

## Key Benefits of Subgraph Architecture

1. **Modularity** - Static analysis can be reused in different contexts
2. **Separation of Concerns** - Clear boundaries between orchestration and analysis
3. **Scalability** - Easy to add new analysis types as additional subgraphs
4. **Maintainability** - Each component has focused responsibilities
5. **Observability** - Better streaming and debugging capabilities
6. **Dev-Friendly** - Works seamlessly with LangGraph development tools

---

## Roadmap

- [x] Static analysis agent *(initial version)*
- [x] **Subgraph architecture** *(current milestone)*
- [x] **LangGraph dev compatibility** *(current milestone)*
- [ ] Dynamic analysis subgraph
- [ ] ML classification subgraph  
- [ ] Vision agent for rendered‑page heuristics
- [ ] External threat‑intel enrichment subgraph
- [ ] Multi‑agent orchestrator with parallel subgraphs
- [ ] Docker distribution & web UI

---

## Contributing

We welcome issues, pull requests and feature ideas.  
Please run the linter and test suite before submitting a PR.

See `SUBGRAPH_IMPLEMENTATION.md` for detailed architecture documentation.

---

## License

MIT © 2025 Gorelik
