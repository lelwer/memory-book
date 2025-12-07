
---
# AI Usage & Contribution Guide (AGENTS.md)

This repository uses AI tools as development partners. This document explains which agents were used, how they were used, the policies contributors must follow when using AI, and example prompts that conform to our standards.

This project was developed using a "pair programmer" methodology.


## 1 — AI Tools Used

This project used a multi-agent strategy. Each tool filled a specific role:

- **Google Gemini (Advanced)** — Primary "Senior Developer" / Architect: high-level planning, architecture, complex functions (PDF assembly, API clients), debugging, and documentation (README, LICENSE, CI workflow, this file).
- **GitHub Copilot** — In-editor assistant: boilerplate, docstrings, inline completions, and small refactors.
- **Anthropic Claude** — Specialist: initial drafts for complex pytest cases and targeted generation tasks.


## 2 — AI Development Policy & Standards

All contributors (including graders) who use AI-assisted generation must follow these standards to preserve code quality and maintainability.

### Rule 1 — Adherence to Project Standards

All AI-generated code must follow the project's conventions:

- Language: Python 3.10+
- Docstrings: Numpy-style docstrings for functions and methods
- Tests: Every non-trivial change must include `pytest` unit tests
- Mocking: Tests that depend on external services must use `pytest-mock` or `unittest.mock` to simulate network/API behavior

### Rule 2 — AI Is a Pair Programmer, Not an Autopilot

You remain the author and owner of any AI-assisted code. Responsibilities include:

- Read and understand every line of AI-generated code before committing
- Write tests that validate behavior, edge cases, and error handling
- Debug and refine AI outputs — the first draft is rarely final

### Rule 3 — Security: Never Commit Secrets

AI tools may log interactions. Never paste secrets (API keys, passwords) into prompts. Use placeholders like `YOUR_API_KEY_HERE` and keep real keys in a `.env` file (which is in `.gitignore`).


## 3 — Strategic AI Usage Log (By Phase)

This section describes how the above policies were followed across development phases.

### Phase 1 — Planning & Architecture

- Tool: Gemini
- Action: Validated the concept vs. course constraints and chose a CLI prototype over a full web app
- Result: Project scaffold (`src/`, `tests/`, `requirements.txt`) and the high-level pipeline: `main.py` → `api_clients.py` → `book_assembler.py`

### Phase 2 — Code Generation

- Tools: Gemini, GitHub Copilot
- Action: Generated initial full-file drafts for `src/` modules, including API client logic (google-generativeai), PDF assembly (fpdf2), and the main orchestration

### Phase 3 — Iterative Refinement & Debugging

- Tool: Gemini (primary)
- Typical problems & actions:
	- PDF layout issues (e.g., missing alpha/transparency): debugged and improved layout; reintroduced a white "bookplate" for readability; added aspect-ratio-preserving image placement
	- Poor rhymes: tightened the `full_prompt` to require stronger rhyming
	- Image glitches: added `negative_prompt` instructions and removed image-to-image transformations to avoid artifact propagation

### Phase 4 — Testing

- Tools: Claude (initial tests), Gemini (refinements)
- Action: Produced pytest-focused tests using `pytest-mock` and `unittest.mock` to simulate API responses and file I/O, ensuring tests run offline for CI

### Phase 5 — Documentation

- Tools: Gemini, GitHub Copilot
- Action: Generated `LICENSE`, `.gitignore`, CI workflow (`.github/workflows/tests.yml`), `README.md`, and this `AGENTS.md`


## 4 — Example Prompts (Enforcing Our Standards)

Example prompts below show how to request code or tests while ensuring project standards (Numpy docstrings, pytest, mocking).

### Example: Generating a Helper Function

Prompt:

```text
Write a helper function for `src/book_assembler.py` that takes a `pdf` object and a `theme_color` string. It should look up the RGB tuple from `COLOR_MAP` and draw a full-page background rectangle. It must include Numpy-style docstrings and Python 3.10+ type hints.
```

### Example: Generating a New Test

Prompt:

```text
I need a new test for `tests/test_api_clients.py`. Using `pytest` and `pytest-mock`, write a test for `get_story_from_gemini` that simulates `google.generativeai` raising a `ConnectionError`. The test must assert that the function catches this error and returns the placeholder story text.
```

### Example: Debugging Prompt

Prompt:

```text
My fpdf2 code is crashing with the error "'PDF' object has no attribute 'set_alpha'". Here is my code: [...]. Why is this happening and what is the correct way to set transparency?
```


---

If you use AI tools while contributing to this repository, follow the rules above and add a short note to your commit message indicating what AI tool(s) and prompts you used (this helps with transparency).
