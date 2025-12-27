# Telco Agent Skills

Telco Agent Skills are folders of instructions, scripts, and resources that AI agents can discover and use to perform specific tasks related to the Telecommunications industry. This repository provides a catalog of skills tailored for Telco use cases, enabling agents to interact with standardized APIs and systems.

## What Are Skills?

Skills are folders of instructions, scripts, and resources that AI agents can discover and use to perform specific tasks. Skills teach agents how to complete specialized tasks in a repeatable way, whether that's creating TMF-compliant APIs, analyzing telecommunications data using standardized workflows, or automating Telco-specific processes.

Each skill is designed to be a self-contained unit that an AI agent can use. The `SKILL.md` file within each skill's directory provides a detailed description of the skill's capabilities, expected inputs, and operational workflow. The goal is to create a standardized approach for building and using Telco-related skills.

For more information about the Agent Skills standard, see [agentskills.io](https://agentskills.io).

## Skill Structure

Each skill follows a standardized structure:

### SKILL.md Format

Every skill must contain a `SKILL.md` file with YAML frontmatter and markdown instructions:

```markdown
---
name: skill-name
description: A clear description of what this skill does and when to use it
---

# Skill Name

[Instructions, examples, and guidelines that the agent will follow]
```

**Required frontmatter fields:**
- `name` - A unique identifier for your skill (lowercase, hyphens for spaces)
- `description` - A complete description of what the skill does and when to use it

The markdown content below the frontmatter contains the instructions, examples, and guidelines that agents will follow when using the skill.

### Example

A key example is the `tmf-mcp-builder` skill, which demonstrates how to build TM Forum (TMF) compliant Management Component Protocol (MCP) servers from TMF OpenAPI specifications.

## Installing a Skill

### For OpenAI Codex

1. Go to the project where you want to install the skill
2. Launch codex:
   ```bash
   > codex
   ```
3. Use skill-installer to install skills:
   ```bash
   $skill-installer install "GitHub directory URL for the skill"
   ```

For example, the following command will install the tmf-mcp-builder skill:
```bash
$skill-installer install https://github.com/oopsyz/skills/tree/main/tmf-mcp-builder
```

## Creating a Skill

Creating a skill is simple - just create a folder with a `SKILL.md` file containing YAML frontmatter and instructions. Here's a basic template:

```markdown
---
name: my-telco-skill
description: A clear description of what this skill does and when to use it
---

# My Telco Skill

[Add your instructions here that the agent will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

The frontmatter requires only two fields:
- `name` - A unique identifier for your skill (lowercase, hyphens for spaces)
- `description` - A complete description of what the skill does and when to use it

The markdown content below contains the instructions, examples, and guidelines that agents will follow. For more details, see [How to create custom skills](https://agentskills.io).

## Available Skills

*   **tmf-mcp-builder**: A skill for building TM Forum (TMF) MCP servers from TMF OpenAPI specs.

## License

The license for an individual skill can be found in the `LICENSE.txt` file within the skill's directory.

## About

This repository is a catalog of Telco-focused skills for AI agents. These skills enable agents to interact with standardized telecommunications APIs and systems, following industry standards like TM Forum (TMF) specifications.

Skills in this repository are designed to be:
- **Self-contained**: Each skill includes all necessary instructions and resources
- **Standardized**: Following the Agent Skills specification for consistency
- **Telco-focused**: Tailored for telecommunications industry use cases
- **Reusable**: Can be installed and used across different projects and agents

## References

- [Agent Skills Specification](https://agentskills.io) - The official standard for Agent Skills
- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Reference implementation and examples
- [TM Forum](https://www.tmforum.org/) - Telecommunications industry standards
