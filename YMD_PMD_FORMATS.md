# YMD & PMD Formats Documentation

## Overview

**YMD (YAML + Markdown + Jinja2)** and **PMD (Prompt Markdown + Jinja2)** are open format specifications for writing structured, modular, and reusable AI prompts. They combine the best of three technologies:

- **YAML** for metadata and structure
- **Markdown** for rich text content
- **Jinja2** for dynamic placeholders (`{{var}}`) and includes (`{% include "file.pmd" %}`)

These formats solve the "spaghetti prompt" problem by providing **organization, reusability, and validation** for complex prompt engineering workflows.

## Format Origins

YMD and PMD are format specifications proposed and developed by **Davi Guides** (https://github.com/daviguides). They are defined as **open language specifications**, independent of any specific implementation, allowing anyone to create their own libraries, extensions, or tools to support them.

**Current Reference Implementations:**
- **[ymd-prompt](https://github.com/daviguides/ymd-prompt)**: Python library for loading, validating, and rendering `.ymd`/`.pmd` files
- **[vscode-ymd-syntax](https://github.com/daviguides/vscode-ymd-syntax)**: VS Code extension for syntax highlighting, snippets, and include navigation

---

## Core Concepts

### YMD (YAML + Markdown + Jinja2)
Complete prompt manifests containing:
- **Metadata**: `id`, `kind`, `version`, `title`, etc.
- **Sections**: `system`, `instructions`, `user`, `expected_output`, or custom sections
- **Jinja2 Support**: Variables and includes for modularity

### PMD (Prompt Markdown + Jinja2)
Modular prompt blocks containing:
- **Rich Text**: Markdown content with Jinja2 templating
- **Reusable Components**: Checklists, examples, system messages, templates
- **Include Chains**: A includes B which includes C, etc.

### Key Philosophy
Break large, complex prompts into **manageable, reusable units** - similar to how large functions are broken into smaller ones in programming.

---

## YMD Format Specification

### Basic Structure

```yaml
id: unique_identifier
kind: prompt_category
version: 0.1.0
title: Human-readable description

section_name: |
  Markdown content with Jinja2 support
  Variables: {{variable_name}}
  {% include "path/to/component.pmd" %}

another_section: |
  More content with {{placeholders}}
```

### Required Metadata Fields

- **`id`**: Unique identifier (string, min 1 character)
- **`kind`**: Prompt category/type (string, min 1 character)
- **`version`**: Semantic version (string, must contain digits)
- **`title`**: Human-readable description (string, min 1 character)

### Standard Section Conventions

While sections are flexible and user-definable, common patterns include:

- **`system`**: System role and behavior instructions
- **`instructions`**: Detailed task instructions and requirements
- **`expected_output`**: Output format and structure expectations
- **`user`**: User context and input template
- **`developer`**: Development/debugging information (optional)

### Complete YMD Example

```yaml
id: pr_description_generator
kind: gh_pr
version: 0.1.0
title: Generate GitHub Pull Request Description from Diff

system: |
  You are a **senior software maintainer** with expertise in:
  - {{primary_language}} development
  - {{project_domain}} best practices
  - Code review and technical communication

  {% include "shared/maintainer_principles.pmd" %}

instructions: |
  {% include "github/pr_analysis_steps.pmd" %}

  Focus areas for this review:
  {% for area in focus_areas %}
  - **{{area.name}}**: {{area.description}}
  {% endfor %}

expected_output: |
  {% include "github/pr_output_format.pmd" %}

user: |
  {% include "github/pr_context.pmd" %}

  **Diff to analyze:**
  ```diff
  {{diff}}
  ```

  **Additional context:**
  - Branch: {{branch_name}}
  - Author: {{author}}
  - Files changed: {{files_changed}}
```

---

## PMD Format Specification

### Structure

PMD files are **Markdown + Jinja2** documents focused on reusable content blocks:

```markdown
## Component Title

Markdown content with full Jinja2 support:
- Variables: {{variable_name}}
- Conditionals: {% if condition %}...{% endif %}
- Loops: {% for item in items %}...{% endfor %}
- Includes: {% include "other.pmd" %}
- Comments: {# This is a Jinja2 comment #}

### Sub-sections

{{dynamic_content}}

{% include "nested/component.pmd" %}
```

### PMD Example: Reusable Checklist

```markdown
{# github/pr_checklist.pmd #}
## Quality Checklist

### Code Quality
- [ ] Code follows {{coding_standard}} guidelines
- [ ] No hardcoded values or magic numbers
- [ ] Error handling is appropriate
- [ ] Performance impact is {{performance_level}}

### Testing
{% if test_coverage_required %}
- [ ] Unit tests added/updated (target: {{coverage_target}}%)
- [ ] Integration tests pass
{% endif %}
- [ ] Manual testing completed

### Documentation
- [ ] Code comments updated
- [ ] API documentation updated
{% if breaking_changes %}
- [ ] **Breaking changes documented in CHANGELOG**
- [ ] Migration guide provided
{% endif %}

### Security
{% include "./security_checklist.pmd" %}

### Deployment
{% if deployment_type == "production" %}
{% include "./production_checklist.pmd" %}
{% else %}
{% include "./staging_checklist.pmd" %}
{% endif %}
```

---

## Jinja2 Template Features

### Variable Substitution

```markdown
Hello {{user_name}}, your {{item_type}} #{{item_id}} is {{status}}!

Processing details:
- Duration: {{duration}} minutes
- Priority: {{priority_level}}
- Team: {{assigned_team}}
```

### File Includes

Include other files for modular composition:

```markdown
{% include "path/to/component.pmd" %}
{% include "./relative/path.pmd" %}
{% include "../shared/header.pmd" %}
```

### Conditional Logic

```markdown
{% if debug_mode %}
## Debug Information
- Debug level: {{debug_level}}
- Timestamp: {{timestamp}}
- Environment: {{environment}}
{% endif %}

{% if environment == "production" %}
{% include "production_warnings.pmd" %}
{% else %}
{% include "development_notes.pmd" %}
{% endif %}
```

### Loops and Iteration

```markdown
{% for item in checklist_items %}
- [ ] **{{item.title}}**: {{item.description}}
  {% if item.critical %}🚨 **CRITICAL**{% endif %}
  {% if item.notes %}
    - Notes: {{item.notes}}
  {% endif %}
{% endfor %}

## Team Members
{% for member in team_members %}
**{{member.name}}** ({{member.role}})
- Expertise: {{member.expertise}}
- Contact: {{member.email}}

{% endfor %}
```

### Advanced Include with Section Selection

YMD supports a special helper for including specific sections from other YMD files:

```markdown
{% include_section "other_prompt.ymd", "system" %}
```

### Jinja2 Comments

```markdown
{# This is a comment that won't appear in rendered output #}
{# TODO: Update this section when API v2 is released #}

## Visible Section
{#
Multi-line comment explaining complex logic:
This section handles edge cases for...
#}
```

---

## Processing Pipeline

### YMD Processing Flow

1. **Load**: `load(path)` → parses and validates YAML → creates `Prompt` (Pydantic model)
2. **Render**: `YmdFile.from_path(...)` → loads, validates, and renders with Jinja2
3. **Access**: `.rendered` → returns dictionary `{section: rendered_text}`
4. **Output**: `.join()` → concatenates sections into final Markdown document

### PMD Processing Flow

1. **Load**: `load(path)` → loads and immediately renders with Jinja2
2. **Access**: `PmdFile` contains both `raw` and `content` (rendered)
3. **Chaining**: Supports nested includes: A includes B which includes C

### Example Usage

```python
from ymd import load, render
from pmd import PmdFile

# Load and render YMD
prompt = load("prompts/pr_generator.ymd")
context = {
    "diff": "// actual diff content",
    "author": "john_doe",
    "branch_name": "feature/api-v2",
    "focus_areas": [
        {"name": "Security", "description": "Check for vulnerabilities"},
        {"name": "Performance", "description": "Analyze efficiency"}
    ]
}

rendered = render(prompt, context)
print(rendered["user"])  # Access specific section
print(rendered.join())   # Full document

# Load and render PMD
checklist = PmdFile.from_file("components/checklist.pmd")
print(checklist.content)  # Rendered content
```

---

## Placeholder Detection and Validation

### Basic Placeholder Detection

```python
from ymd import list_placeholders

# Simple regex-based detection (direct placeholders only)
placeholders = list_placeholders(text)
print(f"Direct variables: {placeholders}")
```

### Deep Placeholder Analysis

```python
from ymd import collect_placeholders_deep_from_text

# Recursive detection through includes/imports
all_placeholders = collect_placeholders_deep_from_text(
    text=content,
    base_path=Path("prompts/")
)
print(f"All variables (including from includes): {all_placeholders}")
```

### Strict vs Permissive Rendering

```python
# Strict mode - error if variable is missing
rendered = render(prompt, context, strict_placeholders=True)

# Permissive mode - empty string for missing variables
rendered = render(prompt, context, strict_placeholders=False)
```

---

## Extensibility and Customization

### Custom Metadata Models

YMD is not closed - users can define custom metadata structures:

```python
from pydantic import BaseModel, Field
from ymd import make_prompt_class

class CustomMeta(BaseModel):
    id: str
    kind: str
    version: str
    title: str
    author: str = Field(..., description="Prompt author")
    tags: list[str] = Field(default_factory=list)
    complexity: int = Field(ge=1, le=5, description="Complexity level 1-5")

# Create custom prompt class
CustomPrompt = make_prompt_class(meta_class=CustomMeta)

# Use with custom validation
prompt = CustomPrompt.from_file("custom_prompt.ymd")
```

### Custom Section Conventions

```python
class ApiDocSections(BaseModel):
    overview: str
    authentication: str
    endpoints: str
    examples: str
    errors: str | None = None

ApiPrompt = make_prompt_class(
    meta_class=CustomMeta,
    sections_class=ApiDocSections
)
```

### Default vs Custom Classes

```python
# Use built-in defaults
from ymd import DefaultPrompt
prompt = DefaultPrompt.from_file("standard.ymd")

# Or create fully custom
prompt = CustomPrompt.from_file("api_docs.ymd")
```

---

## CLI Tools

### YMD Rendering Commands

```bash
# Basic rendering
ymd-render prompts/pr_generator.ymd --var diff="@changes.txt" --var author="john"

# Single section output
ymd-render prompts/docs.ymd --var api_version="v2" --section instructions

# Save to directory (each section as separate file)
ymd-render prompts/complete.ymd --var env="prod" --outdir rendered/

# List all placeholders (including from included files)
ymd-render prompts/complex.ymd --placeholders

# Load variables from JSON file
ymd-render prompts/api.ymd --vars-json config/prod.json

# Permissive mode (allow missing variables)
ymd-render prompts/draft.ymd --var partial="data" --no-strict
```

### PMD Rendering Commands

```bash
# Render standalone PMD
pmd-render components/checklist.pmd --var task="deployment" --var env="prod"

# Use with variable files
pmd-render templates/review.pmd --vars-json review_context.json

# Multiple variables
pmd-render sections/api_docs.pmd \
  --var service="auth" \
  --var version="v2.1" \
  --var examples="@examples.json"
```

### CLI Options Reference

- `--var KEY=VALUE`: Set single variable
- `--var KEY=@file.txt`: Load variable content from file
- `--vars-json config.json`: Load all variables from JSON
- `--section NAME`: Output specific section only (YMD)
- `--outdir DIR`: Save sections as separate files
- `--no-strict`: Allow undefined variables (render as empty)
- `--format json|md`: Output format
- `--placeholders`: List all required variables

---

## Development Tools

### VS Code Extension Features

The **[vscode-ymd-syntax](https://github.com/daviguides/vscode-ymd-syntax)** extension provides:

#### Syntax Highlighting
- **Hybrid highlighting**: YAML + Markdown + Jinja2
- **Context-aware**: Recognizes sections and transitions
- **Jinja2 support**: Variables, includes, comments, control structures

#### Navigation
- **Ctrl/Cmd + Click** on includes → opens target file
- **Go to definition** for included components
- **Breadcrumb navigation** in complex nested structures

#### Snippets
- `prompt` → Full YMD template
- `blk` → PMD block template
- `inc` → Include statement
- `var` → Variable placeholder
- `if` → Conditional block
- `for` → Loop block

#### File Management
- **Custom icons** for `.ymd` and `.pmd` files
- **File association** with proper language modes
- **Comment support** for Jinja2 comments (`{# ... #}`)

### Python Library Features

The **[ymd-prompt](https://github.com/daviguides/ymd-prompt)** library provides:

#### Core Packages
- **`ymd`**: Complete prompt manifests (.ymd files)
- **`pmd`**: Modular prompt blocks (.pmd files)
- **`common`**: Shared utilities and validation

#### Loading Approaches
```python
# Functional approach
from ymd import load, loads, render
prompt = load("file.ymd")
rendered = render(prompt, context)

# Object-oriented approach
from ymd import YmdFile
prompt = YmdFile.from_file("file.ymd")
rendered = prompt.rendered

# Direct content loading
from ymd import loads
prompt = loads(ymd_string_content)
```

#### Validation with Pydantic
- **Automatic validation** of metadata and structure
- **Type checking** for all fields
- **Custom validators** for version formats and constraints
- **Clear error messages** for invalid content

---

## File Organization Best Practices

### Recommended Directory Structure

```
prompts/
├── main/                           # Primary prompt files
│   ├── github/
│   │   ├── pr_generator.ymd
│   │   ├── issue_triage.ymd
│   │   └── release_notes.ymd
│   ├── docs/
│   │   ├── api_documentation.ymd
│   │   └── user_guides.ymd
│   └── code_review/
│       ├── security_review.ymd
│       └── performance_review.ymd
├── components/                     # Reusable PMD components
│   ├── roles/
│   │   ├── senior_developer.pmd
│   │   ├── technical_writer.pmd
│   │   └── security_expert.pmd
│   ├── checklists/
│   │   ├── security_checklist.pmd
│   │   ├── performance_checklist.pmd
│   │   └── accessibility_checklist.pmd
│   ├── formats/
│   │   ├── pr_template.pmd
│   │   ├── api_response_format.pmd
│   │   └── documentation_structure.pmd
│   └── examples/
│       ├── code_examples.pmd
│       ├── api_examples.pmd
│       └── test_examples.pmd
├── shared/                         # Cross-project components
│   ├── common_roles.pmd
│   ├── output_standards.pmd
│   └── validation_rules.pmd
├── config/                         # Variable configurations
│   ├── development.json
│   ├── staging.json
│   ├── production.json
│   └── team_contexts.json
└── examples/                       # Sample data and contexts
    ├── sample_diff.txt
    ├── api_response.json
    └── test_scenarios/
```

### Naming Conventions

#### Files
- **YMD files**: Use descriptive names reflecting purpose
  - `github_pr_generator.ymd`
  - `api_documentation_writer.ymd`
  - `security_code_reviewer.ymd`

- **PMD files**: Use component-focused names
  - `security_checklist.pmd`
  - `senior_developer_role.pmd`
  - `api_response_format.pmd`

#### Variables
- **snake_case** for consistency: `user_name`, `api_endpoint`
- **Descriptive names**: `github_pr_number` vs `number`
- **Grouped naming**: `db_host`, `db_port`, `db_name`
- **Context prefixes**: `github_`, `api_`, `deployment_`

### Modular Design Principles

1. **Single Responsibility**: Each PMD file should have one clear purpose
2. **Logical Grouping**: Group related components in subdirectories
3. **Dependency Management**: Keep include chains shallow and logical
4. **Reusability**: Design components to work across multiple contexts
5. **Documentation**: Include comments explaining complex logic
6. **Version Control**: Track changes like code, use semantic versioning

---

## Common Use Cases and Patterns

### GitHub Workflow Automation

```yaml
# github_pr_comprehensive.ymd
id: github_pr_comprehensive
kind: code_review
version: 2.1.0
title: Comprehensive GitHub PR Analysis

system: |
  {% include "roles/senior_maintainer.pmd" %}

instructions: |
  {% include "github/pr_analysis_workflow.pmd" %}

  **Project Context:**
  - Technology stack: {{tech_stack}}
  - Project complexity: {{complexity_level}}
  - Team experience: {{team_experience}}

user: |
  **Pull Request Analysis Required**

  {% include "github/pr_context_template.pmd" %}

  **Files changed:** {{files_changed}}
  **Diff:**
  ```diff
  {{diff}}
  ```

  {% include "github/analysis_requirements.pmd" %}
```

### API Documentation Generation

```yaml
# api_docs_generator.ymd
id: api_documentation_generator
kind: technical_writing
version: 1.5.0
title: RESTful API Documentation Generator

system: |
  {% include "roles/api_technical_writer.pmd" %}

instructions: |
  {% include "api/documentation_workflow.pmd" %}

expected_output: |
  {% include "api/documentation_format.pmd" %}

user: |
  **API Endpoint Documentation Request**

  - **Method**: {{http_method}}
  - **Endpoint**: `{{api_path}}`
  - **Service**: {{service_name}}
  - **Version**: {{api_version}}

  {% include "api/endpoint_context.pmd" %}

  **OpenAPI Spec:**
  ```yaml
  {{openapi_spec}}
  ```
```

### Code Review Templates

```yaml
# security_review.ymd
id: security_code_review
kind: security_audit
version: 1.2.0
title: Security-Focused Code Review

system: |
  {% include "roles/security_expert.pmd" %}

  **Security Focus Areas:**
  {% for area in security_focus_areas %}
  - **{{area.category}}**: {{area.description}}
    - Risk level: {{area.risk_level}}
    - Check priority: {{area.priority}}
  {% endfor %}

instructions: |
  {% include "security/review_methodology.pmd" %}

user: |
  **Security Review Request**

  {% include "security/threat_model_context.pmd" %}

  **Code to review:**
  ```{{language}}
  {{code_content}}
  ```

  {% include "security/specific_concerns.pmd" %}
```

---

## Integration with Claude Code

### Project Configuration

When using YMD/PMD in Claude Code projects, include this in your `CLAUDE.md`:

```markdown
# Project Name

## Prompt Template System

This project uses **YMD/PMD formats** for structured, modular AI prompts:

### Format Overview
- **YMD (YAML + Markdown + Jinja2)**: Complete prompt manifests with metadata and sections
- **PMD (Prompt Markdown + Jinja2)**: Reusable components and templates
- **Both support**: Variables `{{var}}`, includes `{% include "file.pmd" %}`, conditionals, loops

### Core Commands
- `ymd-render file.ymd --var key=value`: Render YMD templates
- `pmd-render file.pmd --vars-json vars.json`: Render PMD components
- `--placeholders`: List all required variables across includes
- `--section NAME`: Extract specific sections from YMD files

### Project Structure
- `/prompts/main/`: Primary YMD prompt files
- `/prompts/components/`: Reusable PMD components
- `/prompts/shared/`: Cross-project shared components
- `/prompts/config/`: Variable configuration files

### Key Principles
- **Modular Design**: Break large prompts into focused, reusable pieces
- **Include Chains**: Use `{% include %}` to avoid duplication
- **Variable Context**: Pass context through structured JSON configurations
- **Validation**: Leverage Pydantic models for prompt structure validation

### Documentation
- Complete format specification: `YMD_PMD_FORMATS.md`
- VS Code extension: [vscode-ymd-syntax](https://github.com/daviguides/vscode-ymd-syntax)
- Python library: [ymd-prompt](https://github.com/daviguides/ymd-prompt)

When working with prompts:
1. Check existing components before creating new ones
2. Use descriptive variable names and document context requirements
3. Test templates with realistic sample data
4. Version control prompt changes with semantic versioning
```

### Memory Integration

Add to Claude Code project memory:

```markdown
# YMD/PMD Prompt Engineering

## Quick Reference
- `.ymd`: Complete prompts (YAML metadata + Markdown sections)
- `.pmd`: Reusable components (Markdown + Jinja2)
- Variables: `{{name}}`, Includes: `{% include "file.pmd" %}`
- CLI: `ymd-render`, `pmd-render` with `--var` and `--vars-json`

## Working with Templates
- Always check `/prompts/components/` for existing reusable pieces
- Use `--placeholders` to discover required variables
- Organize by context: github/, api/, docs/, security/
- Test with realistic data before deploying
```

---

## Troubleshooting and Common Pitfalls

### Include Path Resolution

```markdown
<!-- ❌ Wrong: Absolute paths -->
{% include "/full/path/to/file.pmd" %}

<!-- ✅ Correct: Relative paths -->
{% include "./relative/file.pmd" %}
{% include "../shared/component.pmd" %}
{% include "components/checklist.pmd" %}
```

### Variable Naming Issues

```markdown
<!-- ❌ Problematic: Special characters -->
{{user-name}}  <!-- Hyphens can cause issues -->
{{user.name}}  <!-- Dots have special meaning -->

<!-- ✅ Safe: Underscore naming -->
{{user_name}}
{{api_endpoint}}
{{deployment_config}}
```

### Circular Dependencies

```markdown
<!-- ❌ Circular include problem -->
<!-- file_a.pmd includes file_b.pmd -->
<!-- file_b.pmd includes file_a.pmd -->

<!-- ✅ Solution: Extract common parts -->
<!-- file_a.pmd and file_b.pmd both include shared.pmd -->
```

### Missing Variable Debugging

```bash
# List all required variables
ymd-render prompt.ymd --placeholders

# Run in permissive mode to see missing variables
ymd-render prompt.ymd --var known="value" --no-strict

# Use detailed error output
ymd-render prompt.ymd --var partial="data" --verbose
```

---

## Conclusion

YMD and PMD represent a **comprehensive approach to prompt engineering** that brings software development best practices to AI prompt design:

### Key Benefits
- ✅ **Modularity**: Break complex prompts into manageable, reusable components
- ✅ **Validation**: Pydantic-based structure validation prevents errors
- ✅ **Maintainability**: Version control, includes, and clear organization
- ✅ **Flexibility**: Extensible metadata and section conventions
- ✅ **Tooling**: Rich ecosystem with VS Code support and CLI tools
- ✅ **Compatibility**: Built on standard formats (YAML, Markdown, Jinja2)

### Format Summary
- **YMD**: Complete prompt manifests with metadata and structured sections
- **PMD**: Modular prompt components for maximum reusability
- **Together**: A comprehensive system for scalable prompt engineering

### Open Ecosystem
As open format specifications, YMD and PMD encourage:
- Multiple implementation approaches
- Community-driven tooling development
- Custom extensions and integrations
- Cross-platform compatibility

The result is a **more organized, maintainable, and collaborative approach to AI prompt development**, supported by real tools and growing ecosystem:

- **[ymd-prompt](https://github.com/daviguides/ymd-prompt)** - Python implementation
- **[vscode-ymd-syntax](https://github.com/daviguides/vscode-ymd-syntax)** - VS Code tooling
- **Open specification** - Community implementations welcome

For more information, visit the GitHub repositories or contact the format creator: **Davi Guides** (https://github.com/daviguides).