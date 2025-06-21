from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
import os
import uuid
import json

# Import the static analysis subgraph
from static_analysis_agent import app as static_analysis_subgraph


# --- Main Graph State ---
class MainGraphState(TypedDict):
    """Simple main graph state"""
    pdf_path: str
    static_analysis_report: Optional[str]
    analysis_id: Optional[str]


# --- Main Graph Nodes ---
def validate_and_initialize(state: MainGraphState) -> MainGraphState:
    """Validates PDF input and initializes the analysis"""
    pdf_path = state["pdf_path"]
    
    print("🔍 " + "="*50)
    print("🔍 PDF THREAT HUNTER - VALIDATION PHASE")
    print("🔍 " + "="*50)
    
    if not pdf_path:
        print("❌ ERROR: PDF path is required")
        raise ValueError("PDF path is required")
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: PDF file not found at: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
    
    if not pdf_path.lower().endswith('.pdf'):
        print("❌ ERROR: File must be a PDF (must have .pdf extension)")
        raise ValueError("File must be a PDF (must have .pdf extension)")
    
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())[:8]
    
    print(f"✅ PDF validation passed")
    print(f"📄 File: {pdf_path}")
    print(f"📊 Analysis ID: {analysis_id}")
    print(f"🚀 Initializing threat analysis...")
    
    return {
        **state,
        "analysis_id": analysis_id
    }


def run_static_analysis_subgraph(state: MainGraphState) -> MainGraphState:
    """Wrapper function that calls the static analysis subgraph"""
    pdf_path = state["pdf_path"]
    analysis_id = state["analysis_id"]
    
    print("\n🔬 " + "="*50)
    print("🔬 STATIC ANALYSIS PHASE")
    print("🔬 " + "="*50)
    print(f"📄 Analyzing: {os.path.basename(pdf_path)}")
    print(f"🆔 Analysis ID: {analysis_id}")
    
    # Prepare subgraph input
    subgraph_input = {
        "pdf_filepath": pdf_path,
        "original_user_request": f"Analyze the PDF file at {pdf_path} for any signs of malicious or suspicious activity.",
        "max_iterations": 10,
        "messages": [],
        "pdfid_output": "",
        "pdfstats_output": "",
        "command_history": [],
        "accumulated_findings": [],
        "code_blocks": {},
        "current_iteration": 0,
        "next_command_to_run": None,
        "command_reasoning": None,
        "analysis_complete": False,
        "final_report": None
    }
    
    print("⚙️  Running subgraph with streaming...")
    
    # Stream the subgraph execution to show internal progress
    subgraph_result = None
    iteration_count = 0
    
    for event in static_analysis_subgraph.stream(subgraph_input):
        if isinstance(event, dict):
            # Show subgraph progress details
            current_iter = event.get("current_iteration", 0)
            if current_iter > iteration_count:
                iteration_count = current_iter
                print(f"   📊 Subgraph iteration {current_iter}")
            
            # Show findings as they accumulate
            findings = event.get("accumulated_findings", [])
            if findings:
                print(f"   🔍 Found {len(findings)} security findings so far")
            
            # Show command execution
            next_cmd = event.get("next_command_to_run")
            if next_cmd:
                print(f"   🔧 Executing: {next_cmd[:50]}...")
            
            # Check if analysis is complete
            if event.get("analysis_complete"):
                print("   ✅ Subgraph analysis completed")
            
            subgraph_result = event
    
    # Extract results
    static_report = subgraph_result.get("final_report", "No report generated") if subgraph_result else "No report generated"
    findings_count = len(subgraph_result.get("accumulated_findings", [])) if subgraph_result else 0
    commands_run = len(subgraph_result.get("command_history", [])) if subgraph_result else 0
    
    print(f"📊 Analysis completed:")
    print(f"   • Commands executed: {commands_run}")
    print(f"   • Security findings: {findings_count}")
    print(f"   • Report length: {len(static_report)} characters")
    
    # Save files
    if analysis_id and subgraph_result:
        try:
            # Save JSON
            output_filename = f"pdf_analysis_report_{analysis_id}.json"
            with open(output_filename, 'w') as f:
                json.dump(subgraph_result, f, indent=2, default=lambda o: str(o))
            print(f"💾 Saved: {output_filename}")
            
            # Save Markdown
            if static_report:
                report_filename = f"pdf_analysis_report_{analysis_id}.md"
                with open(report_filename, 'w') as f:
                    f.write(f"# PDF Threat Analysis Report\n\n")
                    f.write(f"**PDF File:** {pdf_path}\n")
                    f.write(f"**Analysis ID:** {analysis_id}\n\n")
                    f.write("## Static Analysis Report\n\n")
                    f.write(static_report)
                print(f"📄 Saved: {report_filename}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save files: {e}")
    
    return {
        **state,
        "static_analysis_report": static_report
    }


def finalize_analysis(state: MainGraphState) -> MainGraphState:
    """Final processing and summary"""
    
    print("\n🏁 " + "="*50)
    print("🏁 FINALIZATION PHASE")
    print("🏁 " + "="*50)
    
    analysis_id = state.get("analysis_id", "unknown")
    pdf_path = state["pdf_path"]
    report = state.get("static_analysis_report", "")
    
    print(f"📄 Analysis complete: {os.path.basename(pdf_path)}")
    print(f"🆔 Analysis ID: {analysis_id}")
    
    if report:
        # Simple threat assessment
        if "suspicious" in report.lower() or "malicious" in report.lower():
            print("⚠️  THREAT DETECTED: Suspicious content found")
        elif "clean" in report.lower() or "benign" in report.lower():
            print("✅ ASSESSMENT: File appears clean")
        else:
            print("ℹ️  ASSESSMENT: Review report for details")
    else:
        print("⚠️  Warning: No report generated")
    
    print("🎯 Analysis complete!")
    
    return state


# --- Build the Main Graph ---
workflow = StateGraph(MainGraphState)
workflow.add_node("validate", validate_and_initialize)
workflow.add_node("analyze", run_static_analysis_subgraph)
workflow.add_node("finalize", finalize_analysis)

workflow.add_edge(START, "validate")
workflow.add_edge("validate", "analyze")
workflow.add_edge("analyze", "finalize")
workflow.add_edge("finalize", END)

# Compile the graph
app = workflow.compile()


# --- Main execution ---
if __name__ == "__main__":
    
    # Example PDF path
    pdf_path = "./hello_world_js.pdf"
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        pdf_path = "87c740d2b7c22f9ccabbdef412443d166733d4d925da0e8d6e5b310ccfc89e13.pdf"
    
    if not os.path.exists(pdf_path):
        print("❌ ERROR: No PDF found. Update pdf_path variable.")
        exit(1)
    
    print(f"\n🚀 " + "="*50)
    print("🚀 PDF THREAT HUNTER")
    print("🚀 " + "="*50)
    print(f"📄 Target: {os.path.basename(pdf_path)}")
    
    # Run with streaming
    final_result = None
    for chunk in app.stream({"pdf_path": pdf_path}):
        node_name = list(chunk.keys())[0]
        final_result = chunk[node_name]
    
    # Show summary
    if final_result:
        print(f"\n📊 SUMMARY:")
        print(f"🆔 Analysis ID: {final_result.get('analysis_id')}")
        if final_result.get('static_analysis_report'):
            print(f"📄 Report: {len(final_result['static_analysis_report'])} chars")
        print(f"💾 Files: pdf_analysis_report_{final_result.get('analysis_id', 'unknown')}.{{json,md}}")
    
    print("\n🎯 Done!") 