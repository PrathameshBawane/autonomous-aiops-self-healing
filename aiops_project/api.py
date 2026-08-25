from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import threading

app = Flask(__name__)
CORS(app)  # Allow React to talk to Flask

# Store pipeline status in memory
pipeline_status = {
    "status": "idle",
    "current_agent": "",
    "diagnosis": "",
    "solution": "",
    "patch_code": "",
    "patch_path": "",
    "verdict": False,
    "docker_result": False,
    "logs": "",
    "history": []
}

def run_pipeline_thread():
    """Run pipeline in background thread"""
    global pipeline_status

    try:
        from agents.sentry_agent import read_logs, analyze_logs
        from agents.librarian_agent import run_librarian
        from agents.architect_agent import run_architect
        from agents.safety_officer import run_safety_officer
        from agents.docker_sandbox import run_docker_test

        # Sentry
        pipeline_status["current_agent"] = "sentry"
        pipeline_status["status"] = "running"
        # chage the path file for reading the new logs file of any server
        logs = read_logs('logs/server.log') 
        diagnosis = analyze_logs(logs)
        pipeline_status["logs"] = logs
        pipeline_status["diagnosis"] = diagnosis

        # Librarian
        pipeline_status["current_agent"] = "librarian"
        solution = run_librarian(diagnosis)
        pipeline_status["solution"] = solution

        # Architect
        pipeline_status["current_agent"] = "architect"
        patch_code, patch_path = run_architect(solution)
        pipeline_status["patch_code"] = patch_code
        pipeline_status["patch_path"] = patch_path

        # Safety Officer
        pipeline_status["current_agent"] = "safety_officer"
        verdict = run_safety_officer(patch_code, patch_path)
        pipeline_status["verdict"] = verdict

        # Docker
        pipeline_status["current_agent"] = "docker"
        docker_result = run_docker_test(patch_path)
        pipeline_status["docker_result"] = docker_result

        # Wait for human approval
        pipeline_status["current_agent"] = "human_approval"
        pipeline_status["status"] = "awaiting_approval"

    except Exception as e:
        pipeline_status["status"] = "error"
        pipeline_status["current_agent"] = str(e)

