from dataclasses import dataclass
from math import isfinite, pi
from typing import Literal

from qiskit import QuantumCircuit

Mechanism = Literal["pure_rzz", "controlled_phase"]
Channel = Literal["both", "always_on", "spectator"]

def _edge(a: int, b: int) -> tuple[int, int]:
    return (min(a, b), max(a, b))

@dataclass(frozen=True)
class CrosstalkNoise:
    zeta_hz: float = 50_000.0
    duration_s: float = 1.3e-6
    spectator_zeta_hz: float = 50_000.0
    spectator_duration_s: float = 70e-9
    mechanism: Mechanism = "pure_rzz"

    def __post_init__(self) -> None:
        for key in (
            "zeta_hz", "duration_s", "spectator_zeta_hz", "spectator_duration_s"
        ):
            value = getattr(self, key)
            if not isfinite(value):
                raise ValueError(f"{key} must be finite")
        if self.duration_s < 0 or self.spectator_duration_s < 0:
            raise ValueError("Interaction durations must be nonnegative")
        if self.mechanism not in ("pure_rzz", "controlled_phase"):
            raise ValueError("Invalid Hamiltonian mechanism")

    @staticmethod
    def phase(zeta_hz: float, duration_s: float) -> float:
        """Hamiltonian phase in radians, using Hz and seconds."""
        if not isfinite(zeta_hz) or not isfinite(duration_s) or duration_s < 0:
            raise ValueError("Invalid coupling or duration")
        angle = 2 * pi * zeta_hz * duration_s
        if not isfinite(angle):
            raise ValueError("Interaction phase must be finite")
        return angle

    def _append_interaction(
        self, target: QuantumCircuit, a: int, b: int,
        zeta_hz: float, duration_s: float,
    ) -> None:
        angle = self.phase(zeta_hz, duration_s)
        if angle == 0:
            return
        if self.mechanism == "pure_rzz":
            target.rzz(angle, a, b)
        else:
            # Qiskit cp(lambda) = diag(1,1,1,exp(+i*lambda)).
            # For H/h = zeta |11><11|, U = diag(1,1,1,exp(-i*angle)).
            target.cp(-angle, a, b)

    def inject(
        self,
        circuit: QuantumCircuit,
        edges: list[tuple[int, int]] | tuple[tuple[int, int], ...],
        channel: Channel = "both",
    ) -> QuantumCircuit:
        """Return a NEW circuit with coherent physical crosstalk.

        Only unitary circuits with supported serial H/CX-style gate schedules
        are accepted. Measurements, resets, delays and control flow are not
        silently modeled because they require additional timing rules.

        Each unitary instruction (other than barrier) represents one gate
        window; its duration is approximated with `duration_s`, regardless
        of its actual physical gate length. The spectator extra term acts
        after each CX. This makes controlled comparisons straightforward,
        but is not a calibrated QPU timing model.
        """
        if channel not in ("both", "always_on", "spectator"):
            raise ValueError("channel must be both, always_on, or spectator")
        if circuit.num_clbits:
            raise ValueError("This coherent model requires a circuit without classical bits")
        unique_edges = set()
        for a, b in edges:
            if (
                not isinstance(a, int) or not isinstance(b, int)
                or a == b or min(a, b) < 0 or max(a, b) >= circuit.num_qubits
            ):
                raise ValueError(f"Invalid coupling edge {(a, b)}")
            unique_edges.add(_edge(a, b))
        graph_edges = sorted(unique_edges)

        noisy = QuantumCircuit(*circuit.qregs, name=f"{circuit.name}_xtalk")
        noisy.global_phase = circuit.global_phase
        noisy.metadata = dict(circuit.metadata or {})
        noisy.metadata["crosstalk"] = {
            "channel": channel,
            "mechanism": self.mechanism,
            "always_on_zeta_hz": self.zeta_hz,
            "always_on_duration_s_per_gate": self.duration_s,
            "spectator_zeta_hz": self.spectator_zeta_hz,
            "spectator_duration_s_per_cx": self.spectator_duration_s,
            "timing_assumption": "serial per-instruction windows; post-gate injection",
        }

        for instruction in circuit.data:
            op = instruction.operation
            name = op.name
            if name == "barrier":
                noisy.append(op, instruction.qubits)
                continue
            if name in ("measure", "reset", "delay") or op.num_clbits:
                raise ValueError(f"Unsupported timed/nonunitary operation: {name}")
            if name in ("if_else", "for_loop", "while_loop", "switch_case"):
                raise ValueError(f"Unsupported control-flow operation: {name}")

            qubits = tuple(circuit.find_bit(q).index for q in instruction.qubits)
            noisy.append(op, qubits)

            if channel in ("both", "always_on"):
                for a, b in graph_edges:
                    self._append_interaction(noisy, a, b, self.zeta_hz, self.duration_s)

            if channel in ("both", "spectator") and name == "cx":
                active = set(qubits)
                active_edge = _edge(*qubits)
                for a, b in graph_edges:
                    if (a, b) != active_edge and (a in active or b in active):
                        self._append_interaction(
                            noisy, a, b,
                            self.spectator_zeta_hz, self.spectator_duration_s,
                        )

        return noisy
