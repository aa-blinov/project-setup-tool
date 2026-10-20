---
name: project-setup-tool
description: A dark PyQt5 window over a terminal program. One palette, written out by hand in app.py, and the same three levels in the terminal.
colors:
  primary: "#2980b9"
  neutral-bg: "#263238"
  surface: "#212121"
  text: "#ffffff"
  muted: "#90a4ae"
  success: "#4caf50"
  danger: "#ff5252"
typography:
  body:
    fontFamily: "system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.4
  title:
    fontFamily: "system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "14px"
    fontWeight: 700
    lineHeight: 1.3
  code:
    fontFamily: "Consolas, Menlo, monospace"
    fontSize: "13px"
    lineHeight: 1.4
rounded:
  sm: "2px"
spacing:
  xs: "6px"
  sm: "8px"
  md: "16px"
---

# Design system: project-setup-tool

## Overview

**Creative North Star: "the workshop window"**

The tool has two faces and one idea behind them. The window is a workbench:
a form at the top, a console under it, a progress bar at the bottom, and
nothing else on screen. The terminal program is the same nine steps
printed one per line. Both are built from the same pipeline, and both say
the same thing when a step fails.

The visual identity is small and deliberate. There is no logo, no landing
page and no image in the repository. What there is, is a hand-written dark
palette in `app.py`, six colours, one accent, and a set of three levels
that every message in the tool carries: success, error and information.
The window colours those three levels. The terminal prints a glyph in
front of them and drops the colour when the output is not a terminal.

The three levels are the whole colour system. A message that is not one of
them is plain text, and it is the raw output of `uv` or `git`, passed
through untouched.

Key characteristics:

- One dark palette, written out in `app.py`, applied to the Fusion style.
- Three message levels, and the level is in the word: `SUCCESS:`, `ERROR:`,
  `INFO:`.
- No shadows, no gradients, no custom shapes. The widgets are the ones the
  platform draws.
- One monospace face, and only for the output console.

## Colors

### Window

The palette in `app.py`, applied with the Fusion style.

- **Blue grey** (`#263238`): the window background, the button faces and the
  alternating base. It is the ground the whole application sits on.
- **Ink** (`#212121`): the output console, the only recessed surface in the
  window.
- **White** (`#ffffff`): all text. The window text, the button text, the
  console text and the text on a highlighted row are all the same white.
- **Blue** (`#2980b9`): the accent, used for the link colour and the
  selection highlight. It is the only saturated colour that is not a level.
- **Red** (`#ff0000`): the `BrightText` role of the palette, which Qt uses
  for the text of a disabled or otherwise special item.

### Levels

The three levels, written in `OutputHighlighter._setup_formats`.

- **Green** (`#4caf50`): a step that succeeded. The line begins with
  `SUCCESS:`.
- **Red** (`#ff5252`): a step that failed. The line begins with `ERROR:`.
- **White** (`#ffffff`): a step that reported something. The line begins
  with `INFO:`.

### Terminal

The terminal front end uses ANSI codes instead of hex values, so the
colour follows the terminal's own palette.

- **Green** (code 32): a success.
- **Red** (code 31): an error.
- **Cyan** (code 36): information, and the profile slug in the list.
- **Yellow** (code 33): the profile number in the list.
- **Bold** (code 1): the heading, the prompts and the project name.
- **Dim** (code 2): the examples and the hints under the list.

### Rules

**The level is in the word.** Every line the pipeline emits begins with
`SUCCESS:`, `ERROR:` or `INFO:`, and the highlighter reads that prefix
rather than a separate field. A line that does not carry a level is raw
output from a subprocess and is printed in plain text.

**A level never changes meaning.** Green is a step that worked in the
window, in the terminal and in the highlighter, and there is no second
green for anything else.

**Colour is dropped when the output is not a terminal.** `cli.py` checks
`sys.stdout.isatty()` once at import and leaves the text alone when the
output is piped.

## Typography

**Display Font:** system-ui, the platform default
**Body Font:** system-ui, the platform default
**Code Font:** Consolas

The window uses the platform's own font through the Fusion style, and the
tool does not change it. The one exception is the output console, which is
set to Consolas at 13 pixels so that a stack trace lines up the way a
person expects it to.

The window title is the platform's own window title, and the section
labels inside the form ("Project Name:", "Project Type:", "Output Dir:")
are the platform's own. The profile hint under the drop-down is the only
widget with a font size of its own: 11 pixels, in the muted grey.

In the terminal there is no size to choose. The text is the terminal's, and
the tool uses bold, dim and color to mark the levels and nothing else.

## Layout

The window opens at 820 by 640 pixels and holds one vertical column.