def apply_patch_to_demo_server(patch_code):
    """Apply generated patch permanently to demo_server.py"""
    import re
    import shutil
    import subprocess

    demo_server_path = 'demo_server.py'
    backup_path = 'demo_server_backup.py'

    try:
        print("🔧 Applying patch to demo_server.py...")

        # Step 1 - Backup original
        shutil.copy(demo_server_path, backup_path)
        print(f"💾 Backup created: {backup_path}")

        # Step 2 - Clean patch code
        clean_code = patch_code
        clean_code = re.sub(r'```python\n?', '', clean_code)
        clean_code = re.sub(r'```\n?', '', clean_code)
        clean_code = clean_code.strip()

        # Step 3 - Check patch has valid Flask code
        if 'Flask' not in clean_code or 'app.run' not in clean_code:
            print("⚠️ Patch missing Flask code — keeping original")
            return False

        # Step 4 - Check patch has heal endpoint
        # Always keep the /api/heal route in patched server
        if '/api/heal' not in clean_code:
            print("⚠️ Adding heal endpoint to patch...")
            heal_route = """
@app.route('/api/heal', methods=['POST'])
def heal():
    \"\"\"AIOps calls this to heal the server\"\"\"
    print("✅ Server healed by AIOps!")
    return jsonify({"message": "Server healed!"}), 200
"""
            # Insert before app.run line
            clean_code = clean_code.replace(
                "if __name__ == '__main__':",
                heal_route + "\nif __name__ == '__main__':"
            )

        # Step 5 - Write patch to demo_server.py
        with open(demo_server_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(clean_code)
        
        # Step 6 - Restart demo server
        print("🔄 Restarting demo server...")
        subprocess.Popen(
            ['python', demo_server_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("✅ Demo server restarted with patch applied!")
        return True

    except Exception as e:
        print(f"❌ Patch apply failed: {e}")
       
        # Restore backup
        try:
            with open(demo_server_path, 'r', encoding='utf-8', errors='ignore') as f:
                original = f.read()
            with open(backup_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(original)
            print(f"💾 Backup created: {backup_path}")
        except Exception as e:
            print(f"⚠️ Backup failed: {e}")

# ─── API ROUTES ───

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(pipeline_status)

@app.route('/api/start', methods=['POST'])
def start_pipeline():
    global pipeline_status
    if pipeline_status["status"] == "running":
        return jsonify({"message": "Pipeline already running!"}), 400

    # Reset status
    pipeline_status["status"] = "running"
    pipeline_status["current_agent"] = "sentry"

    # Run in background
    thread = threading.Thread(target=run_pipeline_thread)
    thread.daemon = True
    thread.start()

    return jsonify({"message": "Pipeline started!"})

# @app.route('/api/approve', methods=['POST'])
# def approve_patch():
#     global pipeline_status
#     data = request.json
#     action = data.get("action", "reject")

#     if action == "approve":
#         # Heal the server via runtime endpoint
#         try:
#             import requests as req
#             heal = req.post(
#                 'http://localhost:5003/api/heal',
#                 timeout=5
#             )
#             print(f"✅ Server healed! Status: {heal.status_code}")
#         except Exception as e:
#             print(f"⚠️ Heal failed: {e}")

#         pipeline_status["status"] = "approved"
#         pipeline_status["history"].append({
#             "patch": pipeline_status["patch_path"],
#             "verdict": "approved",
#             "diagnosis": pipeline_status["diagnosis"][:100]
#         })
#     else:
#         pipeline_status["status"] = "rejected"

#     return jsonify({"message": f"Patch {action}d!"})

@app.route('/api/approve', methods=['POST'])
def approve_patch():
    global pipeline_status
    data = request.json
    action = data.get("action", "reject")

    if action == "approve":
        patch_code = pipeline_status["patch_code"]
        patch_path = pipeline_status["patch_path"]

        # Step 1 — Runtime heal immediately
        try:
            import requests as req
            req.post('http://localhost:5003/api/heal', timeout=3)
            print("✅ Runtime heal done!")
        except Exception as e:
            print(f"⚠️ Runtime heal: {e}")

        # Step 2 — Write patch permanently to demo_server.py
        try:
            import re
            import shutil

            # Clean patch code
            clean = patch_code
            clean = re.sub(r'```python\n?', '', clean)
            clean = re.sub(r'```\n?', '', clean)
            clean = clean.strip()

            # Only write if valid Flask code
            if 'Flask' in clean and 'app.run' in clean:
                # Backup first
                shutil.copy('demo_server.py', 'demo_server_backup.py')

                # Fix port to 5003
                clean = re.sub(
                    r'app\.run\(.*?\)',
                    "app.run(host='0.0.0.0', debug=True, port=5003)",
                    clean
                )

                # Add heal route if missing
                if '/api/heal' not in clean:
                    heal = """
@app.route('/api/heal', methods=['POST'])
def heal():
    print("Server healed!")
    return jsonify({"message": "Healed!"}), 200
"""
                    clean = clean.replace(
                        "if __name__ == '__main__':",
                        heal + "\nif __name__ == '__main__':"
                    )

                # Write to demo_server.py
                with open('demo_server.py', 'w',
                         encoding='utf-8', errors='ignore') as f:
                    f.write(clean)
                print("✅ Patch written to demo_server.py!")

                # Restart demo server
                import subprocess
                subprocess.Popen(
                    ['python', 'demo_server.py'],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                print("✅ Demo server restarted with patch!")
            else:
                print("⚠️ Patch missing Flask code — keeping original")

        except Exception as e:
            print(f"❌ Patch write error: {e}")
            try:
                shutil.copy('demo_server_backup.py', 'demo_server.py')
            except:
                pass

        pipeline_status["status"] = "approved"
        pipeline_status["history"].append({
            "patch": patch_path,
            "verdict": "approved",
            "diagnosis": pipeline_status["diagnosis"][:100]
        })

    else:
        pipeline_status["status"] = "rejected"

    return jsonify({"message": f"Patch {action}d!"})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    log_path = os.path.join('logs', 'server.log')
    with open(log_path, 'r') as f:
        logs = f.read()
    return jsonify({"logs": logs})

@app.route('/api/reset', methods=['POST'])
def reset_pipeline():
    global pipeline_status
    pipeline_status["status"] = "idle"
    pipeline_status["current_agent"] = ""
    pipeline_status["diagnosis"] = ""
    pipeline_status["solution"] = ""
    pipeline_status["patch_code"] = ""
    return jsonify({"message": "Pipeline reset!"})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
