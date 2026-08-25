from agents.sentry_agent import read_logs, analyze_logs
from agents.librarian_agent import run_librarian
from agents.architect_agent import run_architect
from agents.safety_officer import run_safety_officer

def run_full_pipeline():
    print("🚀 AIOps Self-Healing Pipeline Starting...")
    print("=" * 50)

    # ─── AGENT 1: SENTRY ───
    print("\n📡 AGENT 1 - SENTRY (Monitoring)")
    print("-" * 50)
    logs = read_logs()
    print("✅ Logs loaded!")
    diagnosis = analyze_logs(logs)
    print("\n🤖 Sentry Diagnosis:")
    print(diagnosis)

    # ─── AGENT 2: LIBRARIAN ───
    print("\n📚 AGENT 2 - LIBRARIAN (Research)")
    print("-" * 50)
    solution = run_librarian(diagnosis)

    # ─── AGENT 3: ARCHITECT ───
    print("\n🔧 AGENT 3 - ARCHITECT (Code Fix)")
    print("-" * 50)
    patch_code, patch_path = run_architect(solution)

    # ─── AGENT 4: SAFETY OFFICER ───
    print("\n🛡️  AGENT 4 - SAFETY OFFICER (Testing)")
    print("-" * 50)
    is_approved = run_safety_officer(patch_code, patch_path)

    # ─── FINAL RESULT ───
    print("\n" + "=" * 50)
    print("🏁 PIPELINE COMPLETE - FINAL REPORT")
    print("=" * 50)
    print("  ✅ Sentry Agent     → problems detected")
    print("  ✅ Librarian Agent  → solutions found")
    print("  ✅ Architect Agent  → patch generated")

    if is_approved:
        print("  ✅ Safety Officer  → patch APPROVED!")
        print("\n🎉 System is SELF-HEALED successfully!")
    else:
        print("  ❌ Safety Officer  → patch REJECTED!")
        print("\n⚠️  Manual intervention required!")

    print("=" * 50)

if __name__ == '__main__':
    run_full_pipeline()