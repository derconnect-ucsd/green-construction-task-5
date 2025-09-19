import os
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime

print("=== PMU Data Reader Starting ===")
print("All imports loaded successfully")

# =============================================================================
# CONFIGURATION - Change these values to analyze different files
# =============================================================================

# Choose which signal file to analyze (uncomment one):
SIGNAL_FILENAME = "20250908,000000.000000000,60,Float32.signal"
# SIGNAL_FILENAME = "20250906,000000.000000000,60,Float32.signal"
# SIGNAL_FILENAME = "20250907,003749.466666666,60,Float32.signal"
# SIGNAL_FILENAME = "20250908,000000.000000000,60,Float32.signal"
# SIGNAL_FILENAME = "20250909,000000.000000000,60,Float32.signal"

# You can also specify a different PMU data path:
PMU_DATA_PATH = "SWGR_C_1B17_PhaseA_Current/PhaseA.Current.Magnitude/2025/09/"

# Plot configuration
ENABLE_PLOT = False  # Set to False to disable plotting

# CSV Export configuration
EXPORT_CSV = True  # Set to False to disable CSV export
CSV_OUTPUT_DIR = "data/temp"  # Directory to save CSV files

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def list_available_signal_files():
    """List all available .signal files in the PMU data directories"""
    base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'pmu-data', 'pmu-sample-data')
    
    signal_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.signal'):
                rel_path = os.path.relpath(os.path.join(root, file), base_path)
                signal_files.append(rel_path)
    
    return sorted(signal_files)

def build_file_path(pmu_data_path, signal_filename):
    """Build the complete file path for a PMU signal file"""
    script_dir = os.path.dirname(__file__)
    base_path = os.path.join(script_dir, '..', '..', 'data', 'raw', 'pmu-data', 'pmu-sample-data')
    file_path = os.path.join(base_path, pmu_data_path, signal_filename)
    return os.path.abspath(file_path)

