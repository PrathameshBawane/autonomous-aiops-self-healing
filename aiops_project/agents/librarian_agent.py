import os
from dotenv import load_dotenv
from mistralai.client import Mistral

# Load API key
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# Connect to Mistral AI
client = Mistral(api_key=api_key)

def find_solution(diagnosis):
    """Takes Sentry's diagnosis and finds the best solution"""
    print("📚 Librarian Agent is searching for solutions...")
    print("-" * 50)

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {
                "role": "system",
                "content": """You are a Librarian Agent — an expert at finding solutions 
                to server problems. 
                When given a diagnosis, you must provide:
                1. Exact solution for each problem
                2. The specific Python/Flask code fix
                3. Priority order (fix most critical first)
                Be very specific — give actual code examples."""
            },
            {
                "role": "user",
                "content": f"""Based on this diagnosis from our Sentry Agent, 
                find the best solutions with code fixes:
                
                {diagnosis}"""
            }
        ]
    )

    return response.choices[0].message.content

def run_librarian(diagnosis):
    print("🚀 Starting Librarian Agent...")
    print("=" * 50)

    # Find solutions
    solution = find_solution(diagnosis)

    print("📚 Librarian Agent Solutions:")
    print("-" * 50)
    print(solution)
    print("=" * 50)

    return solution

if __name__ == '__main__':
    # Test with a sample diagnosis
    test_diagnosis = """
    Problems detected:
    1. CRITICAL - Memory usage too high on /memory route
    2. WARNING - Slow response detected on /slow route
    3. WARNING - Development server running in production
    """
    run_librarian(test_diagnosis)