"""
PMU Data Processing Utilities

This module provides utility functions for reading and processing PMU (Phasor Measurement Unit) 
signal files. The functions handle .signal files that contain binary data and extract 
metadata from filenames to create proper timestamps.

USAGE EXAMPLES:
    # Basic usage - read a signal file into a DataFrame
    df = read_pmu_signal_file('path/to/file.signal')
    
    # Get file info without reading all data (faster)
    info = get_pmu_file_info('path/to/file.signal')
    
    # Safe reading (returns None on error instead of raising exception)
    df = read_pmu_signal_file_safe('path/to/file.signal')
    if df is not None:
        print(f"Successfully read {len(df)} data points")

FILENAME FORMAT:
    PMU signal files must follow this naming convention:
    YYYYMMDD,HHMMSS.microseconds,frequency,datatype.signal
    
    Example: 20250908,000000.000000000,60,Float32.signal
    - Date: September 8, 2025
    - Time: 00:00:00.000000000 (midnight)
    - Frequency: 60 Hz sampling rate
    - Data type: Float32 (32-bit floating point)

ERROR HANDLING:
    - PMUDataError: Custom exception for PMU-specific errors
    - File validation: Checks for .signal extension and file existence
    - Filename parsing: Validates date/time format and frequency
    - Data type validation: Supports multiple numeric data types

RETURNED DATAFRAME:
    The DataFrame contains two columns:
    - 'timestamp': Pandas datetime index with proper time progression
    - 'value': Signal values as read from the binary file

Author: Generated for Green Construction Task 5
Date: September 2025
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PMUDataError(Exception):
    """Custom exception for PMU data processing errors"""
    pass


def validate_signal_file(file_path: str) -> None:
    """
    Validate that the file exists and has the correct .signal extension.
    
    Args:
        file_path (str): Path to the signal file
        
    Raises:
        PMUDataError: If file doesn't exist or has wrong extension
    """
    if not os.path.exists(file_path):
        raise PMUDataError(f"Signal file not found: {file_path}")
    
    if not file_path.endswith('.signal'):
        raise PMUDataError(f"File must have .signal extension, got: {os.path.basename(file_path)}")
    
    if os.path.getsize(file_path) == 0:
        raise PMUDataError(f"Signal file is empty: {file_path}")


def parse_signal_filename(filename: str) -> Tuple[str, str, int, str]:
    """
    Parse PMU signal filename to extract metadata.
    
    Expected filename format: YYYYMMDD,HHMMSS.microseconds,frequency,datatype.signal
    Example: 20250908,000000.000000000,60,Float32.signal
    
    Args:
        filename (str): The signal filename (with or without .signal extension)
        
    Returns:
        Tuple[str, str, int, str]: (date_str, time_str, frequency, data_type)
        
    Raises:
        PMUDataError: If filename format is invalid
    """
    # Remove .signal extension if present
    if filename.endswith('.signal'):
        filename = filename[:-7]
    
    parts = filename.split(',')
    
    if len(parts) < 4:
        raise PMUDataError(
            f"Invalid filename format. Expected 'YYYYMMDD,HHMMSS.microseconds,frequency,datatype.signal', "
            f"got: {filename}"
        )
    
    date_str = parts[0].strip()
    time_str = parts[1].strip()
    frequency_str = parts[2].strip()
    data_type = parts[3].strip()
    
    # Validate date format
    if len(date_str) != 8 or not date_str.isdigit():
        raise PMUDataError(f"Invalid date format in filename. Expected YYYYMMDD, got: {date_str}")
    
    # Validate and convert frequency
    try:
        frequency = int(frequency_str)
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
    except ValueError as e:
        raise PMUDataError(f"Invalid frequency in filename: {frequency_str}. Error: {e}")
    
    # Validate time format
    time_parts = time_str.split('.')
    if len(time_parts[0]) != 6 or not time_parts[0].isdigit():
        raise PMUDataError(f"Invalid time format in filename. Expected HHMMSS, got: {time_parts[0]}")
    
    return date_str, time_str, frequency, data_type


def create_start_datetime(date_str: str, time_str: str) -> datetime:
    """
    Create a datetime object from date and time strings extracted from filename.
    
    Args:
        date_str (str): Date string in YYYYMMDD format
        time_str (str): Time string in HHMMSS.microseconds format
        
    Returns:
        datetime: The start datetime for the signal data
        
    Raises:
        PMUDataError: If datetime parsing fails
    """
    try:
        # Parse date
        start_date = datetime.strptime(date_str, "%Y%m%d")
        
        # Parse time
        time_parts = time_str.split('.')
        time_component = time_parts[0]
        
        if len(time_component) != 6:
            raise ValueError(f"Time component must be 6 digits (HHMMSS), got: {time_component}")
        
        hours = int(time_component[:2])
        minutes = int(time_component[2:4])
        seconds = int(time_component[4:6])
        
        # Handle microseconds if present
        microseconds = 0
        if len(time_parts) > 1:
            # Convert fractional seconds to microseconds
            fractional_seconds = float('0.' + time_parts[1])
            microseconds = int(fractional_seconds * 1000000)
        
        # Validate time values
        if not (0 <= hours <= 23):
            raise ValueError(f"Hours must be 0-23, got: {hours}")
        if not (0 <= minutes <= 59):
            raise ValueError(f"Minutes must be 0-59, got: {minutes}")
        if not (0 <= seconds <= 59):
            raise ValueError(f"Seconds must be 0-59, got: {seconds}")
        
        start_datetime = start_date.replace(
            hour=hours, 
            minute=minutes, 
            second=seconds, 
            microsecond=microseconds
        )
        
        return start_datetime
        
    except ValueError as e:
        raise PMUDataError(f"Failed to parse datetime from filename parts '{date_str}', '{time_str}': {e}")


def read_signal_data(file_path: str, data_type: str = "Float32") -> np.ndarray:
    """
    Read binary signal data from file.
    
    Args:
        file_path (str): Path to the signal file
        data_type (str): Data type for reading binary data (default: Float32)
        
    Returns:
        np.ndarray: Array of signal values
        
    Raises:
        PMUDataError: If data reading fails
    """
    try:
        # Map data types to numpy dtypes
        dtype_mapping = {
            'Float32': np.float32,
            'Float64': np.float64,
            'Int32': np.int32,
            'Int16': np.int16,
            'UInt32': np.uint32,
            'UInt16': np.uint16
        }
        
        if data_type not in dtype_mapping:
            logger.warning(f"Unknown data type '{data_type}', defaulting to Float32")
            dtype = np.float32
        else:
            dtype = dtype_mapping[data_type]
        
        # Read binary data
        data = np.fromfile(file_path, dtype=dtype)
        
        if len(data) == 0:
            raise PMUDataError(f"No data could be read from file: {file_path}")
        
        return data
        
    except Exception as e:
        raise PMUDataError(f"Failed to read signal data from {file_path}: {e}")


def create_timestamps(start_datetime: datetime, num_points: int, frequency: int) -> pd.DatetimeIndex:
    """
    Create timestamps for signal data points based on sampling frequency.
    
    Args:
        start_datetime (datetime): Start time for the signal
        num_points (int): Number of data points
        frequency (int): Sampling frequency in Hz
        
    Returns:
        pd.DatetimeIndex: Array of timestamps
        
    Raises:
        PMUDataError: If timestamp creation fails
    """
    try:
        if frequency <= 0:
            raise ValueError(f"Frequency must be positive, got: {frequency}")
        
        if num_points <= 0:
            raise ValueError(f"Number of points must be positive, got: {num_points}")
        
        # Calculate time interval between samples
        time_interval = pd.Timedelta(seconds=1.0 / frequency)
        
        # Generate timestamps
        timestamps = pd.date_range(
            start=start_datetime,
            periods=num_points,
            freq=time_interval
        )
        
        return timestamps
        
    except Exception as e:
        raise PMUDataError(f"Failed to create timestamps: {e}")


def read_pmu_signal_file(file_path: str) -> pd.DataFrame:
    """
    Read a PMU signal file and return a DataFrame with timestamps and values.
    
    This is the main function that combines all the processing steps:
    1. Validate the file
    2. Parse filename for metadata
    3. Create start datetime
    4. Read signal data
    5. Create timestamps
    6. Return DataFrame
    
    Args:
        file_path (str): Path to the .signal file
        
    Returns:
        pd.DataFrame: DataFrame with 'timestamp' and 'value' columns
        
    Raises:
        PMUDataError: If any step in the processing fails
    """
    try:
        # Step 1: Validate file
        validate_signal_file(file_path)
        logger.info(f"Processing PMU signal file: {file_path}")
        
        # Step 2: Parse filename
        filename = os.path.basename(file_path)
        date_str, time_str, frequency, data_type = parse_signal_filename(filename)
        logger.info(f"Parsed metadata - Date: {date_str}, Time: {time_str}, Frequency: {frequency}Hz, Type: {data_type}")
        
        # Step 3: Create start datetime
        start_datetime = create_start_datetime(date_str, time_str)
        logger.info(f"Start datetime: {start_datetime}")
        
        # Step 4: Read signal data
        signal_data = read_signal_data(file_path, data_type)
        logger.info(f"Read {len(signal_data)} data points, range: {signal_data.min()} to {signal_data.max()}")
        
        # Step 5: Create timestamps
        timestamps = create_timestamps(start_datetime, len(signal_data), frequency)
        
        # Step 6: Create DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'value': signal_data
        })
        
        # Log summary statistics
        zero_count = len(df[df.value == 0])
        non_zero_count = len(df[df.value != 0])
        logger.info(f"DataFrame created - Shape: {df.shape}, Zero values: {zero_count}, Non-zero values: {non_zero_count}")
        
        if non_zero_count > 0:
            non_zero_data = df[df.value != 0].value
            logger.info(f"Non-zero value range: {non_zero_data.min()} to {non_zero_data.max()}")
        
        return df
        
    except PMUDataError:
        # Re-raise PMU-specific errors
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise PMUDataError(f"Unexpected error processing PMU signal file {file_path}: {e}")


def read_pmu_signal_file_safe(file_path: str) -> Optional[pd.DataFrame]:
    """
    Safe version of read_pmu_signal_file that returns None on error instead of raising exceptions.
    
    Args:
        file_path (str): Path to the .signal file
        
    Returns:
        Optional[pd.DataFrame]: DataFrame with signal data, or None if processing failed
    """
    try:
        return read_pmu_signal_file(file_path)
    except PMUDataError as e:
        logger.error(f"PMU processing error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def get_pmu_file_info(file_path: str) -> dict:
    """
    Get metadata information about a PMU signal file without reading the full data.
    
    Args:
        file_path (str): Path to the .signal file
        
    Returns:
        dict: Dictionary containing file metadata
        
    Raises:
        PMUDataError: If file validation or parsing fails
    """
    validate_signal_file(file_path)
    
    filename = os.path.basename(file_path)
    date_str, time_str, frequency, data_type = parse_signal_filename(filename)
    start_datetime = create_start_datetime(date_str, time_str)
    
    file_size = os.path.getsize(file_path)
    
    # Estimate number of data points based on file size and data type
    dtype_sizes = {
        'Float32': 4, 'Float64': 8, 'Int32': 4, 'Int16': 2, 'UInt32': 4, 'UInt16': 2
    }
    bytes_per_point = dtype_sizes.get(data_type, 4)  # Default to 4 bytes
    estimated_points = file_size // bytes_per_point
    
    # Calculate estimated duration
    estimated_duration_seconds = estimated_points / frequency if frequency > 0 else 0
    
    return {
        'file_path': file_path,
        'filename': filename,
        'file_size_bytes': file_size,
        'date': date_str,
        'time': time_str,
        'start_datetime': start_datetime,
        'frequency_hz': frequency,
        'data_type': data_type,
        'estimated_data_points': estimated_points,
        'estimated_duration_seconds': estimated_duration_seconds,
        'bytes_per_point': bytes_per_point
    }


# Convenience function for backward compatibility
def analyze_pmu_file(file_path: str) -> pd.DataFrame:
    """
    Alias for read_pmu_signal_file for backward compatibility.
    
    Args:
        file_path (str): Path to the .signal file
        
    Returns:
        pd.DataFrame: DataFrame with signal data
    """
    return read_pmu_signal_file(file_path)
