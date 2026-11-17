import argparse
import sys

import questionary
from questionary import Style
from questionary.prompts import common

from coupling_graphs.graphs import models

OPTIONS = {
    "5 qubit": "2016-inspired reference",
    "contemporary": "Contemporary IBM-style",
    "hyperbolic": "Hyperbolic-inspired model",
}

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

    for qpu in selected:
        model = models[OPTIONS[qpu]]
        circuit = optimal_brute_force_transpile(model)
        #first case: ideal, no noise
        ideal_result = run_ideal(circuit, model["ports"])

        #second case: our own noisy baseline of injected crosstalk
        crosstalk = get_crosstalk(model, circuit)
        noisy_result = run_noisy(
            circuit,
            baseline_noise,
            crosstalk,
        )

        # third case: injected crosstalk noise AND protection method
        protected_circuit = protect_circuit(
            circuit,
            model,
        )
        protected_result = run_noisy(
            protected_circuit,
            baseline_noise,
            get_crosstalk(model, protected_circuit),
        )

        results.append({
            "qpu": qpu,
            "ideal": ideal_result,
            "noisy": noisy_result,
            "protected": protected_result,
        })

    print_results(results)

if __name__ == "__main__":
    main()
