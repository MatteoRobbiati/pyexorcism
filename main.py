import random

from pyexorcism.generation import (
    random_Z_boolean_function,
    z_terms_to_bool_func,
    boolean_function_to_pla,
)
from pyexorcism.optimization import SimpleExorcism
from pyexorcism.circuit import esop_to_qibo_circuit

nsites = 10
nterms = 10
theta = 0.01

# Generating a generic Z-based function
terms, func_string = random_Z_boolean_function(
    nsites, nterms, max_locality=nsites, seed=42
)
print("Random Boolean function (in Zs):")
print(func_string)


# Convert the generated terms into a boolean function
bool_f = z_terms_to_bool_func(terms, nsites)


# Convert it into PLA string
pla_string = boolean_function_to_pla(bool_f, nsites)
# print(pla_string)

# 3. Get PLA lines
pla_lines = pla_string.splitlines()

# 4. Run Exorcism minimization
exorcism = SimpleExorcism.from_pla(pla_lines)
minimized_cubes = exorcism.minimize()

print("Minimized cubes (ESOP):", minimized_cubes)

# 5. ESOP to circuit
circuit = esop_to_qibo_circuit(minimized_cubes, nsites, theta)
circuit.draw()
