import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini_connection():
    """
    Tests the API key and connection for BOTH text and image generation.
    This version correctly loops through all response 'parts' to find
    the image data in the 'inline_data' attribute.
    """
    print("--- Starting Full API Connection Test ---")
    
    # 1. Load the .env file
    print("Loading .env file...")
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    
    # 2. Get the API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n[FAILURE] ❌: 'GEMINI_API_KEY' not found in .env file.")
        return
        
    print("API Key found! Configuring...")
    genai.configure(api_key=api_key)

    # 3. --- TEST TEXT GENERATION ---
    try:
        print("\n--- Testing Text Generation ---")
        text_model = genai.GenerativeModel('models/gemini-2.5-flash')
        print("Sending text prompt to 'models/gemini-2.5-flash'...")
        response = text_model.generate_content("Explain how AI works in a few words")
        print("\n[SUCCESS] ✅: Text generation worked!")
        print("Gemini's Response:", response.text)
        
    except Exception as e:
        print(f"\n[FAILURE] ❌: Text generation failed.")
        print(f"Error Details: {e}")

    # 4. --- TEST IMAGE GENERATION (AND SAVE FILE) ---
    try:
        print("\n--- Testing Image Generation ---")
        image_model = genai.GenerativeModel('models/gemini-2.5-flash-image')
        print("Sending image prompt to 'models/gemini-2.5-flash-image'...")
        response = image_model.generate_content(
            "A simple, cute, storybook-style drawing of a cartoon armadillo"
        )
        
        # --- THIS IS THE CORRECT METHOD ---
        print("API call successful. Searching response parts for image data...")
        
        image_found = False
        # Loop through all parts of the response
        for part in response.parts:
            # Check if the 'inline_data' attribute exists and has data
            if part.inline_data:
                image_data = part.inline_data
                
                # Determine the file extension (e.g., 'image/png' -> '.png')
                file_extension = f".{image_data.mime_type.split('/')[-1]}"
                output_filename = "test_image" + file_extension
                
                print(f"Image data found (MIME type: {image_data.mime_type}).")
                
                # Save the raw bytes (image_data.data) to a file
                print(f"Saving image to: {output_filename}")
                with open(output_filename, 'wb') as f:
                    f.write(image_data.data)
                
                print(f"\n[SUCCESS] ✅: Image generation worked!")
                print(f"Please check your 'src' folder for the new file: {output_filename}")
                image_found = True
                break # Stop looping once we find the image
        
        if not image_found:
             print("\n[FAILURE] ❌: API call worked, but no 'inline_data' found in response.")

    except Exception as e:
        print(f"\n[FAILURE] ❌: Image generation failed.")
        print(f"Error Details: {e}")

if __name__ == "__main__":
    test_gemini_connection()