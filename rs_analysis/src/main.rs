// Load the CSV file for France into Polars

// use polars::prelude::*;
//-> {to enable passing the data to a plot}
use plotlars::polars::prelude::*;

// see: https://docs.rs/plotlars/latest/plotlars/struct.TimeSeriesPlot.html
use plotlars::{Axis, Legend, Line, Plot, Rgb, Shape, Text, TimeSeriesPlot};
//  These imports were unresolved before backend was added to Cargo.toml, but used here.
//  plotlars::Plot
//  plotlars::TimeSeriesPlot

// for STL decomposition
// use scirs2_series::decomposition::stl::{stl_decomposition, STLOptions};
// -> seasonal decomposition
use scirs2_series::decomposition::{decompose_seasonal, DecompositionModel};

use scirs2_core::ndarray::Array1;

// for numeric output: SD
use std_dev::{standard_deviation, StandardDeviationOutput};

fn main() -> PolarsResult<()> {
    let df_time_py = extract_data_fr()?;
    
    // Print the DataFrame to the screen
    println!("DataFrame for Python with dates:");
    println!("{:?}", df_time_py);
    // -> shape: (194, 2) , 2 columns "Time", "Python" of dtypes : date, i64
    plot_historical(&df_time_py).plot(); // Plot the data.
    
    // Cast the "Python" column from column of i64 to Array1 of f64
    let array_py = cast_py_double_array(&df_time_py)?;
    println!("Data as an array: {:?}", array_py); // Check the extracted data array

    // Compute mean && SD of the original data.
    let ref_array_as_slice = &array_py.as_slice();
    // borrowing is used here to ensure 'array_py' can be reused later. mean: 42.9
    
    /*
    let std_full = result_std(ref_array_as_slice)
        .expect("Expected a contiguous array"); // 
    println!("---");
    println!("SD: {}", std_full.standard_deviation); // 22.4
    */
    // ->
    let std_full = result_just_std(ref_array_as_slice)?;
    println!("SD: {}", std_full); // 22.4
    
    // Seasonal decomposition
    let result = decompose_seasonal(&array_py, 12, DecompositionModel::Additive)
        .expect("decomposition should succeed");
    
    // -> SD of the seasonal component reusing the fn.
    /*
    let std_seasonal2 = result_std(&result.seasonal.as_slice())
        .expect("Expected a contiguous array");
        // StandardDeviationOutput<f64>

    println!("---");
    println!("SD of the seasonal part: {}", std_seasonal2.standard_deviation); // 4.6
    */
    // ->
    let std_seasonal2 = result_just_std(&result.seasonal.as_slice())?;
    println!("SD of the seasonal part: {}", std_seasonal2); // 4.6
    
    println!("Ratio: {}", std_seasonal2 / std_full);
    // 0.206
    
    Ok(())
}

// Data extraction from files.

/// Extracts historical data for France.
/// DF with 2 columns: 'Time' (date), 'Python' (i64) , 1 row per month.
fn extract_data_fr() -> PolarsResult<DataFrame>
{
    // Path relative to the Cargo.toml / workspace root directory
    let file_path = "../dat/FR_2010_2025.csv"; // &str

    // Read the CSV file into a Polars DataFrame
    let df = CsvReadOptions::default()
        .with_has_header(true) // CsvReadOptions
        .try_into_reader_with_file_path(Some(file_path.into()))? // CsvReader<File>
        .finish()?; // DataFrame

    // Extract the column with indices
    let df_time_py = df.select(["Time", "Python"])?;

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
    
    Ok(df_time_py)
}

/// Plot the data.
/// This minimal plot can be made "prettier" 
/// by adding ticks and vertical lines at September.
/// Input: DF with 2 columns
///     "Time" (independent)
///     "Python" (dependent)
/// Output: TimeSeriesPlot instance.
fn plot_historical(df_time_py: &DataFrame) -> TimeSeriesPlot {
    TimeSeriesPlot::builder()
        .data(&df_time_py)
        .x("Time")
        .y("Python")
        .build()
        // .plot()
}

// fns for Data analysis. The rest will join.

/// Cast the "Python" column from i64 to Array1 of f64
fn cast_py_double_array(df_time_py: &DataFrame) -> PolarsResult<Array1<f64>>
{
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
    
    Ok(array_py)
}

/// Input: data (&Option<&[f64]>).
///   The first reference is for explicitly borrowing data,
///   Option id for a noncontiguous Array upstream may lead to None ,
///   the 2nd reference is for passing the expected input type to the fn 
///   'standard_deviation' .
/// Output: Result<StandardDeviationOutput>
// fn result_std(ref_opt_data: &Option<&[f64]>) -> Result<StandardDeviationOutput<f64>, String>
/*
fn result_std(ref_opt_data: &Option<&[f64]>) -> Result<StandardDeviationOutput<f64>, String>
{
    let std_full = match *ref_opt_data {
        Some(ref_data) => Ok(standard_deviation(ref_data)),
        None => Err(String::from("Expected contiguous data")),
    };
    // return std_full
    std_full
}
*/
// ->
fn result_std(ref_opt_data: &Option<&[f64]>) -> PolarsResult<StandardDeviationOutput<f64>>
{
    /*
    let std_full = match *ref_opt_data {
        Some(ref_data) => Ok(standard_deviation(ref_data)),
        None => Err(String::from("Expected contiguous data")),
    };
    */
    // ->
    let std_full = standard_deviation((*ref_opt_data)
        .expect("Expected contiguous data"));

    Ok(std_full)
}

fn result_just_std(ref_opt_data: &Option<&[f64]>) -> PolarsResult<f64>
{
    let std_full = result_std(ref_opt_data)
        .expect("Expected a contiguous array"); // mean: 42.9

    // println!("SD: {}", std_full.standard_deviation);
    Ok(std_full.standard_deviation)
}
