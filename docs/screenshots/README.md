# Screenshots

`project-setup-tool` has no screenshots in this folder, and there are no
images anywhere in the repository.

The window is 820 by 640 pixels of plain widgets, and its appearance is
set by a palette written out in `app.py` and by the platform's own Fusion
style. A picture of it would show the widget style of one operating system
and one Qt version rather than the tool, and the tool renders differently
on every platform it runs on.

What the repository carries instead:

- The design record in the [DESIGN.md](../../DESIGN.md), which gives the
  palette, the levels, the layout of the window and the rules the widgets
  follow.
- The profile table in the [README](../../README.md), where each of the 20
  profiles is listed with its slug and its dependencies.

If a screenshot is added later, it goes in this folder and is referenced
from the README by a relative path, so it resolves on GitHub and in a
local checkout. The house-style checker verifies that every image reference
points at a file that exists, so a renamed screenshot cannot quietly break
the README.
