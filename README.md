# Citera

Citera is a zero-friction CLI that helps you create, promote, and organize code projects with AI-assisted metadata. It is built to keep experiments tidy, promote promising work into structured products, and automate the boring bits (naming, metadata, README generation, git setup, GitHub creation).

## Overview

Citera manages projects by maturity stage and category:

- playground: fast experiments
- incubator: promising work-in-progress
- products: versioned, long-term projects
- tools: reusable utilities
- archives: frozen/deprecated work

When a project is promoted from playground to incubator, Citera triggers AI metadata generation to categorize, rename, and document the project automatically.

## Features

- Create new projects in seconds
- Promote projects to higher maturity stages
- AI-generated metadata (name, description, tags, tech, category)
- Category-based structure (e.g., incubator/AI/project-name)
- README generation on promotion
- Git initialization and GitHub repo creation (default on promote)
- Obsidian note generation (optional)

## Requirements

- Python 3.9+
- A virtual environment is recommended (PEP 668 blocks system installs on Ubuntu)
- Git (for repo initialization)
- GitHub CLI (gh) if you want automatic GitHub repo creation
- AI SDKs are installed by default (openai, google-genai)

## Installation

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Install Globally (no venv)

Recommended with pipx:

```bash
sudo apt install pipx
pipx ensurepath
pipx install -e /path/to/citera
```

User install with pip:

```bash
python3 -m pip install --user -e /path/to/citera
```

Notes:
- If you install with `-e`, code changes take effect immediately; reinstall only when dependencies change.
- If `citera` is not found, ensure `~/.local/bin` is on your PATH.

## Configuration

Config file:

```
~/.config/citera/config.yaml
```

Set provider and key:

```bash
citera set llm openai
citera set llm_key sk-your-key
```

Or for Gemini:

```bash
citera set llm gemini
citera set llm_key ya29.your-gemini-key
```

Optional model override:

```bash
citera set llm_model gpt-4o-mini
citera set llm_model gemini-2.5-flash
```

Projects root can be set via config:

```bash
citera set root ~/Documents/Projects
```

If not set, Citera will use this environment variable if present:

```bash
export PROJECTS_DIRECTORY=~/Documents/Projects
```

If not set, Citera defaults to:

```
~/Documents/Projects/
```

Stage names and folders can be customized via `.env`:

```bash
# ~/.config/citera/.env or .env in your working directory
CITERA_STAGE_PLAYGROUND=sandbox
CITERA_STAGE_DIR_PLAYGROUND="1- Sandbox"
CITERA_STAGE_INCUBATOR=develop
CITERA_STAGE_DIR_INCUBATOR="2- Develop"
CITERA_STAGE_PRODUCT=product
CITERA_STAGE_DIR_PRODUCT="3- Products"
CITERA_STAGE_TOOL=tool
CITERA_STAGE_DIR_TOOL="4- Tools"
CITERA_STAGE_ARCHIVE=archived
CITERA_STAGE_DIR_ARCHIVE="9- Archived"
```

## Project Structure

Citera creates and manages this structure automatically (defaults shown):

```
~/Documents/Projects/
├── playground/
├── incubator/
│   └── AI/
│       └── my-project
├── products/
│   └── CLIs/
│       └── another-project
├── tools/
├── archives/
```

## Core Commands

### 1) Create a project

```bash
citera new --type playground
```

Flags:
- --type playground|incubator|product|tool (default: playground; configurable via .env)
- --lang python|js|rust (optional starter file)
- --name CustomId1234 (optional)

### 2) Describe a project (AI metadata)

```bash
citera describe
```

Flags:
- --path /path/to/project (default: current directory)
- --force (overwrite existing metadata fields)
- --dry-run (print metadata only, do not write)

### 3) Promote a project

```bash
citera promote
citera promote --stage incubator
citera promote --stage archived
```

Flags:
- --stage incubator|product|tool|archived (configurable via .env; defaults to next stage)
- --archive (moves project to archives, prompts for confirmation)
- --name "override-name" (overrides AI name)
- --no-github (skip GitHub repo creation)
- --git (force git init even without GitHub)
- --obsidian (create an Obsidian note)
- --dry-run (show actions without changes)
- --path /path/to/project (optional)
- --id ProjectId1234 (optional)

Promotion behavior:
- playground -> incubator triggers AI metadata generation
- incubator -> product/tool requires existing metadata
- README.md is created if missing (using AI description)
- Initial commit is created and pushed when GitHub is enabled

### 4) Set config values

```bash
citera set llm openai
citera set llm_key sk-your-key
citera set llm_model gpt-4o-mini
citera set root ~/Documents/Projects
```

Valid keys:
- llm (openai|gemini)
- llm_key
- llm_model
- root

### 5) List (stub) and archive

```bash
citera list
citera archive --id ProjectId1234
citera archive
```

Archive commands will prompt for confirmation before moving a project.

## Recommended Usage Order

1. Configure AI provider and key:
   - citera set llm openai|gemini
   - citera set llm_key <your-key>
2. Create a project:
   - citera new
3. Work in the project.
4. Promote when ready:
   - citera promote --stage incubator --id <project-id>
5. Optionally describe or re-describe:
   - citera describe --force

## Debugging and Troubleshooting

- Use --dry-run on promote/describe to see actions without changes.
- If GitHub creation fails:
  - Ensure gh is installed and authenticated: gh auth login
  - Use --no-github to skip GitHub creation
- If git commit fails:
  - Configure git user: git config --global user.name "You" and user.email
- If AI fails or returns invalid JSON:
  - Re-run with --dry-run to inspect response
  - Verify llm and llm_key in config

## Roadmap

- Real AI metadata providers (OpenAI/Gemini) with better prompt tuning
- Describe command improvements (more context signals, better summaries)
- Full list/archive/promote workflows
- GitHub issues + labels auto-generation
- Obsidian templates and vault integration
- Project templates per language or framework
- CI setup automation

## License

MIT
