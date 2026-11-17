from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

#we can afford to do brute force cause we have a small number of qubits
def find_paths(edges, start, end):
    graph = {}
    for a, b in edges:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)

    def search(current, path):
        if current == end:
            yield path
            return

        for neighbor in sorted(graph.get(current, [])):
            if neighbor not in path:
                yield from search(neighbor, path + [neighbor])

    yield from search(start, [start])

def build_bell_circuit(num_qubits, path):
    circuit = QuantumCircuit(num_qubits)
    if len(path) < 2:
        raise ValueError("A Bell pair requires two different ports.")

    circuit.h(path[0])
    #make an entanglement with each quibit neighbor in thepath
    for i in range(len(path) - 1):
        circuit.cx(path[i], path[i + 1])

    #get rid of the entanglements of the middle qubits afterwards
    for i in range(len(path) - 3, -1, -1):
        circuit.cx(path[i], path[i + 1])

    return circuit

def optimal_brute_force_transpile(model):
    edges = model["edges"]
    ports = model["ports"]
    #maybe we can define the length to optimzie
    num_qubits = len(model["positions"])
    coupling = CouplingMap(edges)
    coupling.make_symmetric()

    best_circuit = None
    best_cost = None
    for path in find_paths(edges, *ports):
        candidate = build_bell_circuit(num_qubits, path)
        compiled = transpile(
            candidate,
            coupling_map=coupling,
            initial_layout=list(range(num_qubits)),
            routing_method="none",
            basis_gates=["h", "cx"],
            optimization_level=0,
        )
        #prefer fewer CX gates, then lower depth.
        cost = (
            compiled.count_ops().get("cx", 0),
            compiled.depth(),
        )

        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_circuit = compiled
            best_circuit.metadata = {
                "route": path,
                # "routing_swaps": 2 * (len(path) - 2), we do not need swaps i think for routing?
                #basically we can avoid doing "SWAPS" because we can do entanglement propagaition
                #where we entangle the qubits and get rid of entanglements besides our targets afterwards
                "routing_swaps": 0,
            }

    if best_circuit is None:
        raise ValueError(f"No path exists between ports {ports}")

    return best_circuit
