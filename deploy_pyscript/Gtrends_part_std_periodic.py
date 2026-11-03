"""
Extract the Time Series for "Python" from Google Trends data.
Compute the standard deviation of the periodic component
/ that of the time series.

Version 1. Runs on the local machine.
Version 2. To run in browser via pyscript.
"""

import polars as pl
import numpy as np

# from functions.part_std_periodic import part_std_periodic
# from functions.fetch_google_trends_2010_2025 import fetch_google_trends_polars

# for deploy to pyscript
from pyscript import display


# To simplify deployment, everything is in one module in this version.
# fetch_google_trends_2010_2025.py
def fetch_google_trends_csv(
    keyword: str = "/m/05z1_",
    # Google Knowledge Graph entity for Python (Programming Language)
    geo: str = "FR",
    time_range: str = "2010-01-01 2025-12-31",  # e.g., "all", "today 5-y", "today 12-m"
    hl: str = "en-US",
) -> str:
    import json
    import urllib.parse
    import requests

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    # 1. Warm up session / cookies
    session.get("https://trends.google.com/?geo=" + geo)

    # 2. Query the explore endpoint to get widget tokens
    req_payload = {
        "comparisonItem": [{"keyword": keyword, "geo": geo, "time": time_range}],
        "category": 0,
        "property": "",
    }

    explore_params = {
        "hl": hl,
        "req": json.dumps(req_payload),
        "tz": "-60",
    }

    explore_url = f"https://trends.google.com/trends/api/explore?{urllib.parse.urlencode(explore_params)}"
    response = session.get(explore_url)
    response.raise_for_status()

    # Google Trends prefixes JSON responses with ")]}'\n" to avoid XSSI
    raw_text = response.text

    # Arbitrary data from Google API. Google may change this prefix.
    if raw_text.startswith(")]}"):
        raw_text = raw_text.split("\n", 1)[1]

    data = json.loads(raw_text)
    # This panics if JSON has not been correctly extracted from 'response':

    # JSONDecodeError("Expecting value", s, err.value) from None
    # json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

    # 3. Locate the 'TIMESERIES' widget token and request payload
    timeseries_widget = None
    for widget in data.get("widgets", []):
        if widget.get("id") == "TIMESERIES":
            timeseries_widget = widget
            break

    if not timeseries_widget:
        raise ValueError("Could not find TIMESERIES widget in Google Trends response.")

    token = timeseries_widget["token"]
    widget_req = json.dumps(timeseries_widget["request"])

    # 4. Fetch the CSV directly
    csv_params = {
        "hl": hl,
        "req": widget_req,
        "token": token,
        "tz": "-60",
    }
    csv_url = f"https://trends.google.com/trends/api/widgetdata/multiline/csv?{urllib.parse.urlencode(csv_params)}"
    csv_response = session.get(csv_url)
    csv_response.raise_for_status()

    return csv_response.text


def load_trends_to_polars(csv_text: str) -> pl.DataFrame:
    """
    Google Trends CSVs contain header metadata lines
    (e.g., 'Category: All categories')
    Use skip_rows to skip metadata before the column header row
    (typically line 2 or 3)
    """
    df_result = pl.read_csv(
        csv_text.encode("utf-8"),
        skip_rows=2,
    )

    # Clean and cast columns:
    # 1. First column (Month) parsed as Date
    # 2. Second column (Score) cleaned for any '<1' values and cast to Int64
    date_col = df_result.columns[0]
    score_col = df_result.columns[1]

    df_result = df_result.with_columns(
        [
            pl.col(date_col).str.to_date("%Y-%m").alias("date"),
            pl.col(score_col)
            .cast(pl.Utf8)
            .str.replace("<1", "0")
            .cast(pl.Int64, strict=False)
            .alias("search_interest"),
        ]
    ).select(["date", "search_interest"])

    return df_result


def fetch_google_trends_polars(
    keyword: str = "/m/05z1_",
    # Google Knowledge Graph entity for Python (Programming Language)
    geo: str = "FR",
    time_range: str = "2010-01-01 2025-12-31",
) -> pl.DataFrame:
    csv_content = fetch_google_trends_csv(
        keyword,
        geo,
        # time_range="all"
        time_range
    )
    df = load_trends_to_polars(csv_content)
    return df


# part_std_periodic.py
def part_std_periodic(ser: pl.Series) -> float:
    from statsmodels.tsa.seasonal import seasonal_decompose

    std_original = np.std(ser.to_numpy())
    decomposed = seasonal_decompose(ser, model="additive", period=12)

    std_seasonal = float(np.std(decomposed.seasonal))
    # Casting with 'float' is used
    # for seasonal_decompose does not declare its output type.

    ratio_seasonal = std_seasonal / std_original
    return ratio_seasonal


def main():
    # import sys

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
    display(f"Part of seasonality in Py searches: {ratio:.2f}")


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