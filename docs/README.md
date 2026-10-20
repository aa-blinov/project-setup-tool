# Documentation

The documents of `project-setup-tool`, a Python tool that scaffolds a new
project from one of 20 profiles: a directory, a uv virtual environment, a
Git repository, ruff, VS Code settings, a Dockerfile and the dependencies
installed.

| Document | What it covers |
| --- | --- |
| [architecture.md](architecture.md) | The pipeline, the two front ends, the profiles and the boundaries between them. |
| [screenshots/README.md](screenshots/README.md) | Whether the repository carries images, and which ones. |
| [../README.md](../README.md) | The front door: the 20 profiles, the commands and the environment variables. |
| [../AGENTS.md](../AGENTS.md) | The traps, the commands and the rules of the project. |
| [../PRODUCT.md](../PRODUCT.md) | The product truth: who it is for, and what it promises. |
| [../DESIGN.md](../DESIGN.md) | The dark palette, the type and the widgets of the window. |

This folder holds documents only. The tool has no landing page and no
website, because the tool runs on the machine of the person using it and
there is nothing to serve.

## Reading order

New here: [../README.md](../README.md), then
[architecture.md](architecture.md). The README has the profile table, and
the profile table is the tool.

Changing the code: [architecture.md](architecture.md) first, to see which
module owns what, then [../AGENTS.md](../AGENTS.md) for the traps. The list
of traps matters most here: several of them describe behaviour that looks
like a bug and is a decision.

Looking for the reason a change was made: [../PRODUCT.md](../PRODUCT.md).
