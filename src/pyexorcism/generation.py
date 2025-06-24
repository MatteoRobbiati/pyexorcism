import random
import itertools


def random_Z_boolean_function(n, num_terms, max_locality=3, seed=42):
    """
    Generate a random Boolean function as a sum of unique Z-products (over n bits).
    Each term is a product of up to 'max_locality' different Z_i.
    No repeated terms (regardless of order).

    Returns:
        terms: list of tuples (coeff, [qubit_indices])
        as readable string: e.g., "+1*Z0Z2Z5 -1*Z1Z3"
    """
    random.seed(seed)
    # Build the set of all possible (unique) terms, for all localities
    all_terms = []
    for k in range(1, max_locality + 1):
        all_terms.extend(itertools.combinations(range(n), k))

    if num_terms > len(all_terms):
        raise ValueError(
            f"num_terms={num_terms} is larger than the total possible unique terms={len(all_terms)} for n={n}, max_locality={max_locality}"
        )

    selected_terms = random.sample(all_terms, num_terms)
    terms = []
    for qubits in selected_terms:
        coeff = random.choice([1, -1])
        terms.append((coeff, list(qubits)))

    # For a readable string:
    terms_str = []
    for coeff, qlist in terms:
        s = ("+" if coeff > 0 else "-") + "1*" + "".join([f"Z{q}" for q in qlist])
        terms_str.append(s)
    func_string = " ".join(terms_str)
    return terms, func_string


def z_terms_to_bool_func(terms, n):
    """
    Returns a Python function f(b0, b1, ..., bn-1) -> {0,1}
    representing the XOR (mod 2 sum) of the Z-terms (with sign).
    Each term: (coeff, [qubit_indices])
    """

    def f(*bits):
        s = 0
        for coeff, qubits in terms:
            prod = coeff
            for q in qubits:
                prod *= (-1) if bits[q] else 1
            s ^= prod == -1  # XOR: add 1 if the product is -1
        return s & 1

    return f


def boolean_function_to_pla(bool_func, n, input_labels=None, output_label=None):
    lines = []
    lines.append(f".i {n}")
    lines.append(f".o 1")
    if input_labels:
        lines.append(".ilb " + " ".join(str(x) for x in input_labels))
    if output_label:
        lines.append(".ob " + str(output_label))
    for x in range(2**n):
        bits = [(x >> i) & 1 for i in reversed(range(n))]
        out = bool_func(*bits)
        lines.append("".join(str(b) for b in bits) + f" {out}")
    lines.append(".e")
    return "\n".join(lines)


def majority_function(n):
    """
    1 if sum of bits > n//2, else 0
    """

    def f(*bits):
        return int(sum(bits) > n // 2)

    return f
