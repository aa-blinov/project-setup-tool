# Architecture

How `project-setup-tool` is put together.

## The shape

The tool is a flat set of modules at the root of the repository, with one
pipeline in the middle and two front ends around it. The window is PyQt5,
the terminal program is argparse, and neither of them holds any of the
work.

```
name + profile
    -> SetupService.run()
        -> project directory
        -> .venv                 (uv venv)
        -> .gitignore            (downloaded)
        -> git init
        -> ruff.toml
        -> the profile's files
        -> .vscode/settings.json
        -> uv pip install
        -> the editor
```

| Module | What it is responsible for |
| --- | --- |
| `app.py` | The PyQt5 window: the form, the profile drop-down, the output console, the progress bar, the dark palette. |
| `cli.py` | The argparse front end: `--list`, `--no-editor`, the positional `NAME` and `PROFILE`, and the ANSI colouring of the messages. |
| `setup_service.py` | The pipeline. Nine steps, no Qt import, and the only module that runs `uv`, `git` and `requests`. |
| `profiles.py` | `BaseProfile`, `ProfileContext`, the 20 profile classes and the `ALL_PROFILES` registry. |
| `generators.py` | The writers the profiles share: README, Dockerfile, compose file, requirements, ruff, VS Code settings. |
| `editor.py` | The editor search and the system file-explorer fallback. |
| `tests/` | The suite: five files over the profiles, the generators, the command line, the name validation and the subprocess calls. |

## The data flow

A run is a sequence of nine steps, and each one reports when it finishes.

```
name + profile index
  |  SetupService.run()
  v
a message and a progress value
  |  on_message(str), on_progress(int)
  v
the window's console, or the terminal's stdout
```

The pipeline owns the order. The front ends own the presentation. The
pipeline calls `advance()` after each step, which counts nine steps and
turns the count into a percentage, and it calls `check()` after each step
too, which raises `InterruptedError` when the cancel event is set.

The two front ends pass the same three things into the constructor: the
name, the index of the profile, and the callbacks. The window adds two
more: the base path from its output directory field, and the state of its
"Open in editor" box. The command line adds the state of `--no-editor`.

A profile receives a `ProfileContext` that carries the project name and the
`emit` callback, and writes its files. It does not run a command. Every
subprocess call in the tool lives in `setup_service.py` or `editor.py`.

## Decisions worth knowing about

### The pipeline does not import Qt

`setup_service.py` imports `requests`, `os`, `subprocess` and `threading`,
and nothing from PyQt5. The command line and the tests import it without
a display, and the pipeline is the unit both front ends share. A module
that needs Qt cannot be tested on a machine without one.

### The front ends are interchangeable, with one exception

Both front ends hand the same values to the same class. The exception is
the output directory: the window has a field for it and passes it in, and
the command line has no way to set it, so it always writes under
`BASE_PATH`. `BASE_PATH` itself is read when `setup_service` is imported,
which means changing the environment after the process has started does
nothing.

### The profile number is its position

A profile is addressed by its index in `ALL_PROFILES`, and the index is
also the number the command line accepts. Inserting a class in the middle
renumbers everything after it, in the drop-down, in `--list` and in the
help text. The registry at the bottom of `profiles.py` is the only place
the order is written down.

### A profile carries three things

A label, a slug and a list of dependencies, plus a `setup` method that
writes the files. The tests require the slug to be unique, lowercase, and
alphanumeric apart from hyphens. The dependencies are written into
`requirements.txt` together with `_BASE_TEST_DEPS`, the six test packages
that every generated project gets whether it needs them or not.

### The `.gitignore` comes over the network

The file is fetched from `raw.githubusercontent.com` with a 10 second
timeout, and a status other than 200 stops the run. The alternative, a
copy of the file in the repository, was not taken, and the tool has no
offline path.

### Failure is a message, not an exit code

`SetupService.run` catches every exception and turns it into a message.
The command line therefore exits 0 even when the pipeline failed, and the
window shows the same message in its console. The cost is that a script
cannot tell a failed run from a successful one by the exit status.

## Boundaries

- **`setup_service.py` does not import Qt.** The pipeline is the unit the
  command line, the window and the tests share.
- **Profiles write files and do not run commands.** Every subprocess call
  lives in `setup_service.py` and `editor.py`, and the test suite patches
  them there.
- **`generators.py` holds no state.** Its writers are plain functions that
  take a directory and write files, and the profiles use them.
- **`app.py` holds the presentation.** The window does not write a file,
  run a command or decide the order of the steps.
- **`cli.py` holds the presentation.** The terminal program parses
  arguments, resolves a profile and prints; it does not scaffold anything
  itself.
- **The profile list is written down once.** A new profile is a class and
  one line in `ALL_PROFILES`. The window and the command line read that
  list, so neither has to be touched.
