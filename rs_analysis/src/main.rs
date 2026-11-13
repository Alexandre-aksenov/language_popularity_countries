// Load the CSV file for France into Polars
// Proposition by Gemini

use polars::prelude::*;

fn main() -> PolarsResult<()> {
    println!("Hello from polars-rs!");

    // Path relative to the Cargo.toml / workspace root directory
    let file_path = "../dat/FR_2010_2025.csv"; // &str

    // Read the CSV file into a Polars DataFrame
    let df = CsvReadOptions::default()
        .with_has_header(true) // CsvReadOptions
        .try_into_reader_with_file_path(Some(file_path.into()))? // CsvReader<File>
        .finish()?; // DataFrame

    // Extract the column for "Python", 
    // see: https://docs.rs/polars/latest/polars/prelude/struct.DataFrame.html#method.column
    let col_py = df.column("Python")?;
    
    // Print the DataFrame to the screen
    println!("{:?}", df);

    println!("Column for Python:");
    println!("{:?}", col_py);
    Ok(())
}
