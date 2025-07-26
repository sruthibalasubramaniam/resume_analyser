import google.generativeai as genai
import os

print("--- Starting Model Check ---")

# --- Configure the API Key ---
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set! Please set it and try again.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"\n❌ Error during configuration: {e}")
    exit()

print("✅ API Key configured successfully.")
print("🤖 Fetching the list of available models from the API...")
print("-" * 20)

# --- List the Models ---
try:
    found_models = False
    for m in genai.list_models():
        # We only care about models that support the 'generateContent' method
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model found: {m.name}")
            found_models = True
    
    if not found_models:
        print("\n❌ No models supporting 'generateContent' were found for your API key or project.")

except Exception as e:
    print(f"\n❌ An error occurred while trying to list models: {e}")

print("-" * 20)
print("--- Model Check Complete ---")