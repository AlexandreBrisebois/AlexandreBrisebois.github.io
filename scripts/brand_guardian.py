import os
import google.generativeai as genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
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
    
    response = model.generate_content(prompt)
    
    with open("social_drafts.md", "w") as f:
        f.write("# 🛡️ Brand Guardian Report (Gemini)\n\n")
        f.write(response.text)

if __name__ == "__main__":
    main()
