# Python Code Style Guide

### General Principles
- Write **all code in English** (names, docstrings, comments, messages).
- **Format code and imports with Ruff** and **never exceed 80 columns**.
- Maintain **clarity, readability and single responsibility** in each function.
- Structure modules by **context**; if it grows too large or contains multiple actions, **split into subcontexts**.
- **When I request prompt generation or prompt content, return in Markdown.**

### Python (version and dependencies)
- Use **Python ≥ 3.12**.
- **Never add `from __future__ import annotations`** or any other `__future__` import in Python ≥ 3.12 projects.
- **Always use modern type hints syntax native to Python 3.12+.**
- **Manage dependencies with `uv`**; **do not** use `pip` or `poetry`.

### Typing and signatures
- **Always use type hints** in function signatures and class variables; also apply to other variables when necessary.
- When a function has **more than one argument**, **break the signature into multiple lines** and **place comma after the last argument** (trailing comma) to maintain Ruff formatting.

### Function calls
- **Use keyword arguments (kwargs)** whenever there is more than one argument.
- If there is only one argument, **use keyword when it increases semantic clarity**.
- **Break calls into multiple lines** when there is more than one argument.
- **Always add trailing comma** after the last argument.

### Module and function organization
- In each module, **define the main function first**.
  - This function should **act as an index/roadmap** (orchestration), **calling helpers**, and contain **minimal logic**.
- **Order helpers** in the sequence they are called, creating a **natural narrative flow** (index → chapter → subtitle).
- **Ensure Single Responsibility** for each helper.
  - If a helper needs to do more than one thing, **extract subhelpers** and **call them**.

### Project Structure
- Always include a **main entry point** (`main.py` or equivalent) to run the process.
- **Organize code into multiple modules** cohesively, avoiding excessive accumulation in a single file.
- Structure modules so the project is **easy to extend in the future**, allowing new features or components to be added without causing significant breaks.

### Code style and formatting
- **Always use f-strings**; **do not** use `%` or `.format()`.
- Prefer **`pathlib.Path`** instead of `os.path`.
- **Break long queries** (SQL, PromQL etc.) into multiple lines.
- **Order imports** in three groups (stdlib, third-party, local), according to Ruff.
- **Avoid magic values**; prefer **environment variables** or configuration files.
- **Mandatory docstrings** at **module, class and function** level; be **compact**, **in English** and **≤ 80 columns** (break lines when necessary).
- **Punctual comments** are allowed when necessary; always **in English** and **≤ 80 columns**.