# Product

<!-- impeccable:product-schema 1 -->

## Platform

desktop

The tool is a Python program that runs on the machine of the person using it. The interface is a PyQt5 window, 820 by 640 pixels at startup, and a terminal program. The pipeline shells out to `uv`, `git` and `requests`, so the machine needs Python 3.10 or newer, uv, Git, and a network connection to `raw.githubusercontent.com`.

## Users

The person the code is written for is a Python developer at the start of a project. They know which kind of project they are building, a FastAPI service, a Discord bot, a pytest plugin, and they want the surroundings done so that the first file they write is the file that is theirs.

Nothing beyond that is confirmed. The repository has no description on GitHub, one star, no forks and one open issue: the adoption of the house standard. There is no usage data of any kind, so the people who use the tool beyond its author are unknown.

## Product Purpose

The product turns a name and a profile into a directory that runs.

A generated project is not a set of files. It has a `.venv` with the dependencies already installed, a Git repository with a Python `.gitignore`, a ruff configuration that the editor reads, VS Code settings that point at the interpreter, a Dockerfile, a compose file, and a README that says how to start it. The nine steps of the pipeline are the product, and the 20 profiles are 20 answers to the question of what is being built.

Success for the user: the first command in the new project runs, and nothing has to be installed by hand. Success for the product: a new kind of project is a new class and one line in a list, and the window and the command line stay interchangeable.

## Positioning

A generic scaffolder writes the layout and stops. The other half of this tool is the part that makes the layout usable: the environment, the linter configuration, the editor settings and the dependency install, all done by the command that writes the files.

The second difference is the profiles. They are not empty directories with a name on them. The `fastapi-db` profile writes an Alembic environment and a router; the `discord` profile writes a Cog and the extension load that goes with it; the `lambda` profile writes a SAM template and a Makefile; the `pytest-plugin` profile writes a `pytest11` entry point. Copying the tool means copying the templates.

What cannot be claimed from this repository: there is no comparison with cookiecutter, Copier or any other scaffolder, and no measurement of how long the pipeline takes on any machine. The difference described above is a judgement about what the code does.

## Operating Context

The person is at the start of something, and the project does not exist yet. The tool is a one-shot run and not a service: it is started, it writes a directory, it opens an editor, it ends.

The new project lands under `~/projects` unless `PROJECT_BASE_PATH` says otherwise, or unless the directory field in the window says otherwise. The window is the mode for a person who wants to see the profiles and their packages before committing to one. The command line is the mode for a person who already knows, and its arguments can be scripted: `uv run pst-cli my-api fastapi` is the whole flow in one line.

The machine carries uv, Git and a network connection. The editor is optional, and without one the finished folder opens in the system file explorer. The window runs the pipeline on a background thread, so it stays responsive, and the run can be aborted between steps.

## Capabilities and Constraints

Confirmed by the code:

- 20 profiles, each with a label, a slug, a list of dependencies and a `setup` method that writes the files.
- The pipeline creates the directory, the `.venv` with `uv venv`, the `.gitignore`, the Git repository, `ruff.toml`, the files of the profile, `.vscode/settings.json`, the dependencies with `uv pip install`, and then the editor. Nine steps, reported as they finish.
- Every generated project carries the six test packages in `requirements.txt`, whether the profile needs them or not.
- The window has a profile drop-down with the packages under it, an output directory picker, an output console with the levels coloured, a progress bar, and a button that aborts the run.
- The command line runs interactively or takes the name and the profile as arguments, and it has `--list` and `--no-editor`. The profile is a slug or a number from 1 to 20.
- A project name is refused when it holds `\ / : * ? " < > |` or `..`.
- The editor search tries `code`, `code-insiders`, `cursor`, `windsurf`, `codium` and `code-oss`, then the path in `VSCODE_PATH`, and falls back to the file explorer.
- The `data` profile is the only one whose Dockerfile runs on `jupyter/base-notebook:python-3.11.6`; the others run on `python:3.12-slim`, and the `pypi` and `pytest-plugin` profiles write no Dockerfile at all.

Deliberately not true, and worth knowing before a change:

- The tool is not published. There is no release workflow, no PyPI package and no install line that does not go through the repository.
- The command line always exits 0, even when the pipeline failed.
- The pipeline needs the network for the `.gitignore`, and there is no offline path.
- The generated projects are templates. Nothing here runs them, imports what they write, or keeps them in step with a release of the libraries they name.
- The two front ends are not equivalent in one respect: the window can change the output directory, and the command line cannot.

Open questions, for the owner to answer rather than for a later session to guess:

- Should the pipeline remove a half-created directory when a step fails, so that a retry works?
- Should the command line exit non-zero when the pipeline failed?
- Should the base path be settable from the command line?
- The `_HINTS` text in `app.py` names packages that several profiles do not install. Which of the two is the truth?

## Brand Commitments

**Name:** Project Setup Tool. The package is `project-setup-tool`, the commands are `pst` and `pst-cli`.

**Tone:** plain and technical. The tool reports what it did in one line per step, with the level carried in the word: `SUCCESS:`, `ERROR:`, `INFO:`. The window colours the three levels in the console, and the terminal prints a check mark, a cross or a middle dot in front of them, dropping the colour when the output is not a terminal.

The window is dark: the Fusion style and a dark palette written out in `app.py`, with a blue accent and the console set in Consolas.

There is no logo, no landing page and no screenshot in this repository. The name is a description rather than a brand, and it should keep working as one.

## Evidence on Hand

- `README.md` describes the profiles, the commands and the environment variable.
- `profiles.py` holds the 20 profiles and the files each of them writes.
- `setup_service.py` holds the nine steps, the 10 second timeout on the `.gitignore` download, and the rules for the created directory.
- `generators.py` holds the shared writers, and `editor.py` holds the editor candidates and the fallback.
- `tests/` holds 129 tests: 50 for the second batch of profiles, 21 for the generators, 17 for the command line, 17 for the name validation, 14 for the first three profiles and 10 for the subprocess calls. They check which files exist and which strings they hold.
- `.github/workflows/ci.yml` runs `uv run --dev pytest -v` on ubuntu-latest, for pushes to `master` and for pull requests. The last run on `master` passed.
- The repository on GitHub: one star, no forks, no description and no tags.

Absent, and not to be invented: no download counts, no usage numbers, no testimonials, no screenshots of the window, and no comparison with any other scaffolder. The tool has never been released, so there is nothing to count.

## Product Principles

1. **The result runs.** A generated project has its dependencies installed and its interpreter configured before the tool reports that it is done.
2. **One pipeline, two front ends.** The window and the command line do the same work, and the pipeline holds the logic they share.
3. **A failure is a message.** Every step says what happened, in words that carry their level, and no step is reported as done when it has failed.
4. **Profiles are where the work happens.** A new kind of project is a new class and one line in `ALL_PROFILES`, and nothing else in the tool has to move.

## Accessibility & Inclusion

- **The command line carries the whole tool.** Everything the window does has a command line form, so the tool works without a mouse, and the messages stay plain when the output is piped.
- **The state is in the words.** Each step carries its level in the text, so the console reads without colour, in the window and in the terminal alike.
- **The window is a plain widget set.** The profile chooser is a combo box and the directory chooser is the native dialog, and no custom key handling is registered, so the platform's own keyboard behaviour is what the window has.
- **A contrast standard has not been set.** The window uses a hand-written dark palette in `app.py`, and nobody has checked the text against the surfaces.
- **The people who use it are not known.** The repository carries no description and no usage data, so nothing is claimed here about who the tool does and does not serve.
