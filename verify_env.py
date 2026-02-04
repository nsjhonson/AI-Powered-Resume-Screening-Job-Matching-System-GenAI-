import os
import sys
import importlib.util
from dotenv import load_dotenv

def check_import(module_name):
    if importlib.util.find_spec(module_name) is None:
        print(f"❌ Missing dependency: {module_name}")
        return False
    print(f"✅ Found dependency: {module_name}")
    return True

def check_env():
    print("\n--- Environment Check ---")
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        masked = api_key[:4] + "*" * (len(api_key)-8) + api_key[-4:]
        print(f"✅ API Key found: {masked}")
    else:
        print("❌ No API Key found in .env (OPENAI_API_KEY or GOOGLE_API_KEY)")
        print("   -> The AI features will NOT work without this.")

def main():
    print("Checking Python Environment...\n")
    
    dependencies = [
        "fastapi", "uvicorn", "streamlit", "requests", 
        "langchain", "faiss", "pypdf", "sqlalchemy"
    ]
    
    all_good = True
    for dep in dependencies:
        if not check_import(dep):
            all_good = False
            
    check_env()
    
    if all_good:
        print("\n✅ Verification Complete! Your environment looks ready.")
    else:
        print("\n⚠️ Issues found. Please install missing packages or fix .env.")

if __name__ == "__main__":
    main()
