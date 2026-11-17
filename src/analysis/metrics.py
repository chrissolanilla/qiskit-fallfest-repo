from qiskit import QuantumCircuit
from qiskit.quantum_info import (
    Statevector,
    partial_trace,
    state_fidelity,
)

def run_ideal(circuit, ports):
    #simulate the circuit without noise
    state = Statevector.from_instruction(circuit)

    other_qubits = [
        q for q in range(circuit.num_qubits)
        if q not in ports
    ]
    #partial trace makes it so we keep only the two output ports
    output_state = partial_trace(state, other_qubits)

    #this is not cheating cause Statevector simulates every qubit and gate
    #partial trace gets the reduced density matrix
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    target = Statevector.from_instruction(bell)
    #compare otu output
    fidelity = state_fidelity(output_state, target)

    return {
        "fidelity": fidelity,
        "depth": circuit.depth(),
        "cx_count": circuit.count_ops().get("cx", 0),
        "num_qubits": circuit.num_qubits,
    }
