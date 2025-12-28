"""List available Gemini models and find the best one to use."""
from __future__ import annotations

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from google import genai


def list_available_models():
    """List all available Gemini models for the API key."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    print("\n" + "="*60)
    print("Available Gemini Models")
    print("="*60 + "\n")
    
    try:
        client = genai.Client(api_key=api_key)
        models = client.models.list()
        
        all_models = []
        
        for m in models:
            name = getattr(m, "name", None) or (m.get("name") if isinstance(m, dict) else None)
            if not name:
                continue
            
            display_name = getattr(m, "display_name", None) or ""
            supported_methods = getattr(m, "supported_generation_methods", None) or []
            
            model_info = {
                "name": str(name),
                "display_name": str(display_name) if display_name else "",
                "methods": supported_methods if isinstance(supported_methods, list) else []
            }
            
            all_models.append(model_info)
        
        print("📋 All Available Models:")
        print("-" * 60)
        
        vision_capable = []
        
        for model in all_models:
            print(f"\n• {model['name']}")
            if model['display_name']:
                print(f"  Display: {model['display_name']}")
            if model['methods']:
                print(f"  Methods: {', '.join(model['methods'])}")
                if 'generateContent' in model['methods']:
                    vision_capable.append(model['name'])
        
        print("\n" + "="*60)
        print(f"Total models found: {len(all_models)}")
        print("="*60 + "\n")
        
        # Suggest models to use
        if vision_capable:
            print("✅ Models supporting generateContent (vision):")
            for model_name in vision_capable:
                print(f"   {model_name}")
            print(f"\n💡 Recommended: Use '{vision_capable[0]}'\n")
        else:
            print("⚠️  No vision-capable models found\n")
            
    except Exception as e:
        print(f"❌ Error listing models: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    list_available_models()