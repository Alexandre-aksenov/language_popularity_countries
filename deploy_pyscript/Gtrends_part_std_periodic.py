"""
Extract the Time Series for "Python" from Google Trends data.
Compute the standard deviation of the periodic component
/ that of the time series.

Version 1. Runs on the local machine.
Version 2. To run in browser via pyscript.
"""

import polars as pl
import numpy as np

from functions.part_std_periodic import part_std_periodic
from functions.fetch_google_trends_2010_2025 import fetch_google_trends_polars

# for deploy to pyscript
from pyscript import display


def main():
    import sys

    code_country = "FR"  # default: the country where the author lives

    """
    # V3: user input from browser.
    if len(sys.argv) == 2:
        _, code_country = sys.argv  # replace it by the user's input

        # Type check (can it actually fail on sys.argv ?)
        if not isinstance(code_country, str):
            raise ValueError("Country code must be a string.")
    """

    # Load the data
    df = fetch_google_trends_polars(geo=code_country)

    lang = "search_interest"
    ratio = part_std_periodic(df[lang])
    print(f"Part of seasonality in Py searches: {ratio:.2f}")


if __name__ == "__main__":
    main()

"""
Some results.

High seasonality, which may be qualified as a separate group
FR -> 0.23
BE -> 0.24
CZ -> 0.29 (outlayer)

Low seasonality:
DE -> 0.12 (outlayer)

Most common values:
PL -> 0.16
CH -> 0.17
NL -> 0.17
IT -> 0.18
US -> 0.18
GB -> 0.20
CA -> 0.20
ES -> 0.20
"""