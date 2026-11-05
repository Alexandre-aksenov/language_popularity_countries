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
from functions.code_opt_country_name import code2opt_name

import streamlit as st
import json

# For plotting the data
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Seasonal trend in Python searches per country",
    layout="wide",
    initial_sidebar_state="expanded",
)

code_country = st.text_input("Code of a country", "FR", max_chars=2)

if code_country and len(code_country) == 2:
    # switch to uppercase
    code_country = code_country.upper()

    # Try to extract the name
    country_name = code2opt_name(code_country)

    if country_name:
        # Load the data
        try:
            df = fetch_google_trends_polars(geo=code_country)

            if df is not None:
                data_column = "search_interest"
                ratio = part_std_periodic(df[data_column])
                st.write(f"Part of seasonality in Py searches for {country_name}: {ratio:.2f}")

                # Plot
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.plot(df["date"], df["search_interest"], label="Python")
                ax.set_xlabel("Time")
                ax.set_ylabel("Search interest")
                ax.set_title(f"Search interest for Python in {country_name}")
                ax.legend()
                st.pyplot(fig)

            else:
                st.write("Could not connect to Google Trends. Please, try again later.")
        except json.decoder.JSONDecodeError:  # can occur at 'fetch_google_trends_polars'
            st.write("Could not decode the reply of Google Trends. Please, file an issue to the author.")
    else:
        st.write("This country has not been found.")
else:
    st.write("Please enter a valid country code.")

# if __name__ == "__main__":
#     main()

st.markdown("""
-----
Some results in Western Europe and North America.

High seasonality:

| Country | Ratio |
|---------|-------|
| FR      | 0.23  |
| BE      | 0.24  |
| CZ      | 0.29  |

Low seasonality:

| Country | Ratio |
|---------|-------|
| DE      | 0.10  |

Most values are between 0.15 and 0.20:

| Country | Ratio |
|---------|-------|
| PL      | 0.16  |
| CH      | 0.17  |
| NL      | 0.17  |
| IT      | 0.18  |
| US      | 0.18  |
| GB      | 0.20  |
| CA      | 0.20  |
| ES      | 0.20  |
""")
