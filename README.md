# 📚 Memory-to-Storybook Generator

[![Tests](https://github.com/lelwer/memory-book/actions/workflows/tests.yml/badge.svg)](https://github.com/lelwer/memory-book/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

> A command-line tool that transforms a cherished personal memory into a custom, beautifully illustrated storybook PDF using Google's Gemini AI.

This project takes a simple, real-life moment—like a child's funny question—and uses AI to write a unique rhyming story, generate consistent illustrations for each page, and assemble it all into a single, print-ready PDF file.

> **Note:** This program generates AI-produced content, which may occasionally include visuals that are unrealistic or appear distorted. Please keep this in mind when running the program.
---

## 🎯 Project Vision: From CLI to Keepsake

This command-line application serves as the proof-of-concept for a larger vision: **a platform where parents can turn fleeting family moments into physical books**.

### The ultimate goal is to build a web interface where a user can:

1. **Enter** a memory and story details
2. **Get** an instant preview of a unique, AI-generated storybook
3. **Order** a physical, hardbound copy as a timeless family keepsake

This CLI tool is the "engine" that proves the core logic—turning a text prompt into a complete, illustrated book—is possible.

---

## 📑 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [API Configuration](#-api-configuration-crucial-step)
- [Usage](#-usage)
- [Input Guide](#-input-guide-what-do-the-prompts-do)
- [Example Output](#-example-output)
- [Tips for Best Results](#-tips-for-best-results)
- [Testing](#-testing)
- [AI-Assisted Development](#-ai-assisted-development)
- [License](#-license)

---

## ✨ Features

- **AI-Powered Storytelling**: Uses `gemini-2.5-flash` to generate a unique, 5-page rhyming story based on your memory
- **Consistent Illustrations**: Uses `gemini-2.5-flash-image` with a specialized "Style Guide" prompt to ensure characters look consistent across every page
- **Polaroid-Style Layout**: Automatically formats the PDF with solid theme colors, white "Polaroid" frames for images, and bold, readable text
- **Custom Cover Art**: Generates a seamless background pattern based on your chosen theme
- **Interactive CLI**: A friendly command-line interface with smart defaults for quick testing

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/lelwer/memory-book.git
cd memory-book
```

### 2. Create a virtual environment

Using a virtual environment prevents conflicts with other Python projects on your computer.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 API Configuration (Crucial Step)

This tool requires a Google Gemini API key to function.

### ⭐ Step 1: Create a New Google Cloud Project
1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. In the top navigation bar, click the **project selector** (the dropdown showing your current project).
3. Click **“New Project”** in the top-right corner.
4. Enter:
    * **Project Name** (anything you want)
    * **Organization** (if applicable)
    * **Location** (optional)
5. Click **Create**.
6. Wait a few seconds — Google will set it up.

You’ll see a notification once the project is ready.

### ⭐ Step 2: Switch Into That Project
1. Click the **project selector** again.
2. Choose the new project you just created.

*This is important — APIs and keys are always tied to whichever project is currently active.*

### ⭐ Step 3: Enable the Gemini API
Google lists Gemini models under Vertex AI → Generative AI APIs.

1. In the left sidebar, click **APIs & Services** → **Library**.
2. In the search bar, type: “Gemini”.
3. Click **Generative Language API** (this includes all Gemini model endpoints).
4. Click the **Enable** button.

If you see “Enabled,” you’re all set.

### ⭐ Step 4: Create an API Key
1. In the left sidebar, go to **APIs & Services** → **Credentials**.
2. Click **“+ CREATE CREDENTIALS”** at the top.
3. Select **API key**.
4. Google will instantly generate an API key for you and show it in a popup.

### ⭐ Step 5: (Important) Restrict the API Key
For security, you should restrict the key so only certain APIs or domains can use it.

1. In the popup, click **Restrict Key** (or go to **Credentials** → Click your new API key).
2. Under **API restrictions**, select:
    * **Restrict key**
    * Choose **Generative Language API** (this protects you from other services being used).
3. You may also add:
    * HTTP referrer restrictions (for websites)
    * IP address restrictions (for servers)
    * Android/iOS app restrictions

Click **Save**.

> **Note:** A Gemini Pro account is likely required to access these models. This may involve associated costs if your free trial has already been utilized.

### ⭐ Step 6: Paste Your Key

1. Create a `.env` file in the main /memory-book folder and paste your API key like the following:
```
GEMINI_API_KEY=YourActualKeyHere...
```

> **Note**: This file is ignored by Git to keep your key secure. Never share your `.env` file.

---

## 💻 Usage

Run the application from the root directory:
```bash
python -m src.main
```

The script will launch an interactive session. You can type your answers or press **Enter** to use the default values shown in brackets `[]`.
```
--- 📚 Memory-to-Storybook Generator ---
Please provide the following details...

Enter the memory [press Enter for default]: 
Protagonist name [Maya]: 
...
```

---

## 📝 Input Guide: What do the prompts do?

The quality of your book depends on your inputs. Here is how each prompt maps to the final PDF:

| Input | Where it goes in the PDF | Why it matters |
|-------|-------------------------|----------------|
| **Memory** | The Plot | This is the seed. "A trip to the zoo" becomes the story arc. Be specific! |
| **Protagonist Name** | Story Text | Used in the rhymes (e.g., "Little Maya ran so fast"). |
| **Protagonist Description** | The Images | Crucial. Defines the character for the AI illustrator. e.g., "A 3-year-old girl with curly brown hair." |
| **Tone** | Writing Style | "Funny" makes silly rhymes; "Tender" makes sweet, soft rhymes. |
| **Story Title** | Front Cover | Printed in Large Bold Text on the front cover. |
| **Cover Theme** | Cover Pattern | Generates the background pattern for the front and back covers (e.g., "Dinosaurs and stars"). |
| **End Message** | Back Cover | A dedication printed on the back. "Love, Mom & Dad, 2025". |
| **Theme Color** | Page Background | The background color behind the story text and image frames (e.g., "Light Blue"). |

---

## 📖 Example Output

After the program finishes, you will find a file like `[protagonist_name]_storybook.pdf` in your folder.

### The PDF structure:

- **Page 1 (Cover)**: Your selected Pattern background + Your Title in large text
- **Pages 2–6 (Story)**:
  - Background: Theme Color (e.g., Blue)
  - Top: A white "Polaroid" frame containing an AI Illustration of that page's scene
  - Bottom: 4 lines of Rhyming Text generated from your memory
- **Page 7 (Back)**: The Pattern background again + Your End Message

### Visual Preview

Here is an example of the **End Cover** and a **Story Page** generated by the tool:

<p float="left">
  <img src="assets/cover_preview.png" width="45%" />
  <img src="assets/story_preview.png" width="45%" /> 
</p>

*(The images above show the "Armadillos" theme with "Light Blue" background)*
---

## 💡 Tips for Best Results

### ✅ DO...

- **Be Descriptive with Looks**: Instead of "a boy", try "a 5-year-old boy with glasses, a red cap, and a blue shirt." This keeps the character looking the same on every page.
- **Keep the Memory Simple**: The AI writes a 5-page story. Simple memories (e.g., "Baking cookies with grandma") work better than complex ones (e.g., "Our 2-week vacation to Europe").
- **Check Spelling**: The AI reads literally. If you misspell a name, it will appear misspelled in the story.

### 🚫 DON'T...

- **Don't describe complex actions**: "He jumped while eating a sandwich and flying a kite" might confuse the image generator.
- **Don't worry about perfection**: AI art can sometimes be quirky (e.g., a hand with 6 fingers). It's part of the charm!

---

## 🧪 Testing

This project includes a full test suite using `pytest` and `pytest-mock`. We mock all API calls, so running tests does not cost you money or API credits.

**Run all tests:**
```bash
pytest
```

**Run with detailed output:**
```bash
pytest -v
```

---

## 🤖 AI-Assisted Development

This project was built using a "Pair Programmer" methodology with AI.

- **Gemini**: Served as the Lead Architect, planning the file structure, debugging API errors, and designing the PDF layout logic.
- **GitHub Copilot**: Assisted with writing boilerplate code, docstrings, and unit tests.

See `AGENTS.md` for a detailed log of the prompts and strategy used.

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.