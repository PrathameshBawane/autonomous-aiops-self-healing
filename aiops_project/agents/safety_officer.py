import os
import subprocess
import sys
from dotenv import load_dotenv
from mistralai.client import Mistral

# Load API key
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# Connect to Mistral AI
client = Mistral(api_key=api_key)

def clean_patch_code(patch_code):
    """Remove markdown code blocks if present"""
    lines = patch_code.split('\n')
    cleaned = []
    for line in lines:
        if line.strip().startswith('```'):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)

def validate_patch(patch_code):
    """Ask Mistral to review the patch for errors"""
    print("🔍 Safety Officer is reviewing the patch...")
    print("-" * 50)

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {
                "role": "system",
                "content": """You are a Safety Officer Agent — a senior code reviewer.
                Your job is to check if a code patch is safe to apply.
                Check for:
                1. Syntax errors
                2. Security issues
                3. Logic errors
                4. Missing imports
                Respond with either:
                VERDICT: PASS - if code is safe
                VERDICT: FAIL - if code has problems
                Then explain why in 2-3 lines."""
            },
            {
                "role": "user",
                "content": f"Review this patch and give your verdict:\n\n{patch_code}"
            }
        ]
    )
    return response.choices[0].message.content

def syntax_check(patch_code):
    """Actually test if the Python code has syntax errors"""
    print("🧪 Running syntax check...")
    
    # Clean the code first
    clean_code = clean_patch_code(patch_code)
    
    # Save temporarily
    temp_path = 'patches/temp_test.py'
    with open(temp_path, 'w') as f:
        f.write(clean_code)

    # Run Python syntax check
    result = subprocess.run(
        [sys.executable, '-m', 'py_compile', temp_path],
        capture_output=True,
        text=True
    )

    # Clean up temp file
    os.remove(temp_path)

    if result.returncode == 0:
        print("✅ Syntax check PASSED!")
        return True, "No syntax errors found"
    else:
        print("❌ Syntax check FAILED!")
        return False, result.stderr

def run_safety_officer(patch_code, patch_path):
    print("🚀 Starting Safety Officer Agent...")
    print("=" * 50)

    # Test 1: Syntax check
    syntax_ok, syntax_msg = syntax_check(patch_code)

    # Test 2: AI review
    ai_verdict = validate_patch(patch_code)
    print("\n🤖 AI Review:")
    print(ai_verdict)

    # Final verdict
    print("\n" + "=" * 50)
    if syntax_ok and "PASS" in ai_verdict:
        print("✅ SAFETY OFFICER VERDICT: PATCH APPROVED!")
        print(f"📁 Safe to apply: {patch_path}")
        return True
    else:
        print("❌ SAFETY OFFICER VERDICT: PATCH REJECTED!")
        print(f"Reason: {syntax_msg}")
        return False

if __name__ == '__main__':
    # Test with patch_1.py
    patch_path = 'patches/patch_1.py'
    with open(patch_path, 'r') as f:
        patch_code = f.read()
    run_safety_officer(patch_code, patch_path)