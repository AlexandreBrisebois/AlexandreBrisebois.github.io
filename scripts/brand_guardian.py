import os
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found")
        return

    client = genai.Client(api_key=api_key)
    
    # Debug: List available models
    print("Listing available models...")
    try:
        for m in client.models.list():
            print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    branding_rules = open("branding/system.md", "r").read()
    
    blog_dir = "src/content/blog"
    files = [os.path.join(blog_dir, f) for f in os.listdir(blog_dir) if f.endswith(".md")]
    latest_file = max(files, key=os.path.getmtime)
    
    content = open(latest_file, "r").read()
    
    prompt = f"""
    You are the 'Brand Guardian' for srvrlss.dev. 
    Using the following branding rules:
    {branding_rules}
    
    Analyze and generate social drafts for this blog post:
    {content}
    
    Output a markdown response with:
    1. A branding audit (Editor rules).
    2. A LinkedIn draft (Strategist PDL framework).
    3. An X (Twitter) draft.
    4. Two prompts for nanobananav2 (one for the blog hero, one for social).
    """
    
    # Attempt with 1.5 Pro, fallback to 2.0 Flash or 1.5 Flash
    selected_model = "gemini-1.5-pro"
    
    print(f"Using model: {selected_model}")
    try:
        response = client.models.generate_content(
            model=selected_model,
            contents=prompt
        )
    except Exception as e:
        print(f"Error with {selected_model}: {e}")
        selected_model = "gemini-1.5-flash"
        print(f"Falling back to: {selected_model}")
        response = client.models.generate_content(
            model=selected_model,
            contents=prompt
        )
    
    with open("social_drafts.md", "w") as f:
        f.write(f"# 🛡️ Brand Guardian Report ({selected_model})\n\n")
        f.write(response.text)

if __name__ == "__main__":
    main()
