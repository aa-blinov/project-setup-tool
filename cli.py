"""Command-line interface for Project Setup Tool.

Usage
-----
Interactive mode (prompts for name and profile):
    uv run pst-cli

Non-interactive, profile by slug:
    uv run pst-cli my-api fastapi
    uv run pst-cli my-bot telegram
    uv run pst-cli ml-exp  ml

Non-interactive, profile by number (1-based):
    uv run pst-cli my-api 3

List available profiles:
    uv run pst-cli --list
"""

from __future__ import annotations

import argparse
import re
import sys
import threading

from profiles import ALL_PROFILES
from setup_service import SetupService

_INVALID_NAME_RE = re.compile(r'[\\/:*?"<>|]')

# ── ANSI colour helpers ────────────────────────────────────────────────────────
_USE_COLOUR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text


def _ok(msg: str) -> str:
    return _c("32", msg)


def _err(msg: str) -> str:
    return _c("31", msg)


def _info(msg: str) -> str:
    return _c("36", msg)


def _bold(msg: str) -> str:
    return _c("1", msg)


def _dim(msg: str) -> str:
    return _c("2", msg)


# ── Profile lookup ─────────────────────────────────────────────────────────────

_SLUG_MAP: dict[str, int] = {p.slug: i for i, p in enumerate(ALL_PROFILES)}


def _resolve_profile(value: str) -> int | None:
    """Return 0-based index from a slug or 1-based number string, or None."""
    if value.isdigit():
        n = int(value)
        if 1 <= n <= len(ALL_PROFILES):
            return n - 1
        return None
    return _SLUG_MAP.get(value.lower())


def _list_profiles() -> None:
    slugs = [p.slug for p in ALL_PROFILES]
    max_slug = max(len(s) for s in slugs)
    print(_bold("Available profiles:\n"))
    for i, p in enumerate(ALL_PROFILES, 1):
        num = _c("33", f"{i:>2}")
        slug = _c("36", p.slug.ljust(max_slug))
        print(f"  {num}  {slug}  {p.label}")
    print()
    print(_dim("  Use the slug or number as the second argument:"))
    print(_dim("    uv run pst-cli my-api fastapi"))
    print(_dim("    uv run pst-cli my-bot telegram"))


# ── Validation ─────────────────────────────────────────────────────────────────


def _validate_name(name: str) -> str | None:
    if not name:
        return "Project name cannot be empty."
    if _INVALID_NAME_RE.search(name) or ".." in name:
        return 'Project name contains invalid characters (\\/:*?"<>| or ..).'
    return None


# ── Interactive prompts ────────────────────────────────────────────────────────


def _prompt_name() -> str:
    while True:
        try:
            name = input(_bold("  Project name: ")).strip()
        except EOFError:
            sys.exit(0)
        msg = _validate_name(name)
        if msg:
            print(_err(f"  ✗ {msg}"))
        else:
            return name


def _prompt_profile() -> int:
    print()
    _list_profiles()
    print()
    while True:
        try:
            raw = input(
                _bold(f"  Profile (slug or 1-{len(ALL_PROFILES)}, default basic): ")
            ).strip()
        except EOFError:
            sys.exit(0)
        if not raw:
            return 0
        idx = _resolve_profile(raw)
        if idx is not None:
            return idx
        print(
            _err(f"  ✗ Unknown profile. Enter a slug or number 1-{len(ALL_PROFILES)}.")
        )


# ── Output callbacks ───────────────────────────────────────────────────────────


def _on_message(msg: str) -> None:
    if msg.startswith("SUCCESS:"):
        print(_ok(f"  ✓ {msg.removeprefix('SUCCESS:').strip()}"))
    elif msg.startswith("ERROR:"):
        print(_err(f"  ✗ {msg.removeprefix('ERROR:').strip()}"))
    elif msg.startswith("INFO:"):
        print(_info(f"  · {msg.removeprefix('INFO:').strip()}"))
    else:
        print(f"    {msg}")


def _on_progress(value: int) -> None:
    filled = value // 5
    bar = "█" * filled + "░" * (20 - filled)
    end = "\n" if value >= 100 else "\r"
    print(f"  [{bar}] {value:3d}%", end=end, flush=True)


# ── Argument parser ────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    slugs = ", ".join(p.slug for p in ALL_PROFILES)
    parser = argparse.ArgumentParser(
        prog="pst-cli",
        description=(
            "Project Setup Tool — bootstrap a new Python project in seconds.\n\n"
            "Run without arguments to enter interactive mode."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "profiles:\n"
            f"  {slugs}\n"
            "\n"
            "examples:\n"
            "  uv run pst-cli                         interactive mode\n"
            "  uv run pst-cli --list                  show all profiles\n"
            "  uv run pst-cli my-project              basic python project (default)\n"
            "  uv run pst-cli my-api fastapi          FastAPI project\n"
            "  uv run pst-cli my-bot telegram         Telegram bot\n"
            "  uv run pst-cli ml-exp ml --no-editor   ML project, skip editor\n"
            "  uv run pst-cli my-api 3                profile by number also works"
        ),
    )
    parser.add_argument("name", nargs="?", metavar="NAME", help="Project name.")
    parser.add_argument(
        "profile",
        nargs="?",
        metavar="PROFILE",
        help="Profile slug or number (default: basic).",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all available profiles and exit.",
    )
    parser.add_argument(
        "--no-editor",
        action="store_true",
        help="Skip opening the project in an editor.",
    )
    return parser


# ── Entry point ────────────────────────────────────────────────────────────────


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.list:
        _list_profiles()
        return

    interactive = args.name is None

    # ── Resolve name ──────────────────────────────────────────────────
    if interactive:
        print(_bold("\n  Project Setup Tool") + _dim("  (Ctrl-C to quit)\n"))
        name = _prompt_name()
    else:
        err = _validate_name(args.name)
        if err:
            parser.error(err)
        name = args.name

    # ── Resolve profile ───────────────────────────────────────────────
    if args.profile is not None:
        profile_index = _resolve_profile(args.profile)
        if profile_index is None:
            slugs = ", ".join(p.slug for p in ALL_PROFILES)
            parser.error(f"Unknown profile '{args.profile}'. Valid slugs: {slugs}")
    elif interactive:
        profile_index = _prompt_profile()
    else:
        profile_index = 0  # default: basic

    profile_label = ALL_PROFILES[profile_index].label
    print(f"\n  {_bold(name)}  {_dim('·')}  {profile_label}\n")

    # ── Run ───────────────────────────────────────────────────────────
    try:
        service = SetupService(
            project_name=name,
            profile_index=profile_index,
            on_message=_on_message,
            on_progress=_on_progress,
            cancel_event=threading.Event(),
            open_editor=not args.no_editor,
        )
        service.run()
    except KeyboardInterrupt:
        print(_info("\n  · Cancelled."))


if __name__ == "__main__":
    main()
