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

    # now we actually run our program
    # compile the specific circuit most optimal for least noise
    # default is make it on the ports defined
    # our main goal is just to do a cnot with the defined ports
    # for my case, i want to explore cross talk noise like my previous research.
    # i want incoperate always on and spectator noise, and we derive this with the hamiltonian and pauli twirling?
    # maybe we do not need pauli twirling since the qubit count is so low and we can get the optimal circuit

    noise = []
    noisy_result = []
    protected_result = []
    i=0
    for qpu in selected:
        circuit = optimal_brute_force_transpile(qpu)
        noise =+ analyze_noise() #maybe get noise is better name?
        noisy_result[i] = get_noisy_result(noise)
        protected_result[i] = get_protected_result(circuit, noise) # maybe just pass in noisy_result?

    for result in results:
        print("Results:")
        #print the results i guess maybe in a table form or something

if __name__ == "__main__":
    main()
