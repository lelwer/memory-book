import sys
import os
from dotenv import load_dotenv

# --- 1. PRE-FLIGHT CHECK ---
# Force load .env from the project root directory immediately.
# This ensures the key is available before we import other modules.
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

# Check the key immediately. If missing, fail fast with a clear message.
if not os.environ.get("GEMINI_API_KEY"):
    print("\n" + "="*50)
    print("❌ CRITICAL ERROR: API Key Missing")
    print("="*50)
    print(f"The program could not find 'GEMINI_API_KEY'.")
    print(f"It looked for the .env file here: {env_path}")
    print("\nPlease ensure you have created the .env file in the PROJECT ROOT.")
    print("The file content should look like: GEMINI_API_KEY=AIzaSy...")
    print("="*50 + "\n")
    sys.exit(1) # STOP THE PROGRAM HERE

# --- 2. MODULE IMPORTS ---
# We import these AFTER checking the key, so they initialize correctly.
from .api_clients import get_story_from_gemini, get_images_from_api, get_cover_image
from .book_assembler import create_pdf

def get_user_input():
    """Prompt the user for story inputs instead of returning hard-coded test data.

    Press Enter to accept the suggested default for any prompt.
    """
    print("--- 📚 Memory-to-Storybook Generator ---")
    print("Please provide the following details. Press Enter to accept the default shown in brackets.")

    def ask(prompt, default):
        try:
            resp = input(f"{prompt} [{default}]: ").strip()
        except EOFError:
            resp = ""
        return resp if resp else default

    memory = input("Enter the memory (briefly describe the event) [press Enter for default]: ").strip()
    if not memory:
        memory = (
            "I had my daughter ask as I was going to the bathroom when she was three: "
            "what do you know about armadillos?"
        )

    protagonist = ask("Protagonist name", "Maya")
    character_desc = ask("Protagonist description", "a 3-year-old girl with brown curly hair and big brown eyes")
    tone = ask("Tone (e.g., Funny, Serious, Tender)", "Funny")
    details = ask("Additional details / setting", "The setting is our family home. The story scenes take place in a hallway and a bathroom.")
    style = ask("Style (e.g., Rhyming, Narrative)", "Rhyming")
    complexity = ask("Complexity (Short/Standard/Advanced)", "Standard")
    title = ask("Story title", 'Silly Maya "Muffin" Elwer')
    end_message = ask("End message to include", "Merry Christmas! Love, Mom!")
    other_characters = ask("Other characters (brief)", "The narrator, 'mom', is a woman with blonde hair.")
    cover_theme = ask("Cover theme", "armadillos and flowers")
    theme_color = ask("Theme color", "light blue")

    return {
        "memory": memory,
        "protagonist": protagonist,
        "character_desc": character_desc,
        "tone": tone,
        "details": details,
        "style": style,
        "complexity": complexity,
        "title": title,
        "end_message": end_message,
        "other_characters": other_characters,
        "cover_theme": cover_theme,
        "theme_color": theme_color
    }


def main():
    """
    Main function to run the storybook generation pipeline.
    """
    
    # 1. Get user input
    story_inputs = get_user_input()
    protagonist = story_inputs['protagonist']
    
    print(f"\nThanks! Generating a '{story_inputs['tone']}' story for {protagonist}...")

    # 2. Craft the master prompt
    print("Step 1/4: Crafting a unique story prompt...")
    
    full_prompt = (
        f"Write a 5-page story about a memory. "
        f"CRITICAL: The story MUST be written from the **mom's point of view**. "
        f"The narrator (the 'I' in the story) is the mom. "
        f"THE MEMORY: {story_inputs['memory']}. "
        f"CHARACTERS: The mom (narrator) and her daughter, {protagonist}. "
        f"DETAILS: {story_inputs['details']}. "
        f"The tone must be {story_inputs['tone']}. "
        f"The style must be: {story_inputs['style']}. "
        f"Each of the 5 pages MUST have a maximum of 4 rhyming lines. "
        f"The rhymes MUST be strong and clear (e.g., 'day'/'play', not 'mom'/'jam'). "
        f"Format the output so that each page is separated by a double newline ('\n\n')."
    )
    
    try:
        print("Step 2/4: Calling Gemini for the story...")
        story_text = get_story_from_gemini(full_prompt)
        print("... Story text received!")
    except Exception as e:
        print(f"\n[Fatal Error] Failed to get story from API: {e}")
        sys.exit(1)

    # 3a. Call the Cover Image API
    try:
        print("Step 3/5: Calling API for cover image...")
        cover_image_path = get_cover_image(story_inputs['cover_theme'])
        if cover_image_path:
            print(f"... Cover image received!")
        else:
            print("... Could not generate cover image.")
    except Exception as e:
        print(f"\n[Fatal Error] Failed to get cover image from API: {e}")
        sys.exit(1)
        
    # 3b. Call the Story Image API
    try:
        print(f"Step 4/5: Calling API for {story_inputs['protagonist']}'s story images...")
        image_list = get_images_from_api(
            story_text, 
            story_inputs['character_desc'],
            story_inputs['other_characters'],
            story_inputs['details']
        )
        print(f"... {len(image_list)} images received!")
    except Exception as e:
        print(f"\n[Fatal Error] Failed to get story images from API: {e}")
        sys.exit(1)
            
    # 4. Assemble the final PDF
    print("Step 5/5: Assembling the final PDF...")
    output_filename = f"{protagonist.lower().replace(' ', '_')}_storybook.pdf"
    
    success = create_pdf(
        title=story_inputs['title'],
        story_text=story_text,
        image_list=image_list,
        end_message=story_inputs['end_message'],
        cover_image_path=cover_image_path,
        theme_color=story_inputs['theme_color'],
        output_filename=output_filename
    )
    
    if success:
        print(f"\n✅ Success! Your storybook has been saved as {output_filename}")
    else:
        print("\n[Error] Failed to create the final PDF.")


if __name__ == "__main__":
    main()