import argparse
import sys

import questionary
from questionary import Style
from questionary.prompts import common

OPTIONS = ("5 qubit", "contemporary", "hyperbolic")

common.INDICATOR_SELECTED = "[x]"
common.INDICATOR_UNSELECTED = "[ ]"

CUSTOM_STYLE = Style([
    ("qmark", "fg:#00aa88 bold"),
    ("question", "bold"),
    ("pointer", "fg:#00aa88 bold"),
    ("highlighted", "bold"),
    ("selected", ""),
    ("instruction", "fg:#888888"),
])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Select all modes")
    parser.add_argument("--5qubit", dest="five_qubit", action="store_true", help="Select 5 qubit")
    parser.add_argument("--contemporary", action="store_true", help="Select contemporary")
    parser.add_argument("--hyperbolic", action="store_true", help="Select hyperbolic")
    args = parser.parse_args()

    selected = [
        option
        for option, enabled in zip(
            OPTIONS,
            (args.five_qubit, args.contemporary, args.hyperbolic),
        )
        if args.all or enabled
    ]

    if not selected:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            parser.exit(
                1,
                "Please provide a mode or run in an interactive terminal.\n",
            )

        try:
            selected = questionary.checkbox(
                "Which quantum code demos do you want to run?",
                choices=list(OPTIONS),
                pointer=">",
                qmark="?",
                style=CUSTOM_STYLE,
                instruction="(↑/↓ move, Space select, Enter confirm)",
                validate=lambda choices: (
                    True if choices else "Select at least one demo."
                ),
            ).ask()
        except KeyboardInterrupt:
            return

    if selected:
        print("Selected: " + ", ".join(selected))


if __name__ == "__main__":
    main()
