"""
Extract the Time Series for Python from a CSV file.
Compute the standard deviation of the periodic component
/ that of the time series.

Version 1. The data for France.
"""

import polars as pl
import numpy as np

from statsmodels.tsa.seasonal import seasonal_decompose

# Check the versions
print(np.__version__)  # 2.5.4
print(pl.__version__)  # 2.0.0


def part_std_periodic(ser) -> float:
    std_original = np.std(ser.to_numpy())
    decomposed = seasonal_decompose(ser, model="additive", period=12)

    std_seasonal = float(np.std(decomposed.seasonal))
    # Casting with 'float' is used
    # for seasonal_decompose does not declare its output type.

    ratio_seasonal = std_seasonal / std_original
    return ratio_seasonal


# Load the data
df = pl.read_csv("./dat/FR_2010_2025.csv")

dec = seasonal_decompose(df["Python"], model="additive", period=12)

std_seasonality = float(np.std(dec.seasonal))
# Casting with 'float' is used
# for seasonal_decompose does not declare its output type.

print(f"SD of the seasonality component: {std_seasonality:.2f}")  # FR -> 4.96

std_orig = np.std(df["Python"].to_numpy())
print(f"Standard deviation of the original signal: {std_orig:.2f}")
# FR -> 22.38

ratio = std_seasonality / std_orig
print(f"Part of the seasonality component: {ratio:.2f}")  # FR -> 0.22

print(f"Part using function: {part_std_periodic(df["Python"]):.2f}")
