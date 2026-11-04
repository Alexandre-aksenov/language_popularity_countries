"""
Extract the Time Series for "Python" from Google Trends data.
Compute the standard deviation of the periodic component
/ that of the time series.

Version 1. Runs on the local machine in Command Line.
Version 2. Runs as a local Streamlit server.
"""

# import polars as pl
# import numpy as np

from functions.part_std_periodic import part_std_periodic
from functions.fetch_google_trends_2010_2025 import fetch_google_trends_polars

import streamlit as st


st.set_page_config(
    page_title="Medical Image Data Exploration",
    layout="wide",
    initial_sidebar_state="expanded",
)

code_country = st.text_input("Code of a country", "FR", max_chars=2)

if code_country and len(code_country) == 2:
    # Load the data
    df = fetch_google_trends_polars(geo=code_country)

    data_column = "search_interest"
    ratio = part_std_periodic(df[data_column])
    st.write(f"Part of seasonality in Py searches for {code_country}: {ratio:.2f}")
else:
    st.write("Please enter a valid country code.")

# if __name__ == "__main__":
#     main()

st.markdown("""
-----
Some previous results.

High seasonality, which may be qualified as a separate group
FR -> 0.23
BE -> 0.24
CZ -> 0.29 (outlayer)

Low seasonality:
DE -> 0.10 (outlayer)

Most common values:
PL -> 0.16
CH -> 0.17
NL -> 0.17
IT -> 0.18
US -> 0.18
GB -> 0.20
CA -> 0.20
ES -> 0.20
""")
