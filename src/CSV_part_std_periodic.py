"""
Extract the Time Series for Python from a CSV file.
Compute the standard deviation of the periodic component
/ that of the time series.

Version 1. The data for France.
Version 2. The data for any country in the data.
"""

import polars as pl
import numpy as np

from functions.part_std_periodic import part_std_periodic
from functions.load_data import load_data

# Check the versions
print("Version of numpy:", np.__version__)  # 2.5.4
print("Version of polars:", pl.__version__)  # 2.0.0


def main():
    import sys

    code_country = "FR"  # default: the country where the author lives
    if len(sys.argv) == 2:
        _, code_country = sys.argv  # replace it by the user's input

        # Type check (can it actually fail on sys.argv ?)
        if not isinstance(code_country, str):
            raise ValueError("Country code must be a string.")

    # Load the data
    df = load_data(code_country)

    lang = "Python"
    ratio = part_std_periodic(df[lang])
    print(f"Part of seasonality in Py searches: {ratio:.2f}")


"""

print(f"Part of seasonality in Py searches: {part_std_periodic(df[lang]):.2f}")
# FR -> 0.22
# DE -> 0.11
# IT -> 0.17
"""

if __name__ == "__main__":
    main()
