"""Render learning progress bars into README.md from progress.json.

Reads skills from progress.json, rebuilds the terminal code block
(the first fenced block in README.md), and writes it back.
Triggered by GitHub Actions on progress.json changes, or run locally.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

TEMPLATE = """$ whoami
Modusensus — urban planning · public management
exploring where cities meet data, code & AI

$ echo $STACK
{stack}

$ progress
{bars}

$ cat links.txt
blog      https://modusensus.space
substack  modusensus.substack.com
linkedin  /in/modusensus
afdian    https://ifdian.net/a/modusensus"""


def render_bar(name: str, percent: int) -> str:
    filled = round(percent / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"{name:<10} {bar} {percent:>3}%"


def build_terminal() -> str:
    data = json.loads((ROOT / "progress.json").read_text(encoding="utf-8"))
    stack = " · ".join(data.get("stack", []))
    in_progress = [s for s in data["skills"] if int(s["percent"]) < 100]
    bars = "\n".join(render_bar(s["name"], int(s["percent"])) for s in in_progress)
    if not bars:
        bars = "all clear ✓"
    return "\n" + TEMPLATE.format(stack=stack, bars=bars) + "\n"


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
