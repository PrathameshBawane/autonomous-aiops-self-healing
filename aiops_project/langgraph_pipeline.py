import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from agents.sentry_agent import read_logs, analyze_logs
from agents.librarian_agent import run_librarian
from agents.architect_agent import run_architect
from agents.safety_officer import run_safety_officer

load_dotenv()

# ─── SHARED STATE ───
# This is the shared notebook all agents read and write to
class AgentState(TypedDict):
    logs: str           # raw server logs
    diagnosis: str      # sentry's findings
    solution: str       # librarian's solution
    patch_code: str     # architect's code patch
    patch_path: str     # where patch is saved
    verdict: bool       # safety officer's decision
    retry_count: int    # how many times we retried
    status: str         # current pipeline status

# ─── AGENT 1: SENTRY ───
def sentry_node(state: AgentState) -> AgentState:
    print("\n📡 SENTRY AGENT running...")
    print("-" * 50)
    logs = read_logs()
    diagnosis = analyze_logs(logs)
    print(f"✅ Sentry complete!")
    return {
        **state,
        "logs": logs,
        "diagnosis": diagnosis,
        "status": "sentry_done"
    }

# ─── AGENT 2: LIBRARIAN ───
def librarian_node(state: AgentState) -> AgentState:
    print("\n📚 LIBRARIAN AGENT running...")
    print("-" * 50)
    solution = run_librarian(state["diagnosis"])
    print(f"✅ Librarian complete!")
    return {
        **state,
        "solution": solution,
        "status": "librarian_done"
    }

# ─── AGENT 3: ARCHITECT ───
def architect_node(state: AgentState) -> AgentState:
    print("\n🔧 ARCHITECT AGENT running...")
    print("-" * 50)
    patch_code, patch_path = run_architect(state["solution"])
    print(f"✅ Architect complete!")
    return {
        **state,
        "patch_code": patch_code,
        "patch_path": patch_path,
        "status": "architect_done"
    }

# ─── AGENT 4: SAFETY OFFICER ───
def safety_officer_node(state: AgentState) -> AgentState:
    print("\n🛡️  SAFETY OFFICER running...")
    print("-" * 50)
    verdict = run_safety_officer(
        state["patch_code"],
        state["patch_path"]
    )
    return {
        **state,
        "verdict": verdict,
        "status": "safety_done"
    }

# ─── HUMAN APPROVAL ───
def human_approval_node(state: AgentState) -> AgentState:
    print("\n👤 HUMAN APPROVAL REQUIRED")
    print("=" * 50)
    print(f"Patch location: {state['patch_path']}")
    print("\nOptions:")
    print("  1 → Apply Fix")
    print("  2 → Reject")
    choice = input("\nYour decision (1 or 2): ").strip()

    if choice == "1":
        print("✅ Human approved the fix!")
        return {**state, "status": "approved"}
    else:
        print("❌ Human rejected the fix!")
        return {**state, "status": "rejected"}

# ─── ROUTING LOGIC ───
def should_retry(state: AgentState) -> str:
    """If safety officer rejects — retry up to 2 times"""
    if state["verdict"]:
        return "human_approval"
    elif state["retry_count"] < 2:
        print(f"\n⚠️  Patch failed! Retrying... (attempt {state['retry_count'] + 1})")
        state["retry_count"] += 1
        return "architect"
    else:
        print("\n❌ Max retries reached!")
        return END

def after_human(state: AgentState) -> str:
    """After human decision"""
    if state["status"] == "approved":
        return "end"
    else:
        return "end"

# ─── BUILD THE GRAPH ───
def build_graph():
    graph = StateGraph(AgentState)

    # Add all agent nodes
    graph.add_node("sentry", sentry_node)
    graph.add_node("librarian", librarian_node)
    graph.add_node("architect", architect_node)
    graph.add_node("safety_officer", safety_officer_node)
    graph.add_node("human_approval", human_approval_node)

    # Define the flow
    graph.set_entry_point("sentry")
    graph.add_edge("sentry", "librarian")
    graph.add_edge("librarian", "architect")

    # Safety officer decides: retry or human approval
    graph.add_conditional_edges(
        "safety_officer",
        should_retry,
        {
            "human_approval": "human_approval",
            "architect": "architect",
            END: END
        }
    )
    graph.add_edge("architect", "safety_officer")
    graph.add_edge("human_approval", END)

    return graph.compile()

# ─── RUN ───
def run_langgraph_pipeline():
    print("🚀 LangGraph AIOps Pipeline Starting...")
    print("=" * 50)

    app = build_graph()

    # Initial state
    initial_state = AgentState(
        logs="",
        diagnosis="",
        solution="",
        patch_code="",
        patch_path="",
        verdict=False,
        retry_count=0,
        status="starting"
    )

    # Run the graph
    final_state = app.invoke(initial_state)

    # Final report
    print("\n" + "=" * 50)
    print("🏁 LANGGRAPH PIPELINE COMPLETE")
    print("=" * 50)
    print(f"  Status     : {final_state['status']}")
    print(f"  Patch file : {final_state['patch_path']}")
    print(f"  Retries    : {final_state['retry_count']}")
    print("=" * 50)

if __name__ == '__main__':
    run_langgraph_pipeline()