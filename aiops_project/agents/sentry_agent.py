import os
from dotenv import load_dotenv
from mistralai.client import Mistral

# Load API key from .env file
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# Connect to Mistral AI
client = Mistral(api_key=api_key)

def read_logs(log_path=None):
    """Read the server log file"""
    if log_path is None:
        log_path = os.path.join('logs', 'server.log')
    with open(log_path, 'r') as f:
        logs = f.read()
    return logs

def analyze_logs(logs):
    """Send logs to Mistral AI for analysis"""
    print("🔍 Sentry Agent is analyzing logs...")
    print("-" * 50)

    # Send logs to Mistral AI
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {
                "role": "system",
                "content": """You are a server monitoring expert called Sentry Agent.
                Your job is to analyze server logs and detect problems.
                When you find problems, clearly state:
                1. What the problem is
                2. How serious it is (INFO, WARNING, CRITICAL)
                3. What might have caused it
                Keep your answer short and clear."""
            },
            {
                "role": "user",
                "content": f"Please analyze these server logs and tell me if there are any problems:\n\n{logs}"
            }
        ]
    )

    return response.choices[0].message.content

def run_sentry():
    print("🚀 Starting Sentry Agent...")
    print("=" * 50)

    # Step 1: Read logs
    logs = read_logs()
    print("📋 Logs loaded successfully!")
    print("-" * 50)

    # Step 2: Analyze with AI
    diagnosis = analyze_logs(logs)

    # Step 3: Print diagnosis
    print("🤖 Sentry Agent Diagnosis:")
    print("-" * 50)
    print(diagnosis)
    print("=" * 50)

if __name__ == '__main__':
    run_sentry()