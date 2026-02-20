"""
Add enhanced diagnostics to calculate_time_varying_harmonics function in both notebooks
to investigate why only Phase C shows harmonics.
"""
import json
import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
NOTEBOOKS = [
    os.path.join(REPO_ROOT, 'src', 'analysis', 'harmonics-study_test_9B_moxion.ipynb'),
    os.path.join(REPO_ROOT, 'src', 'analysis', 'harmonics-study_test_9C.ipynb'),
]

def find_cell_with_function(nb, func_name):
    """Find the cell index containing the function definition."""
    for i, cell in enumerate(nb['cells']):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            if f'def {func_name}(' in source:
                return i, source
    return None, None

def add_diagnostics_to_function(source):
    """Add enhanced diagnostics to the calculate_time_varying_harmonics function."""
    
    # Add pre-processing diagnostics after the empty check
    old_check = 'if waveform_df.empty:\n        raise ValueError("No waveform data available for harmonics calculation")\n    \n    # Calculate sampling rate'
    new_check = '''if waveform_df.empty:
        raise ValueError("No waveform data available for harmonics calculation")
    
    # Enhanced diagnostics: Check data availability and statistics BEFORE processing
    print("\\n=== PRE-PROCESSING DIAGNOSTICS ===")
    current_phases = ['PhaseA_Current', 'PhaseB_Current', 'PhaseC_Current']
    for phase in current_phases:
        if phase in waveform_df.columns:
            phase_data = waveform_df[phase].dropna()
            if len(phase_data) > 0:
                print(f"{phase}:")
                print(f"  Data points: {len(phase_data)}")
                print(f"  Min: {phase_data.min():.6f}, Max: {phase_data.max():.6f}")
                print(f"  Mean: {phase_data.mean():.6f}, Std: {phase_data.std():.6f}")
                print(f"  Non-zero count: {(phase_data != 0).sum()} ({(phase_data != 0).sum()/len(phase_data)*100:.1f}%)")
            else:
                print(f"{phase}: No data (all NaN)")
        else:
            print(f"{phase}: Column not found in waveform_df")
    print("=" * 40)
    
    # Calculate sampling rate'''
    
    if old_check in source:
        source = source.replace(old_check, new_check)
    
    # Change zero check to use threshold
    old_zero_check = 'if fundamental_magnitude == 0:\n                continue'
    new_zero_check = '''# Use threshold instead of exact zero check
            FUNDAMENTAL_THRESHOLD = 1e-10
            if fundamental_magnitude < FUNDAMENTAL_THRESHOLD:
                windows_skipped_zero_fundamental += 1
                continue
            
            windows_processed += 1'''
    
    # But first, we need to add tracking variables before the loop
    old_loop_start = 'for phase in current_phases:\n        if phase not in waveform_df.columns:\n            continue\n        \n        print(f"\\nProcessing {phase}...")\n        phase_data = waveform_df[phase].dropna()\n        \n        if len(phase_data) < samples_per_window:\n            print(f"Warning: Not enough data for {phase}")\n            continue\n        \n        # Slide window across data'
    new_loop_start = '''for phase in current_phases:
        if phase not in waveform_df.columns:
            print(f"Warning: {phase} not found in waveform_df columns: {list(waveform_df.columns)}")
            continue
        
        print(f"\\nProcessing {phase}...")
        phase_data = waveform_df[phase].dropna()
        
        if len(phase_data) < samples_per_window:
            print(f"Warning: Not enough data for {phase}")
            continue
        
        # Track statistics for this phase
        windows_processed = 0
        windows_skipped_zero_fundamental = 0
        fundamental_magnitudes = []
        
        # Slide window across data'''
    
    if old_loop_start in source:
        source = source.replace(old_loop_start, new_loop_start)
    
    # Add threshold constant before results_list
    old_results = 'results_list = []\n    current_phases = [\'PhaseA_Current\', \'PhaseB_Current\', \'PhaseC_Current\']'
    new_results = '''results_list = []
    # Use a small threshold instead of exact zero to handle very small fundamental magnitudes
    FUNDAMENTAL_THRESHOLD = 1e-10
    current_phases = ['PhaseA_Current', 'PhaseB_Current', 'PhaseC_Current']'''
    
    if old_results in source:
        source = source.replace(old_results, new_results)
    
    # Update zero check
    if 'if fundamental_magnitude == 0:' in source:
        source = source.replace(
            'if fundamental_magnitude == 0:\n                continue',
            '''fundamental_magnitudes.append(fundamental_magnitude)
            
            # Use threshold instead of exact zero check
            if fundamental_magnitude < FUNDAMENTAL_THRESHOLD:
                windows_skipped_zero_fundamental += 1
                continue
            
            windows_processed += 1'''
        )
    
    # Add phase summary after the loop
    old_append = '**top_harmonics\n            })\n    \n    if not results_list:'
    new_append = '''**top_harmonics
            })
        
        # Print phase-specific diagnostics
        if fundamental_magnitudes:
            avg_fundamental = np.mean(fundamental_magnitudes)
            min_fundamental = np.min(fundamental_magnitudes)
            max_fundamental = np.max(fundamental_magnitudes)
            print(f"  {phase} processing summary:")
            print(f"    Windows processed: {windows_processed}")
            print(f"    Windows skipped (zero fundamental): {windows_skipped_zero_fundamental}")
            print(f"    Fundamental magnitude - Min: {min_fundamental:.6f}, Max: {max_fundamental:.6f}, Avg: {avg_fundamental:.6f}")
        else:
            print(f"  {phase}: No windows processed (all had zero fundamental)")
    
    if not results_list:'''
    
    if old_append in source:
        source = source.replace(old_append, new_append)
    
    # Update post-processing diagnostics header
    if 'print("\\nDiagnostic: Time-varying harmonics by phase:")' in source:
        source = source.replace(
            'print("\\nDiagnostic: Time-varying harmonics by phase:")',
            'print("\\n=== POST-PROCESSING DIAGNOSTICS ===")\n    print("Time-varying harmonics by phase:")'
        )
    
    # Add closing separator
    if 'print(f"  {phase_name}: No data found!")\n    \n    return results_df' in source:
        source = source.replace(
            'print(f"  {phase_name}: No data found!")\n    \n    return results_df',
            'print(f"  {phase_name}: No data found!")\n    print("=" * 40)\n    \n    return results_df'
        )
    
    return source

def main():
    for notebook_path in NOTEBOOKS:
        if not os.path.exists(notebook_path):
            print(f"Warning: Notebook not found: {notebook_path}")
            continue
        
        print(f"Processing {notebook_path}...")
        
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        # Find the cell with calculate_time_varying_harmonics
        cell_idx, source = find_cell_with_function(nb, 'calculate_time_varying_harmonics')
        
        if cell_idx is None:
            print(f"  Warning: calculate_time_varying_harmonics function not found")
            continue
        
        # Modify the function
        new_source = add_diagnostics_to_function(source)
        
        if new_source == source:
            print(f"  No changes made (function may have already been modified)")
        else:
            # Update the cell - preserve the original format (list of strings)
            # Split by newlines but don't keep the newline characters
            new_lines = new_source.split('\n')
            # Add newline to all but the last line to match notebook format
            nb['cells'][cell_idx]['source'] = [line + '\n' for line in new_lines[:-1]] + ([new_lines[-1]] if new_lines[-1] else [])
            
            # Write back
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(nb, f, indent=1, ensure_ascii=False)
            
            print(f"  Updated calculate_time_varying_harmonics function with enhanced diagnostics")

if __name__ == '__main__':
    main()
