import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    print(f"--- TESTING GEMINI CONNECTION ---")
    print(f"Model: {model_name}")
    print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        print("Sending test prompt: 'Hello, are you there?'")
        response = model.generate_content("Hello, are you there?")
        print(f"SUCCESS! Response: {response.text}")
    except Exception as e:
        print(f"FAILED! Error: {e}")

if __name__ == "__main__":
    test_gemini()
