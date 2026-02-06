# Contributing to Aftermath Skills

Thanks for your interest in contributing! This guide covers how to propose, create, and submit skills.

## Ways to Contribute

- **Improve an existing skill** — Fix inaccuracies, add missing endpoints, clarify instructions
- **Create a new skill** — Cover a new part of the Aftermath ecosystem
- **Report issues** — Found something wrong or confusing? Open an issue

## Creating a New Skill

### 1. Check for Duplicates

Search existing skills and open issues/PRs to make sure the skill doesn't already exist or isn't already in progress.

### 2. Skill Guidelines

A good skill should be:

- **Self-contained** — An agent should be able to use the skill without needing external docs. Include all necessary context, URLs, parameter schemas, and response shapes inline.
- **Actionable** — Focus on what the agent needs to *do*, not background theory. Lead with patterns, endpoints, and concrete examples.
- **Accurate** — Test every endpoint, code snippet, and example. Wrong information is worse than no information.
- **Concise** — Agents have context limits. Be thorough but not verbose. Prefer tables and structured formats over prose where possible.
- **Up to date** — Reference current API versions and behaviors. Note any deprecated or unstable features.

### 3. Directory Structure

Create a new directory under `skills/` with a descriptive, lowercase, hyphenated name:

```
skills/
└── your-skill-name/
    ├── aftermath-<skill-name>.md    # Required — the skill definition
    └── examples/                    # Optional — example code, configs, etc.
```

### 4. Test Your Skill

Before submitting, test the skill with at least one AI agent to verify it produces correct results. Include a brief summary of your testing in the PR description.

## Submitting Changes

### For Small Fixes

1. Fork the repo
2. Make your changes on a feature branch
3. Submit a pull request with a clear description of what changed and why

### For New Skills

1. Open an issue first to discuss the proposed skill — this avoids duplicate effort
2. Fork the repo and create a branch (e.g., `skill/typescript-sdk`)
3. Add your skill following the directory structure and template
4. Submit a pull request referencing the issue

### Pull Request Checklist

- [ ] Skill follows the [template](./templates/SKILL_TEMPLATE.md) structure
- [ ] All endpoints/examples have been tested and are accurate
- [ ] No sensitive information (API keys, internal URLs, etc.) is included
- [ ] Spelling and formatting are clean
- [ ] PR description includes a summary of testing performed

## Code of Conduct

Be respectful, constructive, and collaborative. We're all here to make the Aftermath developer experience better.

## Questions?

Open an issue or reach out to the Aftermath team on [Discord](https://discord.gg/aftermath).
