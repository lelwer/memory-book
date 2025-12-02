# 📚 Memory-to-Storybook Generator

A command-line tool that transforms a cherished personal memory into a custom, beautifully illustrated storybook PDF using Google's Gemini AI.

This project takes a simple, real-life moment—like a child's funny question—and uses AI to write a unique story, generate consistent illustrations for each page, and assemble it all into a single, print-ready PDF file.

## Project Vision: From CLI to Keepsake

This command-line application serves as the powerful backbone and proof-of-concept for a much larger vision: a full web platform where any user can create and order a physical storybook.

The ultimate goal is to build a user-friendly website where a person can:

- Enter their memory and story details into a simple, beautiful interface
- Get an instant preview of their unique, AI-generated storybook right in the browser
- Order a physical copy to be professionally printed, bound, and shipped to their doorstep, creating a timeless family keepsake

This CLI tool is the foundational "engine" that proves the core logic—turning a prompt into a complete, illustrated book—is possible.

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Setting Up Your Gemini API Key](#setting-up-your-gemini-api-key)
- [Usage](#usage)
- [Understanding the Inputs](#understanding-the-inputs)
- [Tips for Best Results](#tips-for-best-results)
- [Example Output](#example-output)
- [Testing](#testing)
- [AI-Assisted Development](#ai-assisted-development)
- [License](#license)

## Features

- **AI-Powered Storytelling**: Uses `gemini-2.5-flash` to generate a unique, multi-page story based on your personal memory.
- **Consistent AI Illustrations**: Leverages `gemini-2.5-flash-image` to generate a custom cover pattern and a unique, stylistically consistent illustration for every page of the story.
- **PDF Assembly**: Automatically assembles the generated text and images into a print-ready, square-format PDF using `fpdf2`.
- **Fully Customizable**: Control the story's protagonist, tone, style, setting, and even add a personal dedication.
- **Interactive CLI**: A simple and friendly command-line interface that guides you through every necessary input.

## How It Works

The application runs in a simple, five-step process:

1. **Collect Inputs**: The `main.py` script asks you for 11 key details (the memory, protagonist, theme, etc.).
2. **Generate Story**: These inputs are compiled into a detailed "master prompt." This prompt is sent to the Gemini API, which returns a complete, 5-page story separated by newlines.
3. **Generate Cover**: The `cover_theme` input is used to generate a single, seamless background pattern for the front and back cover.
4. **Generate Images**: The script starts a "chat" with the image AI. It first provides a "style guide" (based on your `protagonist_description`, `other_characters`, and `details`) to ensure all images are consistent. It then loops through each page of the story, sending the text as a prompt to get a matching illustration.
5. **Assemble PDF**: The `book_assembler.py` script takes the story text, all the generated images, the title, and the theme color. It then carefully places each element onto the pages of a square PDF, creating the final storybook.

## Installation

To run this project, you'll need Python 3.10+ and the required libraries.

### 1. Clone this repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2. Create a virtual environment (recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API Key

See the [Setting Up Your Gemini API Key](#setting-up-your-gemini-api-key) section below.

## Setting Up Your Gemini API Key

This tool requires a Google Gemini API key to function.

### Get your key

1. Go to the [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click on **"Get API key"** and then **"Create API key in new project"**
4. Copy the generated key

### Create a `.env` file

1. In the root directory of this project (the same folder as `requirements.txt`), create a new file named `.env`
2. Open the `.env` file and add the following line, pasting your key after the equals sign:

```
GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

3. Save the file

The `api_clients.py` script is already configured to read this file automatically, so you're all set. Your API key is kept private and will not be uploaded to GitHub (as `.env` is included in the `.gitignore` file).

## Usage

Once installed, you can run the application from the root directory of the project:

```bash
python -m src.main
```

The script will launch an interactive session. Pressing Enter without typing will accept the default value shown in brackets `[default]`. Here is an example of what the session will look like:

```
--- 📚 Memory-to-Storybook Generator ---
Please provide the following details. Press Enter to accept the default shown in brackets.

Enter the memory (briefly describe the event) [press Enter for default]: I had my daughter ask as I was going to the bathroom when she was three: what do you know about armadillos?
Protagonist name [Maya]:
Protagonist description [a 3-year-old girl with brown curly hair and big brown eyes]:
Tone (e.g., Funny, Serious, Tender) [Funny]:
Additional details / setting [The setting is our family home. The story scenes take place in a hallway and a bathroom.]:
Style (e.g., Rhyming, Narrative) [Rhyming]:
Complexity (Short/Standard/Advanced) [Standard]:
Story title [Silly Maya "Muffin" Elwer]:
End message to include [Merry Christmas! Love, Mom!]:
Other characters (brief) [The narrator, 'mom', is a woman with blonde hair.]:
Cover theme [armadillos and flowers]:
Theme color [light blue]:

Thanks! Generating a 'Funny' story for Maya...
Step 1/4: Crafting a unique story prompt...
Step 2/4: Calling Gemini for the story...
... Story text received!
Step 3/5: Calling API for cover image...
... Cover image received!
Step 4/5: Calling API for Maya's story images...
... 5 images received!
Step 5/5: Assembling the final PDF...
...PDF assembly complete. Pages created: 7

✅ Success! Your storybook has been saved as maya_storybook.pdf
```


## Understanding the Inputs

The quality of your storybook depends entirely on the quality of your inputs. Here is what each prompt does and why it's important.

| Input | Purpose |
|-------|---------|
| **Enter the memory** | This is the most important input. It's the "seed" for the entire story. A short, specific event (like the "armadillos" question) works best. The AI will build a 5-page plot around this single moment. |
| **Protagonist name** | The name of the main character (e.g., "Maya"). This will be used directly in the story text. |
| **Protagonist description** | Crucial for the image AI. This is your primary instruction for what the main character looks like. A good description like "a 3-year-old girl with brown curly hair and big brown eyes" is essential for generating consistent illustrations. |
| **Tone** | Sets the emotional feel of the story (e.g., "Funny", "Tender", "Adventurous"). The AI will adjust its writing style to match. |
| **Additional details / setting** | Crucial for the image AI. This tells the AI where the story is happening. "Our family home" and "scenes take place in a hallway and a bathroom" are vital clues for the illustrator. |
| **Style** | Controls the text generation. "Rhyming" instructs the AI to write a poem, while "Narrative" would produce standard prose. |
| **Story title** | This is the exact text that will be printed on the cover of your PDF. |
| **End message to include** | A personal dedication (e.g., "Merry Christmas! Love, Mom!") that will be printed on the final page of the book. |
| **Other characters** | Crucial for the image AI. Just like the protagonist description, this tells the image AI what other characters look like (e.g., "The narrator, 'mom', is a woman with blonde hair"). |
| **Cover theme** | This prompt is used to generate the single repeating background pattern for the front and back covers (e.g., "armadillos and flowers"). |
| **Theme color** | This sets the background color for all the internal story pages (the ones with illustrations). It must be one of: `light blue`, `light pink`, `light green`, `light yellow`, `light gray`, or `white`. |

## Tips for Best Results

Garbage in, garbage out. Follow these tips to get a high-quality storybook.

### ✅ DO...

**Be Specific (Especially for Images)**  
The AI can't read your mind. More detail produces better results.
- ❌ Bad: "a girl"
- ✅ Good: "a 4-year-old girl with bright red pigtails, freckles, and glasses"

**Be Detailed About Settings**
- ❌ Bad: "in the house"
- ✅ Good: "in a messy living room with a blue sofa and a big window"

**Check Your Spelling**  
The AI is literal. It will be confused by typos or if you spell a character's name two different ways.

**Keep the Memory Simple**  
The AI has to stretch your memory into a 5-page story. A simple, single event (like one funny question, one silly misunderstanding) works much better than a complex event (like "our entire 3-week vacation").

### 🚫 DON'T...

**Don't Use Vague Descriptions**  
Using generic terms for the protagonist will result in inconsistent images (different hair, gender, etc.) on every page.

**Don't Overcomplicate the Plot**  
The AI is writing a 5-page (20-line) rhyming story. It can't handle complex plots with multiple twists.

**Don't Expect Perfection**  
AI is an amazing creative partner, but it's not perfect. You might occasionally get a weird rhyme, a slightly strange-looking hand in an image, or a character that doesn't look exactly right. If you don't like the result, just run the script again!

## Example Output

Running the script with the default values (the "armadillos" memory) will produce a new file in your directory named: `maya_storybook.pdf`.

This file will be a **7-page, 210mm × 210mm square storybook**:

- **Page 1 (Cover)**: The title "Silly Maya 'Muffin' Elwer" centered on a white "bookplate" over a background pattern of "armadillos and flowers"
- **Pages 2–6 (Story)**: The 5-page rhyming story. Each page has a custom illustration at the top and the corresponding 4 lines of text at the bottom. The page background is light blue
- **Page 7 (Back Cover)**: The end message "Merry Christmas! Love, Mom!" on the same "armadillos and flowers" pattern

## Testing

This project uses `pytest` and `pytest-mock` to run unit tests. The tests are designed to check the logic of the `book_assembler.py` script without making live (and costly) calls to the Gemini API.

### Run all tests

```bash
pytest
```

### Run with detailed output

```bash
pytest -v
```

All tests should pass in the GitHub Actions CI/CD pipeline.

## AI-Assisted Development

This project was developed with assistance from AI tools, including Google's Gemini and GitHub Copilot. For a detailed breakdown of how these tools were used for planning, code generation, debugging, and documentation, see [AGENTS.md](./AGENTS.md).

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.