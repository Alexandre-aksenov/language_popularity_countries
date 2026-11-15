// Load the CSV file for France into Polars
// Proposition by Gemini

use polars::prelude::*;

// see: https://docs.rs/plotlars/latest/plotlars/struct.TimeSeriesPlot.html
use plotlars::{Axis, Legend, Line, Plot, Rgb, Shape, Text, TimeSeriesPlot};
// Unresolved imports (although declared in the example)
//  plotlars::Plot
//  plotlars::TimeSeriesPlot

fn main() -> PolarsResult<()> {
    // println!("Hello from polars-rs!");

    // Path relative to the Cargo.toml / workspace root directory
    let file_path = "../dat/FR_2010_2025.csv"; // &str

    // Read the CSV file into a Polars DataFrame
    let df = CsvReadOptions::default()
        .with_has_header(true) // CsvReadOptions
        .try_into_reader_with_file_path(Some(file_path.into()))? // CsvReader<File>
        .finish()?; // DataFrame

    // Extract the column for "Python",
    // see: https://docs.rs/polars/latest/polars/prelude/struct.DataFrame.html#method.column
    // let col_py = df.column("Python")?;

    // Print the column to the screen
    println!("{:?}", df);

    // println!("Column for Python:");
    // println!("{:?}", col_py);
    
    // Extract a new DF
    // let df_py = df.select(["Python"])?;

    // Print the DataFrame to the screen
    // println!("DataFrame for Python:");
    // println!("{:?}", df_py);
    // -> shape: (194, 1) , one column "Python" of dtype : i64

    // Extract the column with indices
    let df_time_py = df.select(["Time", "Python"])?;

    // Print the DataFrame to the screen
    println!("DataFrame for Python with timestamps:");
    println!("{:?}", df_time_py);
    // -> shape: (194, 2) , 2 columns "Time", "Python" of dtypes : str, i64
    
    // Convert the type of column "Time" from "str" to Chrono.
    // Suggested by Gemini
    let df_time_py = df_time_py
        .lazy()
        .with_columns([
            col("Time")
                .str()
                .to_date(StrptimeOptions { // https://docs.rs/crate/polars-plan/0.55.2#method.to_date
                    format: Some("%Y-%m-%d".into()),
                    ..Default::default()
                })
        ])// LazyFrame
        .collect()?;
    
    // Print the DataFrame to the screen
    println!("DataFrame for Python with dates:");
    println!("{:?}", df_time_py);
    // -> shape: (194, 2) , 2 columns "Time", "Python" of dtypes : date, i64
    
    Ok(())
}
