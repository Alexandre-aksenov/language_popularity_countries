# see: https://docs.pyscript.net/2026.7.3/user-guide/configuration/
# "Practical example" (section near the bottom)

import numpy as np
from pyscript import display


# Use installed packages.
data = np.array([1, 2, 3, 4, 5])
display(f"Mean: {data.mean()}")

# Read configured files.
"""
with open("data.csv") as f:
    display(f"Data: {f.read()[:100]}")

# Use JavaScript modules.
from pyscript.js_modules import chartjs
display("Chart.js loaded!")
"""