def analyze_pmu_file(file_path):
    """Main function to analyze a PMU signal file"""
    
    print("=== Analyzing PMU Signal File ===\n")
    print(f"File: {file_path}")
    print(f"File size: {os.path.getsize(file_path)} bytes")
    
    # Read the binary data as Float32 (based on filename)
    data_f32 = np.fromfile(file_path, dtype=np.float32)
    print(f"Total data points: {len(data_f32)}")
    print(f"Value range: {data_f32.min()} to {data_f32.max()}")
    print(f"Unique values: {np.unique(data_f32)}")
    
    # Parse filename to extract metadata
    filename = os.path.basename(file_path)
    filename_parts = filename.replace('.signal', '').split(',')
    
    if len(filename_parts) >= 3:
        date_str = filename_parts[0]
        time_str = filename_parts[1]
        frequency = int(filename_parts[2])
        
        print(f"\nFrom filename:")
        print(f"  Date: {date_str}")
        print(f"  Time: {time_str}")
        print(f"  Frequency: {frequency} Hz")
        
        # Create timestamps based on filename and sampling frequency
        print("\n=== Creating Timestamps ===")
        try:
            # Parse the start datetime from filename
            start_date = datetime.strptime(date_str, "%Y%m%d")
            time_parts = time_str.split('.')
            hours = int(time_parts[0][:2])
            minutes = int(time_parts[0][2:4]) 
            seconds = int(time_parts[0][4:6])
            microseconds = int(float('0.' + time_parts[1]) * 1000000) if len(time_parts) > 1 else 0
            
            start_datetime = start_date.replace(hour=hours, minute=minutes, second=seconds, microsecond=microseconds)
            print(f"Start time from filename: {start_datetime}")
            
            # Generate timestamps for each data point based on sampling frequency
            time_interval = 1.0 / frequency  # seconds between samples
            
            # Create DataFrame with timestamps for ALL data points (including zeros)
            timestamps = []
            values = []
            
            for i in range(len(data_f32)):
                # Calculate timestamp for this data point
                elapsed_time = i * time_interval
                timestamp = start_datetime + pd.Timedelta(seconds=elapsed_time)
                timestamps.append(timestamp)
                values.append(data_f32[i])
            
            df = pd.DataFrame({
                'timestamp': timestamps,
                'value': values
            })
            
            print(f"Created {len(df)} data points")
            print(f"Time range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
            
        except Exception as e:
            print(f"Error creating timestamps: {e}")
            # Fallback to simple indexing
            df = pd.DataFrame({
                'index': range(len(data_f32)),
                'value': data_f32
            })
    else:
        print("Could not parse filename for metadata")
        df = pd.DataFrame({
            'index': range(len(data_f32)),
            'value': data_f32
        })
    
    print(f"\nDataFrame summary:")
    print(f"Shape: {df.shape}")
    print(f"Value statistics:")
    print(f"  Total values: {len(df)}")
    print(f"  Zero values: {len(df[df.value == 0])}")
    print(f"  Non-zero values: {len(df[df.value != 0])}")
    if len(df[df.value != 0]) > 0:
        print(f"  Non-zero range: {df[df.value != 0].value.min()} to {df[df.value != 0].value.max()}")
    
    print(f"\nFirst few data points:")
    print(df.head(10))
    
    # Plot the data (if enabled)
    if ENABLE_PLOT:
        print("\n=== Creating Plot ===")
        if 'timestamp' in df.columns:
            fig = px.line(df, x='timestamp', y='value', title='PMU Signal Data with Proper Timestamps')
            fig.show()
        else:
            fig = px.line(df, x='index', y='value', title='PMU Signal Data by Index')
            fig.show()
    else:
        print("\n=== Plot Disabled ===")
        print("Set ENABLE_PLOT = True in configuration to show plot")
    
    # Export CSV (if enabled)
    if EXPORT_CSV:
        print("\n=== Exporting CSV ===")
        try:
            # Create output directory if it doesn't exist
            script_dir = os.path.dirname(__file__)
            csv_output_path = os.path.join(script_dir, '..', '..', CSV_OUTPUT_DIR)
            csv_output_path = os.path.abspath(csv_output_path)
            
            os.makedirs(csv_output_path, exist_ok=True)
            
            # Generate CSV filename based on the signal filename
            csv_filename = os.path.splitext(os.path.basename(file_path))[0] + "_analysis.csv"
            csv_file_path = os.path.join(csv_output_path, csv_filename)
            
            # Export DataFrame to CSV
            df.to_csv(csv_file_path, index=False)
            print(f"CSV exported successfully to: {csv_file_path}")
            print(f"CSV contains {len(df)} rows and {len(df.columns)} columns")
            
        except Exception as e:
            print(f"Error exporting CSV: {e}")
    else:
        print("\n=== CSV Export Disabled ===")
        print("Set EXPORT_CSV = True in configuration to export CSV")
    
    return df

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    if SIGNAL_FILENAME == "LIST_FILES":
        print("Available signal files:")
        files = list_available_signal_files()
        for i, file in enumerate(files, 1):
            print(f"{i:2d}. {file}")
    else:
        # Build the complete file path
        file_path = build_file_path(PMU_DATA_PATH, SIGNAL_FILENAME)
        
        if os.path.exists(file_path):
            print(f"Analyzing: {SIGNAL_FILENAME}")
            df = analyze_pmu_file(file_path)
            print(f"\nAnalysis complete! DataFrame shape: {df.shape}")
            
            # Summary statistics
            if 'value' in df.columns:
                zero_count = len(df[df.value == 0])
                non_zero_count = len(df[df.value != 0])
                print(f"Zero values: {zero_count}")
                print(f"Non-zero values: {non_zero_count}")
                if non_zero_count > 0:
                    print(f"Value range: {df.value.min()} to {df.value.max()}")
                    print(f"Unique values: {df.value.unique()}")
        else:
            print(f"File not found: {file_path}")
            print("\nSet SIGNAL_FILENAME = 'LIST_FILES' to see available files")
