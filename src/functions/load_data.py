import polars as pl


def load_data(code_country: str) -> pl.DataFrame:
    filename = f"./dat/{code_country}_2010_2025.csv"
    return pl.read_csv(filename)
