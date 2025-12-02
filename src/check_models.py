import os
import google.generativeai as genai
from dotenv import load_dotenv

def list_my_models():
    """
    Connects to the API and prints a list of all models
    your API key has access to.
    """
    print("--- Checking Available Models ---")
    
    # 1. Load the .env file
    # Go one directory up (from 'src' to 'Final Project') to find .env
    print("Loading .env file...")
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    
    # 2. Get the API key
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("\n[FAILURE] ❌: 'GEMINI_API_KEY' not found in .env file.")
        print(f"Checking in: {dotenv_path}")
        print("Please check your .env file and try again.")
        return
        
    print("API Key found! Configuring...")

    # 3. Configure and call the API
    try:
        genai.configure(api_key=api_key)
        
        print("\n[SUCCESS] ✅: Your key has access to these models:\n")
        
        # Call the ListModels method
        for m in genai.list_models():
            # We only care about models that can 'generateContent'
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
        print("\n---------------------------------")
        print("Please use one of the model names listed above in your code.")

    except Exception as e:
        print(f"\n[FAILURE] ❌: An error occurred during the API call.")
        print("---------------------------------")
        print(f"Error Details: {e}")
        print("---------------------------------")
        print("If this list is empty, it may be a billing or API setup issue.")

if __name__ == "__main__":
    list_my_models()