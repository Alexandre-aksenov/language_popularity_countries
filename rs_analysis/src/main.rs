// Load the CSV file for France into Polars

// use polars::prelude::*;
//-> {to enable passing the data to a plot}
use plotlars::polars::prelude::*;

// see: https://docs.rs/plotlars/latest/plotlars/struct.TimeSeriesPlot.html
use plotlars::{Axis, Legend, Line, Plot, Rgb, Shape, Text, TimeSeriesPlot};
//  These imports were unresolved before backend was added to Cargo.toml
//  plotlars::Plot
//  plotlars::TimeSeriesPlot

// for STL decomposition
use scirs2_series::decomposition::stl::{stl_decomposition, STLOptions};
// use scirs2_core::ndarray::array; // declared as `scirs2-core`
use scirs2_core::ndarray::Array1;

// for numeric output: SD
use std_dev::{standard_deviation, StandardDeviationOutput};
// use log::error;

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
    // println!("{:?}", df);

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

    // Plot the data.
    // This minimal plot can be made "prettier" by adding ticks and vertical lines at September
    TimeSeriesPlot::builder()
        .data(&df_time_py) 
        .x("Time")
        .y("Python")
        .build()
        .plot();
    
    // Next step: STL decomposition of the col "Python". See:
    // https://docs.rs/scirs2-series/latest/scirs2_series/
    // https://stackoverflow.com/a/74332649
    /*
    let array_py = df_time_py.select(["Python"])?
        .to_ndarray::<Float64Type>().unwrap();
    */
    // ->
    // No method named `to_ndarray` found for struct `DataFrame`
    
    // Approach suggested by Gemini
    // 1. Cast the "Python" column from i64 to f64
    let py_series = df_time_py
        .column("Python")?
        .cast(&DataType::Float64)?;

    // 2. Collect into a Vec<f64> (handling potential nulls if any exist)
    let py_vec: Vec<f64> = py_series
        .f64()?
        .into_no_null_iter()
        .collect();

    // 3. Convert to scirs2_core's Array1<f64>
    let array_py: Array1<f64> = Array1::from_vec(py_vec);
    
    // Check the extracted data array
    println!("Data as an array: {:?}", array_py);

    // Compute mean && SD of the original data.
    let ref_array_as_slice = &array_py.as_slice();
    // borrowing is used here to ensure 'array_py' can be reused later.

    let std_full = result_std(ref_array_as_slice)
        .expect("Expected a contiguous array");
    println!("---");
    println!("SD (computed by the library) of full data: {:?}", std_full);

    // STL decomposition
    let options = STLOptions::default(); // STLOptions
    let result = stl_decomposition(&array_py, 12, &options)
        .expect("should succeed"); // DecompositionResult<f64>
    // result.seasonal : ArrayBase<_,Dim<[usize;1]>, f64>

    let seasonal = result.seasonal.as_slice()// Option<&[f64]>
        .expect("seasonal array must be contiguous"); // &[f64]

    println!("---");
    println!("Seasonal: {:?}", seasonal);

    let std_seasonal = standard_deviation(seasonal);
    // StandardDeviationOutput<f64>

    println!("---");
    println!("Its SD (computed by the library): {:?}", std_seasonal);
    
    Ok(())
}

fn result_std(ref_opt_data: &Option<&[f64]>) -> Result<StandardDeviationOutput<f64>, String>
{
    let std_full = match *ref_opt_data {
        Some(ref_data) => Ok(standard_deviation(ref_data)),
        None => Err(String::from("Expected contiguous data")),
    };
    return std_full

}
