import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

models_to_test = ["gemini-2.0-flash-001", "gemini-pro", "gemini-1.5-pro"]

for model_name in models_to_test:
    print(f"\nTesting {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"Match: {model_name} - Success -> {response.text.strip()}")
    except Exception as e:
        print(f"Error with {model_name}: {e}")
    time.sleep(1)
