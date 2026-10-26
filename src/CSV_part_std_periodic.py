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
print("Version of numpy:", np.__version__)  # 2.5.4
print("Version of polars:", pl.__version__)  # 2.0.0


def part_std_periodic(ser: pl.Series) -> float:
    std_original = np.std(ser.to_numpy())
    decomposed = seasonal_decompose(ser, model="additive", period=12)

    std_seasonal = float(np.std(decomposed.seasonal))
    # Casting with 'float' is used
    # for seasonal_decompose does not declare its output type.

    ratio_seasonal = std_seasonal / std_original
    return ratio_seasonal


def load_data(code_country: str) -> pl.DataFrame:
    filename = f"./dat/{code_country}_2010_2025.csv"
    return pl.read_csv(filename)


# Load the data
df = load_data("FR")

lang = "Python"

print(f"Part of seasonality in Py searches: {part_std_periodic(df[lang]):.2f}")
# FR -> 0.22