```
Project Name:    [ my-awesome-project            ]
Project Type:    [ 1 — Basic Python Project  [basic] v ]
Output Dir:      [ ~/projects            ] [Browse…]
                 [x] Open in editor after creation
                 Minimal Python project — main.py, tests, ruff, .gitignore.
                 Packages: (only dev/test tools)

[Create Project] [Cancel]

Output:                                    [Clear]
┌──────────────────────────────────────────────┐
│ SUCCESS: Created project directory "...".     │
│ SUCCESS: Virtual environment created.        │
└──────────────────────────────────────────────┘
[████████████████████] 100%
```

The column has 8 pixels between its parts, and the form inside it has 6.
The `Browse` button is 80 pixels wide and the `Clear` button 55, so both
are sized by their labels rather than by the layout. The console takes
whatever height is left over, and the progress bar is the last row.

The terminal program prints the same information as a list of lines with
two spaces of indent, and the progress bar as 20 cells: a filled block for
every 5 percent and a light block for the rest.

The window asks the platform for Windows dark mode on every operating
system, by passing `-platform windows:darkmode=1` to the application. The
palette does not depend on the answer.

## Elevation & Depth

There is no elevation in this design. Nothing is lifted, nothing is
shadowed, and nothing overlaps. The window is one column of widgets, and
the only depth is the recessed console, which the platform draws with the
`Base` colour of the palette.

The rule the code follows is that the platform draws the parts and the
tool only chooses the colours. There is no stylesheet in the repository
apart from the one line that sets the hint label's colour and size, and
adding one would put the tool at the mercy of a widget style that is not
under its control.

## Shapes

The platform's own shapes. No radius is set on any widget, no border is
drawn, and the Fusion style's own frames are left alone. The two fixed
widths, 80 pixels for `Browse` and 55 for `Clear`, are the only shape
decisions in the window.

## Components

### The profile drop-down

- **Content:** one entry per profile, written as
  `{number} — {label}  [{slug}]`, so the number, the readable name and the
  slug the command line takes are all on the same line.
- **Order:** the order of `ALL_PROFILES`, which is also the number the
  command line takes.
- **Hint:** choosing a profile writes a line of description and the list of
  packages under the drop-down, in the muted grey.

### The profile hint

- **Style:** a label in `#90a4ae` at 11 pixels, with word wrap on, under
  the form.
- **Content:** the profile's description, then `Packages:` and the
  dependency list, or `(only dev/test tools)` when the profile has none.
- **Known drift:** several of the descriptions name packages the profile
  does not install. `AGENTS.md` records which ones.

### The output console

- **Shape:** a read-only `QTextEdit` with the platform's own frame and the
  console font.
- **Highlighting:** the first three characters of a line decide its
  colour. `ERROR` is red, `SUCCESS` is green, `INFO` is white. A line that
  starts with none of them keeps the default.
- **Behaviour:** the console scrolls to the bottom after every line, and
  the `Clear` button empties it.

### The progress bar

- **Shape:** the platform's `QProgressBar`, filled left to right.
- **Values:** the pipeline reports nine steps and turns them into
  percentages, so the bar reaches 100 at the end. `advance()` is called
  after the first eight steps, which means the bar reads 88 percent until
  the run ends.
- **In the terminal:** the same progress is printed as a 20-cell bar of
  filled and light blocks, with the percentage after it, rewritten in
  place with a carriage return.

### The buttons

- **Shape:** the platform's buttons, with the Fusion style.
- **Labels:** `Create Project`, `Cancel`, `Browse` and `Clear`. During a
  run the cancel button reads `Abort`, and the create button is disabled.
- **Behaviour:** the cancel button closes the window when nothing is
  running, and sets the cancel event when a run is.

## Do's and Don'ts

### Do:

- **Do** put the level in the text of the message. The highlighter reads
  the prefix, and the level survives when the colour does not.
- **Do** use the palette roles that Qt defines, and set the colours that
  the design needs in `apply_dark_theme`, rather than reaching for a
  stylesheet.
- **Do** keep the console in Consolas, so that the output of a command
  lines up.
- **Do** let the platform draw the widget frames and borders.

### Don't:

- **Don't** add a stylesheet. The platform's own style is what the tool
  inherits, and it changes with the operating system.
- **Don't** use a colour outside the palette. The accent is for the
  selection highlight, and the three level colours are for the three
  levels.
- **Don't** set a radius, a border or a shadow on a widget. The window has
  no shape of its own.
- **Don't** rely on the colour to carry a level. The colour is dropped when
  the output is piped, and the word is what is left.
- **Don't** add a level without adding its colour to the highlighter and
  its glyph to the terminal front end.
