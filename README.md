# project_manager

**A zero-friction CLI tool to capture, evolve, and document your code projects — powered by AI and built for VS Code.**

---

## ✨ Why project_manager?

- Create new projects instantly — no naming, no setup
- Promote experiments into real projects with one command
- Let AI generate names, tags, descriptions, README, and commit messages
- Keep everything organized by intent (playground → incubator → product/tool)
- Optional GitHub and Obsidian integration

---

## 🛠️ Features

- `project_manager new` — Start coding in <5 seconds
- `project_manager promote` — Upgrade projects to serious mode
- `project_manager describe` — Generate structured metadata using AI
- `project_manager list` — Browse by stage or tag
- `project_manager archive` — Clean up deprecated ideas

---

## 🧠 Philosophy

Organize by **maturity**, not mess.

```
~/Projects/
├── playground/     # throwaway experiments
├── incubator/      # promising WIPs
├── products/       # real, versioned software
├── tools/          # reusable scripts/utilities
├── archives/       # frozen or deprecated
└── _meta/          # Obsidian vault, templates, etc.

````

---

## 🚀 Getting Started

Install:

```bash
pip install project_manager
````

Start a new project:

```bash
project_manager new --type playground
```

Then just open it in VS Code and go.

---

## ⚙️ Configuration

Default config file:

```bash
~/.config/project_manager/config.yaml
```

Example:

```yaml
projects_root: ~/Projects
default_stage: playground
obsidian_enabled: true
llm_provider: openai
github_visibility: private
```

---

## 🤖 AI Metadata

AI generates:

* Project name (kebab-case)
* Description (1 paragraph)
* Tags (3–6)
* Tech stack
* README content
* Git commit messages

All saved to `project.yaml`.

---

## 🧩 Integrations

* **GitHub**: `--git`, `--github` flags use `gh` CLI
* **Obsidian**: Notes auto-generated into your vault with YAML frontmatter

---

## 📅 Roadmap

See [PROJECT_MANAGER_PRD.md](./PROJECT_MANAGER_PRD.md) for full development plan.

---

## 🙌 License

MIT

---

Built for myself. Designed for every dev who codes fast and forgets less.
