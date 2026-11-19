from qiskit import QuantumCircuit
from qiskit.quantum_info import (
    Statevector,
    partial_trace,
    state_fidelity,
)

def bell_fidelity(circuit, ports):
    """Simulate the full circuit and measure Bell fidelity on two ports."""
    if len(ports) != 2 or len(set(ports)) != 2:
        raise ValueError("Expected two distinct output ports")

    if any(q < 0 or q >= circuit.num_qubits for q in ports):
        raise ValueError("Output ports must belong to the circuit")

    #Statevector simulates every qubit and gate but with partial trace so its a reduce density matrix
    state = Statevector.from_instruction(circuit)
    other_qubits = [
        q for q in range(circuit.num_qubits)
        if q not in ports
    ]
    output_state = partial_trace(state, other_qubits)

    #target Bell state is (|00> + |11>) / sqrt(2)
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    target = Statevector.from_instruction(bell)

    return float(state_fidelity(output_state, target))

#wrapper functions for bell_fidelity depending on the case
def run_noisy(circuit, ports):
    return {
        "fidelity": bell_fidelity(circuit, ports),
        "depth": circuit.depth(),
        "cx_count": circuit.count_ops().get("cx", 0),
        "num_qubits": circuit.num_qubits,
        "rzz_count": circuit.count_ops().get("rzz", 0),
        "cp_count": circuit.count_ops().get("cp", 0),
    }

def run_ideal(circuit, ports):
    return {
        "fidelity": bell_fidelity(circuit, ports),
        "depth": circuit.depth(),
        "cx_count": circuit.count_ops().get("cx", 0),
        "num_qubits": circuit.num_qubits,
    }
