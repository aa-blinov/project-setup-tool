# AGENTS.md — agent context for `project-setup-tool`

A Python tool that scaffolds a new Python project from one of 20 profiles: a directory, a uv virtual environment, a Git repository, ruff, VS Code settings, a Dockerfile and the dependencies installed. It ships as a PyQt5 window (`pst`) and as a command line program (`pst-cli`), and both drive the same pipeline in `setup_service.py`.

This file is what a session needs to work on the project without reading all of it.

## Run / build / test

```bash
uv sync                  # install
uv run --dev pytest -v   # run the tests, 129 of them
uv run pst               # run the window
uv run pst-cli --list    # list the profiles
uv run pst-cli my-api fastapi --no-editor   # scaffold one project
```

Python 3.10 or newer. There is no build step: `pyproject.toml` uses setuptools, and `pst` and `pst-cli` come from `[project.scripts]`.

## Where things live

| Path | What it holds |
| --- | --- |
| `app.py` | The PyQt5 window: the form, the profile drop-down, the output console, the progress bar. |
| `cli.py` | The argparse front end: `--list`, `--no-editor`, and the positional `NAME` and `PROFILE`. |
| `setup_service.py` | The pipeline. Nine steps, no Qt import, and the only module that runs `uv`, `git` and `requests`. |
| `profiles.py` | The 20 profile classes, `BaseProfile`, `ProfileContext` and the `ALL_PROFILES` list. |
| `generators.py` | The writers the profiles share: README, Dockerfile, compose file, requirements, ruff, VS Code. |
| `editor.py` | The editor search and the file explorer fallback. |
| `tests/` | 129 tests over the profiles, the generators, the CLI and the subprocess calls. |
| `run.sh`, `run.bat` | Launchers that call `uv run pst`. |
| `.github/workflows/ci.yml` | The CI: install uv, run `uv run --dev pytest -v`. |

## Traps

- **The `PyQt5-Qt5==5.15.2` pin blocks Apple Silicon.** `pyproject.toml` sets
  `override-dependencies = ["PyQt5-Qt5==5.15.2"]`, and that version has no
  wheel for macOS arm64, so `uv sync` fails on a Mac with an Apple chip. The
  pin is there for Windows. Dropping it, and dropping `uv.lock`, is what makes
  the suite installable on an Apple Silicon Mac. The CI runs on ubuntu-latest
  and is unaffected.
- **`run.sh` and `run.bat` document flags that do not exist.** They show
  `uv run pst-cli --name my-project --profile fastapi --dir ~/projects`. The
  name and the profile are positional arguments, there is no `--dir`, and
  argparse refuses the other two.
- **A failed run leaves the directory behind.** The project directory is
  created first, and nothing removes it when a later step fails, so the next
  run stops with `Project directory "..." already exists`.
- **The command line exits 0 when the setup failed.** `SetupService.run`
  catches every exception and turns it into a message, so a shell sees no
  failure. The window shows the same message in its output console.
- **The abort button stops between steps.** The cancel event is checked after
  each step, so a long `uv pip install` runs to the end before the run stops.
- **The hints in `app.py` do not match the profiles.** The `_HINTS` dictionary
  names packages that several profiles do not install: Click for the `cli`
  profile, which installs typer; python-telegram-bot for `telegram`, which
  installs aiogram; requests and Playwright for `scraper`, which installs
  httpx and lxml; seaborn for `data`; torch for `ml`. The hint is the first
  thing a reader of the window sees for that profile.
- **The progress bar counts eight of the nine steps.** `advance()` runs after
  each of the first eight, so the bar reads 88% until the run ends and jumps
  to 100.
- **A profile number is its position in `ALL_PROFILES`.** Inserting a class in
  the middle renumbers everything after it, and `pst-cli`, `--list` and the
  drop-down all read from that list.
- **The two `_write` helpers are copies.** `generators.py` and `profiles.py`
  each have one, and the profiles use theirs, so a change to the generator's
  version does not reach the profiles.
- **The base path is read at import.** `PROJECT_BASE_PATH` is read when
  `setup_service` is imported, so changing it after the process has started
  does nothing. The window's output directory field overrides it. The command
  line has no way to change it, and always writes under the base path rather
  than in the current directory.
- **Every generated project gets the six test packages.** `requirements.txt` is
  the profile's dependencies plus `_BASE_TEST_DEPS`, whether the profile needs
  them or not.
- **The `.gitignore` needs the network.** It comes from
  `raw.githubusercontent.com/github/gitignore/main/Python.gitignore` with a 10
  second timeout, and a status other than 200 stops the run.
- **The window asks for Windows dark mode on every platform.** `main()` builds
  the application with `sys.argv + ["-platform", "windows:darkmode=1"]`, so the
  request is made on macOS and Linux as well.
- **The tests build a real Qt application.** `tests/conftest.py` creates a
  `QApplication` and a `ProjectSetupApp` widget, so the suite needs a working
  Qt platform plugin. On a machine without a display, set
  `QT_QPA_PLATFORM=offscreen`.

## Style / safety rails

- **Keep `setup_service.py` free of Qt.** The command line and the tests
  import it without a display, and the pipeline is the unit both front ends
  share.
- **Profiles write files, they do not run commands.** Every subprocess call
  lives in `setup_service.py`, and `tests/test_subprocess_calls.py` patches
  them there.
- **A profile carries a label, a slug and a list of dependencies.** The tests
  require the slug to be unique, lowercase, and alphanumeric apart from
  hyphens.
- **Comments explain why, never what.**
- **No emoji in any file.** `profiles.py` still writes one into the Streamlit
  title, on line 1098, and the house check fails on it.

## Where the product truth lives

`PRODUCT.md` holds it. Read it before changing what the tool produces, and
write the change there when the behaviour changes.
