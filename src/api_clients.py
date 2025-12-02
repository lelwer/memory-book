import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image 
import io

# (Top of file is unchanged)
# --- Load .env file ---
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
# --- API Key Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY environment variable not set.")
# (get_story_from_gemini function is unchanged)
def get_story_from_gemini(full_prompt):
    if not GEMINI_API_KEY:
        print("[Error] Cannot call Gemini: API key is missing.")
        return "This is placeholder story text. The GEMINI_API_KEY is not set."
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(full_prompt)
        clean_text = response.text
        clean_text = clean_text.replace("…", "...")
        clean_text = clean_text.replace("’", "'")
        clean_text = clean_text.replace("‘", "'")
        clean_text = clean_text.replace("“", '"')
        clean_text = clean_text.replace("”", '"')
        clean_text = clean_text.replace("—", "--")
        return clean_text
    except Exception as e:
        print(f"[Error] Failed to generate story: {e}")
        return "Placeholder story text. An API error occurred."


# --- START FIX (Problem #2) ---
def get_cover_image(theme):
    """
    Generates a single, beautiful pattern for the cover.
    """
    if not GEMINI_API_KEY:
        print("[Error] Cannot get cover image: API key is missing.")
        return None

    try:
        prompt = (
            f"Generate a beautiful, seamless, repeating pattern for a children's "
            f"storybook cover. The theme should be '{theme}'. "
            f"Style: playful, colorful, simple cartoon."
            f"CRITICAL: DO NOT include any text or words. "
            f"DO NOT draw malformed animals, extra limbs, or distorted features." # <-- NEW
        )
        
        image_model = genai.GenerativeModel('models/gemini-2.5-flash-image')
        response = image_model.generate_content(prompt)
        
        for part in response.parts:
            if part.inline_data:
                image_data = part.inline_data
                file_extension = f".{image_data.mime_type.split('/')[-1]}"
                output_filename = "cover_pattern" + file_extension
                
                print(f"... Saving cover pattern to {output_filename}")
                with open(output_filename, 'wb') as f:
                    f.write(image_data.data)
                return output_filename # Return the file path
                
    except Exception as e:
        print(f"[Error] Failed to generate cover image: {e}")
        return None
    return None
# --- END FIX ---


# (get_images_from_api function is unchanged, it's working well)
def get_images_from_api(story_text, character_description, other_characters, details):
    if not GEMINI_API_KEY:
        print("[Error] Cannot get images: API key is missing.")
        return []

    generated_image_paths = []
    story_pages = story_text.split('\n\n')
    
    if not story_pages:
        print("[Warning] Story text was empty, cannot generate images.")
        return []

    print(f"...Generating {len(story_pages)} images (one per page)...")

    try:
        style_guide = (
            f"STYLE: You are an illustrator for a single children's storybook. "
            f"You must use one CONSISTENT style (whimsical, colorful, cartoon). "
            f"MAIN CHARACTER (Maya): '{character_description}'. "
            f"OTHER CHARACTER (Mom): '{other_characters}'. "
            f"SETTING: {details}. Each scene prompt will describe a specific "
            f"room. The setting MUST match the prompt. Do NOT merge "
            f"scenes (e.g., no bathtubs in kitchens)."
        )
        negative_prompt = (
            f"CRITICAL: DO NOT include any text, words, or letters. "
            f"DO NOT draw malformed bodies, distorted faces, dead eyes, "
            f"zombie-like or uncanny valley expressions, disfigured features, "
            f"or missing limbs. All characters must be drawn "
            f"correctly, with happy, natural expressions."
        )
        
        image_model = genai.GenerativeModel('models/gemini-2.5-flash-image')
        chat = image_model.start_chat(
            history=[
                {'role': 'user', 'parts': [style_guide, negative_prompt]},
                {'role': 'model', 'parts': ["Okay, I understand. I will draw in one consistent style, keeping the characters and setting consistent. I will not draw text or malformed bodies."]}
            ]
        )
        
        for i, page_text in enumerate(story_pages):
            print(f"... Sending prompt for page {i+1}...")
            scene_prompt = f"SCENE: {page_text}"
            response = chat.send_message(scene_prompt)
            
            image_found = False
            for part in response.parts:
                if part.inline_data:
                    image_data = part.inline_data
                    file_extension = f".{image_data.mime_type.split('/')[-1]}"
                    output_filename = f"temp_image_{i}{file_extension}"
                    
                    print(f"... Saving image to {output_filename}")
                    with open(output_filename, 'wb') as f:
                        f.write(image_data.data)
                    
                    generated_image_paths.append(output_filename)
                    image_found = True
                    break
            
            if not image_found:
                 print(f"[Warning] Image API call worked for page {i+1}, but no image data found.")
                 
    except Exception as e:
        print(f"[Error] Failed during image generation chat: {e}")
        pass

    return generated_image_paths