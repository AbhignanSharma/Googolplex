import os
import sys
import google.generativeai as genai

def main():
    print("Starting AI PR Reviewer...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    try:
        with open("pr_details.txt", "r") as f:
            pr_content = f.read()
    except FileNotFoundError:
        print("Error: pr_details.txt not found.")
        sys.exit(1)

    print("Authenticating with Gemini...")
    genai.configure(api_key=api_key)
    
    # robust model selection
    model_name = os.environ.get("GEMINI_MODEL", "gemini-pro")
    model = genai.GenerativeModel(model_name)

    prompt = f"""
    You are an expert code reviewer and technical writer. 
    Please review the following Pull Request details. 
    Provide a improved title (if applicable), a summary of the changes, 
    and identify any potential risks or missing information based on the description.

    PR Details:
    {pr_content}
    """

    print("Generating review...")
    try:
        response = model.generate_content(prompt)
        review_text = response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        sys.exit(1)

    print("Review generated. Saving to ai_response.txt...")
    with open("ai_response.txt", "w") as f:
        f.write(review_text)

if __name__ == "__main__":
    main()
