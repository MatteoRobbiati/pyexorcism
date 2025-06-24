from qibo import Circuit, gates


def add_cube_phase(circuit, cube, theta, qubits):
    """
    Adds a multi-controlled RZ rotation according to the cube.
    cube: string (e.g. '1-0'), qubits: list of qubit indices, theta: float
    """
    controls = []
    flip = []
    n = len(cube)
    for i, val in enumerate(cube):
        if val == "1":
            controls.append(qubits[i])
        elif val == "0":
            circuit.add(gates.X(qubits[i]))
            controls.append(qubits[i])
            flip.append(qubits[i])
        # if '-', not a control
    # Choose a target qubit NOT in controls, or just the first qubit (if all are controls)
    target = next((q for q in qubits if q not in controls), qubits[0])
    # Apply controlled RZ
    gate = gates.RZ(target, theta)
    if controls:
        gate = gate.controlled_by(*controls)
    circuit.add(gate)
    # Undo any X flips
    for q in flip:
        circuit.add(gates.X(q))


def esop_to_qibo_circuit(minimized_cubes, n, theta=3.14):
    """
    minimized_cubes: list of cube strings (from SimpleExorcism)
    n: number of qubits
    theta: phase to apply (default pi)
    Returns: Qibo Circuit
    """
    circuit = Circuit(n)
    qubits = list(range(n))
    for cube in minimized_cubes:
        # Skip cubes that are all '-' (global phase, not physical)
        if all(c == "-" for c in cube):
            continue
        add_cube_phase(circuit, cube, theta, qubits)
    return circuit
