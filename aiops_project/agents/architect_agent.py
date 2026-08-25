import os
from dotenv import load_dotenv
from mistralai.client import Mistral

# Load API key
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# Connect to Mistral AI
client = Mistral(api_key=api_key)

def generate_patch(solution):
    """Takes Librarian's solution and generates actual code patch"""
    print("🔧 Architect Agent is generating code patch...")
    print("-" * 50)

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {
                "role": "system",
                "content": """You are an Architect Agent — an expert Python developer.
                Your job is to generate clean, working code patches to fix server problems.
                Rules:
                STRICT RULES:
               1. Generate ONLY Python code — no explanations outside the code
               2. Add comments inside the code explaining each fix
               3. The code must be complete and ready to run
               4. Start with: # ARCHITECT AGENT - AUTO GENERATED PATCH
               5. End with: # END OF PATCH
               6. ONLY use these standard libraries: flask, logging, os, time, collections
               7. DO NOT use celery, redis, rabbitmq, or any external message brokers
               8. DO NOT use psycopg2, SQLAlchemy or any database libraries
               9. Use simple Python fixes — deque, generators, basic async
              10. Always include app.run(host='0.0.0.0', debug=True, port=5000) at the end
              11. Always include all original routes from app.py
              12. Always include these exact routes that works:
                   - GET / → jsonify status ok
                   - GET+POST /api/checkout → jsonify order placed successfully
                   - GET+POST /api/database → jsonify data list
                   - GET+POST /api/memory → jsonify memory ok
                   - GET /api/status → jsonify server status
                   - POST /api/heal → jsonify healed message
              13. Fix ALL bugs found in diagnosis:
                   - Replace division by zero with safe division
                   - Replace undefined variables with actual values
                   - Replace infinite loops with bounded loops
              14. ALL routes must return HTTP 200 with valid JSON"""
            
            },
            {
                "role": "user",
                "content": f"""Based on this solution, generate a complete Python code patch:

                {solution}
                
                Generate a fixed version of the Flask app with all fixes applied."""
            }
        ]
    )

    return response.choices[0].message.content

def save_patch(patch_code):
    """Save the generated patch to a file"""
    # Create patches folder if it doesn't exist
    if not os.path.exists('patches'):
        os.makedirs('patches')

    # Save patch with a number
    patch_files = os.listdir('patches')
    patch_number = len(patch_files) + 1
    patch_path = f'patches/patch_{patch_number}.py'

    with open(patch_path, 'w') as f:
        f.write(patch_code)

    print(f"💾 Patch saved to: {patch_path}")
    return patch_path

def run_architect(solution):
    print("🚀 Starting Architect Agent...")
    print("=" * 50)

    # Generate the patch
    patch_code = generate_patch(solution)

    print("🔧 Generated Patch:")
    print("-" * 50)
    print(patch_code)
    print("=" * 50)

    # Save the patch
    patch_path = save_patch(patch_code)

    print(f"✅ Architect Agent complete!")
    print(f"📁 Patch saved at: {patch_path}")

    return patch_code, patch_path

if __name__ == '__main__':
    # Test with sample solution
    test_solution = """
    Fix memory leak in /memory route using deque with maxlen=1000
    Fix slow route using async
    Replace dev server warning
    """
    run_architect(test_solution)