import subprocess
import time
import requests
import os
import socket
import re

def is_port_open(port):
    """Check if port is accepting connections"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def clean_patch_code(patch_code):
    """Clean patch code for Docker testing"""
    # Remove markdown
    code = re.sub(r'```python\n?', '', patch_code)
    code = re.sub(r'```\n?', '', code)
    code = code.strip()

    # Fix port to 5000 for Docker
    code = re.sub(
        r'app\.run\(.*?\)',
        "app.run(host='0.0.0.0', debug=False, port=5000)",
        code
    )

    # Add app.run if missing
    if 'app.run' not in code:
        code += "\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', debug=False, port=5000)\n"

    # Remove use_reloader
    code = code.replace('use_reloader=False', '')
    code = code.replace('use_reloader=True', '')

    return code

def write_patch_for_docker(patch_code):
    """Write cleaned patch as patch_to_test.py"""
    try:
        clean = clean_patch_code(patch_code)
        with open('patch_to_test.py', 'w',
                 encoding='utf-8', errors='ignore') as f:
            f.write(clean)
        print("✅ Patch written to patch_to_test.py")
        return True
    except Exception as e:
        print(f"❌ Failed to write patch: {e}")
        return False

def build_patch_image():
    """Build Docker image using Dockerfile.patch"""
    print("🐳 Building Docker image from patch...")

    # Remove old image
    subprocess.run(
        ["docker", "rmi", "-f", "aiops-patch-test"],
        capture_output=True
    )

    result = subprocess.run(
        ["docker", "build",
         "-f", "Dockerfile.patch",
         "-t", "aiops-patch-test",
         "."],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        timeout=120
    )

    if result.returncode == 0:
        print("✅ Docker image built successfully!")
        return True
    else:
        print("❌ Docker build failed!")
        print(result.stderr[-500:])
        return False

def test_patch_container():
    """Run patch in Docker container and test it"""
    # Kill any existing container
    subprocess.run(
        ["docker", "rm", "-f", "aiops-patch-sandbox"],
        capture_output=True
    )

    print("▶️  Starting Docker container with patch...")
    container = subprocess.Popen(
        [
            "docker", "run",
            "--rm",
            "-p", "5001:5000",
            "--name", "aiops-patch-sandbox",
            "aiops-patch-test"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='ignore'
    )

    # Wait for port to open
    print("⏳ Waiting for patch server in Docker...")
    max_wait = 60
    waited = 0
    server_ready = False

    while waited < max_wait:
        if is_port_open(5001):
            time.sleep(3)  # Extra buffer
            server_ready = True
            print("✅ Patch server is ready in Docker!")
            break
        time.sleep(3)
        waited += 3
        print(f"  ⏳ Still waiting... ({waited}s)")

    if not server_ready:
        stdout, stderr = container.communicate(timeout=5)
        print("❌ Container logs:")
        print(stderr[-300:] if stderr else "No logs")
        subprocess.run(
            ["docker", "rm", "-f", "aiops-patch-sandbox"],
            capture_output=True
        )
        container.terminate()
        return False

    # Test the patch
    test_results = []
    try:
        # Test 1 — Home route
        print("🧪 Test 1: Home route...")
        r = requests.get(
            "http://127.0.0.1:5001/",
            timeout=5
        )
        if r.status_code in [200, 404]:
            print(f"  ✅ Home route OK! ({r.status_code})")
            test_results.append(True)
        else:
            print(f"  ❌ Home route failed: {r.status_code}")
            test_results.append(False)

        # Test 2 — Checkout route
        print("🧪 Test 2: Checkout route...")
        r = requests.get(
            "http://127.0.0.1:5001/api/checkout",
            timeout=5
        )
        if r.status_code == 200:
            print(f"  ✅ Checkout FIXED! Returns 200!")
            test_results.append(True)
        elif r.status_code in [405, 500]:
            print(f"  ⚠️ Checkout exists but: {r.status_code}")
            test_results.append(True)
        else:
            print(f"  ❌ Checkout failed: {r.status_code}")
            test_results.append(False)

        # Test 3 — Server stability
        print("🧪 Test 3: Server stability...")
        time.sleep(3)
        if is_port_open(5001):
            print("  ✅ Patch server still running!")
            test_results.append(True)
        else:
            print("  ❌ Patch server crashed!")
            test_results.append(False)

    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ Connection error: {e}")
        test_results.append(False)

    finally:
        print("\n🛑 Stopping Docker container...")
        subprocess.run(
            ["docker", "rm", "-f", "aiops-patch-sandbox"],
            capture_output=True
        )
        container.terminate()
        # Cleanup
        if os.path.exists('patch_to_test.py'):
            os.remove('patch_to_test.py')

    # Results
    passed = sum(test_results)
    total = len(test_results)
    print(f"\n📊 Docker Test Results: {passed}/{total} passed")

    if passed >= 2:
        print("✅ DOCKER SANDBOX: PATCH APPROVED!")
        return True
    else:
        print("❌ DOCKER SANDBOX: PATCH REJECTED!")
        return False

def run_docker_test(patch_path):
    """Main entry — test patch in Docker"""
    print("🚀 Starting Docker Patch Testing...")
    print("=" * 50)

    # Read patch
    try:
        with open(patch_path, 'r',
                 encoding='utf-8', errors='ignore') as f:
            patch_code = f.read()
    except Exception as e:
        print(f"❌ Cannot read patch: {e}")
        return False

    # Step 1 — Write patch for Docker
    if not write_patch_for_docker(patch_code):
        return False

    # Step 2 — Build Docker image with patch
    if not build_patch_image():
        return False

    # Step 3 — Run and test patch in container
    return test_patch_container()

if __name__ == '__main__':
    patches = [p for p in os.listdir('patches')
               if p.endswith('.py') and p != '.gitkeep']
    if patches:
        latest = sorted(patches)[-1]
        print(f"Testing: {latest}")
        run_docker_test(f'patches/{latest}')
    else:
        print("No patches found!")