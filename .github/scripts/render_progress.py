"""Render learning progress bars into README.md from progress.json.

Reads skills (and research directions) from progress.json, rebuilds the
terminal code block (the first fenced block in README.md), and writes it back.
Triggered by GitHub Actions on progress.json changes, or run locally.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

TEMPLATE = """$ whoami
Modusensus — urban planning · public management
exploring where cities meet data, code & AI

$ date --born
2004-09-20

$ echo $STACK
{stack}

{research}$ progress
{bars}
"""


def render_bar(name: str, percent: int) -> str:
    filled = round(percent / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"{name:<10} {bar} {percent:>3}%"


def render_research(items: list[str]) -> str:
    """Research directions have no end point, so they get no progress bar."""
    if not items:
        return ""
    return "$ research\n" + "\n".join(items) + "\n\n"


def build_terminal() -> str:
    data = json.loads((ROOT / "progress.json").read_text(encoding="utf-8"))
    stack = " · ".join(data.get("stack", []))
    research = render_research(data.get("research", []))
    in_progress = [s for s in data["skills"] if int(s["percent"]) < 100]
    bars = "\n".join(render_bar(s["name"], int(s["percent"])) for s in in_progress)
    if not bars:
        bars = "all clear ✓"
    return "\n" + TEMPLATE.format(
        stack=stack, research=research, bars=bars
    ) + "\n"


def main() -> None:
    readme = ROOT / "README.md"
    parts = readme.read_text(encoding="utf-8").split("```")
    if len(parts) < 3:
        raise SystemExit("No fenced code block found in README.md")
    parts[1] = build_terminal()
    readme.write_text("```".join(parts), encoding="utf-8")
    print("README.md progress block updated")


if __name__ == "__main__":
    main()
