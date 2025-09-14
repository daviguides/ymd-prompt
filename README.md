# YMD Prompt

<p align="center">
  <a href="http://daviguides.github.io"><img src="https://img.shields.io/badge/built%20with-%E2%9D%A4%EF%B8%8F%20by%20Davi%20Guides-orange"></a>
  <img src="https://img.shields.io/badge/tests-passing-brightgreen">
  <img src="https://img.shields.io/badge/coverage-100%25-brightgreen">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg"></a>
</p>

**YMD Prompt** is a small Python library + CLI to **load**, **validate**, and **render**  
`.ymd` / `.yamd` files — a hybrid format where YAML holds metadata and Markdown holds prompt text.

---

## ✨ Features
- ✅ Pydantic models for strict validation (`id`, `kind`, `version`, `title`, sections)
- 📥 Loader: `load(path)` and `loads(text)` using `yaml.safe_load`
- 🧩 Rendering with Jinja2: `render(prompt, context)` replaces `{{var}}`
- 🔎 Placeholder discovery: `list_placeholders()`
- 🔒 `strict_placeholders=True` to enforce completeness
- 🖥️ CLI: `ymd` for rendering and placeholder inspection

---

## 🚀 Install
```bash
pip install ymd
```

---

## 📚 Library usage
```python
from ymd import load, render, list_placeholders

p = load("examples/sample.ymd")
needed = list_placeholders(p.sections())
print("placeholders:", needed)

out = render(p, {"diff": "+++ simulated diff +++"})
print(out["user"])
```

---

## 🖥️ CLI usage
```bash
# Render and print JSON with all sections
ymd render examples/sample.ymd --var diff="@examples/diff.txt"

# Render a single section to stdout
ymd render examples/sample.ymd --var diff="+++diff+++" --section user

# Render all sections into separate files under out/
ymd render examples/sample.ymd --var diff="+++diff+++" --outdir out

# List placeholders
ymd placeholders examples/sample.ymd
```

### Options
```
--var KEY=VALUE         # add a single variable (use @path to read from file)
--vars-json PATH        # load a JSON file with variables
--section NAME          # only print given section (system|instructions|user...)
--outdir DIR            # write rendered sections to files (NAME.md)
--no-strict             # allow missing placeholders (render empty string)
--format json|md        # output format (default: json; md prints a combined document)
```

---

## 📂 Example
See [examples/sample.ymd](examples/sample.ymd).

---

## ⚖️ License
MIT
