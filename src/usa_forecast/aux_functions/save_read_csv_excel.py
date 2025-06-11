from pathlib import Path
import pandas as pd

#%%

def export_results_to_csv(
    results: dict[str, pd.DataFrame],
    output_dir: str = "Output"
) -> None:
    """
    Exports each DataFrame in the results dictionary to a CSV file.
    The files are saved in the specified output directory and named by their ticker symbol.

    Parameters
    ----------
    results : dict[str, pd.DataFrame]
        Dictionary mapping ticker symbols to their enriched DataFrames.
    output_dir : str, optional
        Directory where CSV files will be saved (default is 'Output').
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for ticker, df in results.items():
        file_path = Path(output_dir) / f"{ticker}.csv"
        df.to_csv(file_path)
