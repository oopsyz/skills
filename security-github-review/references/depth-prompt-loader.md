# Depth Prompt Loader

This module provides prompt template loading logic for the security-github-review skill, enabling flexible depth-based prompts without cluttering the main SKILL.md file.

## Usage

In the main skill orchestration logic, replace the prompt template loading section with:

```yaml
### Step 0: Confirm scope (fast)

- Verify Security MCP availability:
- Load appropriate prompt template from `references/depth-prompt-loader.md` based on depth and compliance parameters.
- Load prompt template and determine depth preference:
  - If `depth` is not provided, default to `quick` (fast review).
  - Load appropriate prompt template from `references/prompts-for-depth-levels.md` based on depth and compliance parameters.
  - If depth or compliance is specified, use corresponding focused prompt template:
    - `depth=quick`: Use quick review prompts from prompts-for-depth-levels.md
    - `depth=standard` or unspecified: Use standard review prompts
    - `depth=deep`: Use deep review prompts with comprehensive analysis
    - `compliance=nist-800-53`: Use compliance-focused prompts
    - `compliance=privacy`: Use privacy-focused prompts
  - Proceed with review using loaded prompt template.
- After completing review, ask to user if they would like:
  - "Would you like a more advanced analysis? This can include:"
  - [next depth level-specific benefits]
  - If user responds "yes" or "advanced", or requests "standard/deep", re-run review using deeper prompt template from prompts-for-depth-levels.md:
    - If currently at `quick` level and user requests deeper analysis:
      - Load `depth=standard` or `depth=deep` prompt template
      - Execute review with expanded scope including:
        - Code-level vulnerability examination
        - Detailed threat modeling with attack scenarios
        - Expanded ASVS/NIST compliance checks
        - Comprehensive remediation guidelines with code examples
    - If currently at `standard` or `deep` level and user requests deeper analysis:
      - This indicates potential gap or uncertainty - offer to clarify findings before proceeding with deeper analysis
    - If user declines or requests to proceed, finalize current review output.
    - If `output` or `depth` is still ambiguous after initial preference check, proceed with `output=report`, `depth=quick`, and ask clarifying questions.
```

## Prompt Template Loading Function

```python
def load_prompt_template(depth: str, compliance: str = None) -> str:
    """
    Load appropriate prompt template based on depth and compliance focus.
    
    Args:
        depth: 'quick', 'standard', 'deep', or None
        compliance: 'nist-800-53', 'privacy', or None
    
    Returns:
        Path to the appropriate prompt template file
    """
    
    templates_dir = Path(__file__).parent / "references" / "prompts-for-depth-levels.md"
    
    # Base filename for standard reviews
    base_filename = "standard-review"
    
    # Add compliance modifier if needed
    if compliance and compliance != "none":
        base_filename = f"{compliance}-{base_filename}"
    
    # Use deep prompts for deep reviews
    if depth == "deep":
        base_filename = "deep-review"
    
    prompt_file = templates_dir / f"{base_filename}.md"
    
    if prompt_file.exists():
        return prompt_file
    else:
        # Fallback to default standard review prompts if specific template not found
        fallback_file = templates_dir / "standard-review.md"
        if fallback_file.exists():
            return fallback_file
        else:
            # Create default standard review prompts if none exist
            default_prompts = """# Standard Security Review

[repo_url or repo_path]

Please perform a standard security review including:

## Review Scope

1. Critical and high severity vulnerabilities
2. OWASP ASVS L2 compliance mapping
3. Basic threat modeling
4. Code-level analysis where appropriate

## Deliverables

Please provide:

1. A prioritized list of security findings
2. ASVS requirement mappings
3. Practical remediation recommendations
4. Gap analysis
"""
    
    return str(prompt_file)
```

## Integration Notes

The loader function should be integrated into the skill's action phase, replacing the hardcoded prompt loading logic with a function call:

```python
# In skill execution phase
template = load_prompt_template(depth, compliance)
```

## Benefits

1. **Maintainability:** Prompt templates can be updated independently from SKILL.md logic
2. **Modularity:** Each depth level has its own template file
3. **Flexibility:** Easy to add new depth levels or compliance focuses
4. **Clarity:** Orchestration logic stays clean and readable
5. **Reusability:** Prompt loader can be used by other skills

## Template File Structure

Create corresponding template files in `references/prompts-for-depth-levels.md/`:

- `standard-review.md` - Standard security review prompts
- `compliance-nist-800-53-review.md` - NIST compliance focused
- `compliance-privacy-review.md` - Privacy and data protection focused
- `deep-review.md` - Comprehensive deep analysis prompts
