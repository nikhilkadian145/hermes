# HERMES SKILLS DIRECTORY

This folder contains the authoritative source of truth for all 22 HERMES LLM Skills.

## Multi-Tenant Skill Routing (Phase 11.4)
Because HERMES is a multi-tenant application where every client might have their own isolated `workspace` folder containing distinct SQLite databases and `MEMORY.md` states, we manage the skills universally via **Symlinks**.

Instead of copying these 22 folders 100 times for 100 different clients, you should execute:
```bash
ln -s /path/to/hermes/hermes-skills /path/to/hermes/customers/c001/workspace/skills
```
*(On Windows, use `New-Item -ItemType SymbolicLink -Path "workspace\skills" -Target "hermes-skills"`)*

### Why Symlinks?
- Whenever you `git pull` new logic for a skill (e.g., teaching HERMES a new GST rule in `report-gst`), **all** customers receive the updated prompt instructions instantly on the next bot interaction without running massive migration scripts.
- The `nanobot` agent natively traverses symlinks when executing its `read_file` tool and constructing its system prompt.
