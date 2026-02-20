"""
Add worst case analysis functions to both notebooks.
"""
import json
import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
NOTEBOOKS = [
    os.path.join(REPO_ROOT, 'src', 'analysis', 'harmonics-study_test_9B_moxion.ipynb'),
    os.path.join(REPO_ROOT, 'src', 'analysis', 'harmonics-study_test_9C.ipynb'),
]

WORST_CASE_CURRENT_FUNCTION = '''def analyze_worst_case_current_harmonics(time_varying_harmonics_df, waveform_df=None, loadbank_df=None):
    """
    Identify worst case scenario for current harmonics and calculate impact metrics.
    
    Args:
        time_varying_harmonics_df: DataFrame with time-varying current harmonics
        waveform_df: Optional DataFrame with waveform data for calculating RMS current
        loadbank_df: Optional DataFrame with loadbank data for load condition correlation
    
    Returns:
        dict: Dictionary with worst case analysis results
    """
    print("\\n" + "="*70)
    print("WORST CASE CURRENT HARMONICS ANALYSIS")
    print("="*70)
    
    if time_varying_harmonics_df.empty:
        print("Warning: No time-varying harmonics data available")
        return None
    
    # Find maximum THD across all phases and time windows
    max_thd_idx = time_varying_harmonics_df['thd'].idxmax()
    worst_case = time_varying_harmonics_df.loc[max_thd_idx]
    
    # Extract worst case details
    worst_phase = worst_case['phase']
    worst_timestamp = worst_case.name if hasattr(worst_case, 'name') else max_thd_idx
    max_thd = worst_case['thd']
    
    # Get top harmonics at worst case
    harmonic_cols = [col for col in time_varying_harmonics_df.columns if col.startswith('H')]
    top_harmonics = {}
    for h_col in harmonic_cols[:5]:
        if h_col in worst_case:
            top_harmonics[h_col] = worst_case[h_col]
    
    # Get load conditions if available
    load_condition = None
    if loadbank_df is not None and not loadbank_df.empty:
        # Find nearest loadbank timestamp
        try:
            nearest_idx = loadbank_df.index.get_indexer([worst_timestamp], method='nearest')[0]
            if nearest_idx >= 0:
                load_row = loadbank_df.iloc[nearest_idx]
                load_condition = {
                    'R_kw': load_row.get('resistive_kw (kW)', 0) if 'resistive_kw (kW)' in load_row else 0,
                    'L_kvar': load_row.get('inductive_kvar (kVAR)', 0) if 'inductive_kvar (kVAR)' in load_row else 0,
                    'C_kvar': load_row.get('capacitive_kvar (kVAR)', 0) if 'capacitive_kvar (kVAR)' in load_row else 0
                }
        except Exception as e:
            print(f"Warning: Could not get load condition: {e}")
    
    # Calculate impact metrics
    # Extra Current: I_RMS_total = I_fundamental * sqrt(1 + (THD/100)^2)
    # Extra current percentage = (sqrt(1 + (THD/100)^2) - 1) * 100
    thd_ratio = max_thd / 100.0
    i_rms_total_ratio = np.sqrt(1 + thd_ratio**2)
    extra_current_pct = (i_rms_total_ratio - 1) * 100
    
    # Heating factor = (I_RMS_total / I_fundamental)^2 = 1 + (THD/100)^2
    heating_factor = 1 + thd_ratio**2
    
    # Print summary
    print(f"\\nWorst Case Identified:")
    print(f"  Phase: {worst_phase}")
    print(f"  Timestamp: {worst_timestamp}")
    print(f"  Maximum THD: {max_thd:.2f}%")
    if load_condition:
        print(f"  Load Condition: R={load_condition['R_kw']:.1f} kW, L={load_condition['L_kvar']:.1f} kVAR, C={load_condition['C_kvar']:.1f} kVAR")
    
    print(f"\\nTop Harmonics at Worst Case:")
    for h_name, h_value in sorted(top_harmonics.items(), key=lambda x: x[1], reverse=True):
        print(f"  {h_name}: {h_value:.2f}% of fundamental")
    
    print(f"\\nImpact Analysis:")
    print(f"  Extra Current Induced: {extra_current_pct:.2f}% increase")
    print(f"  Excess Line Heating Factor: {heating_factor:.2f}x (compared to fundamental-only)")
    print(f"  I²R Loss Increase: {heating_factor:.2f}x")
    print("="*70)
    
    # Return dictionary for use in figures
    return {
        'phase': worst_phase,
        'timestamp': worst_timestamp,
        'max_thd': max_thd,
        'load_condition': load_condition,
        'top_harmonics': top_harmonics,
        'extra_current_pct': extra_current_pct,
        'heating_factor': heating_factor
    }
'''

WORST_CASE_VOLTAGE_FUNCTION = '''def analyze_worst_case_voltage_harmonics(time_varying_voltage_harmonics_df, loadbank_df=None):
    """
    Identify worst case scenario for voltage harmonics.
    
    Args:
        time_varying_voltage_harmonics_df: DataFrame with time-varying voltage harmonics
        loadbank_df: Optional DataFrame with loadbank data for load condition correlation
    
    Returns:
        dict: Dictionary with worst case analysis results
    """
    print("\\n" + "="*70)
    print("WORST CASE VOLTAGE HARMONICS ANALYSIS")
    print("="*70)
    
    if time_varying_voltage_harmonics_df.empty:
        print("Warning: No time-varying voltage harmonics data available")
        return None
    
    # Find maximum THD across all phases and time windows
    max_thd_idx = time_varying_voltage_harmonics_df['thd'].idxmax()
    worst_case = time_varying_voltage_harmonics_df.loc[max_thd_idx]
    
    # Extract worst case details
    worst_phase = worst_case['phase']
    worst_timestamp = worst_case.name if hasattr(worst_case, 'name') else max_thd_idx
    max_thd = worst_case['thd']
    
    # Get top harmonics at worst case
    harmonic_cols = [col for col in time_varying_voltage_harmonics_df.columns if col.startswith('H')]
    top_harmonics = {}
    for h_col in harmonic_cols[:5]:
        if h_col in worst_case:
            top_harmonics[h_col] = worst_case[h_col]
    
    # Get load conditions if available
    load_condition = None
    if loadbank_df is not None and not loadbank_df.empty:
        try:
            nearest_idx = loadbank_df.index.get_indexer([worst_timestamp], method='nearest')[0]
            if nearest_idx >= 0:
                load_row = loadbank_df.iloc[nearest_idx]
                load_condition = {
                    'R_kw': load_row.get('resistive_kw (kW)', 0) if 'resistive_kw (kW)' in load_row else 0,
                    'L_kvar': load_row.get('inductive_kvar (kVAR)', 0) if 'inductive_kvar (kVAR)' in load_row else 0,
                    'C_kvar': load_row.get('capacitive_kvar (kVAR)', 0) if 'capacitive_kvar (kVAR)' in load_row else 0
                }
        except Exception as e:
            print(f"Warning: Could not get load condition: {e}")
    
    # Print summary
    print(f"\\nWorst Case Identified:")
    print(f"  Phase: {worst_phase}")
    print(f"  Timestamp: {worst_timestamp}")
    print(f"  Maximum THD: {max_thd:.2f}%")
    if load_condition:
        print(f"  Load Condition: R={load_condition['R_kw']:.1f} kW, L={load_condition['L_kvar']:.1f} kVAR, C={load_condition['C_kvar']:.1f} kVAR")
    
    print(f"\\nTop Harmonics at Worst Case:")
    for h_name, h_value in sorted(top_harmonics.items(), key=lambda x: x[1], reverse=True):
        print(f"  {h_name}: {h_value:.2f}% of fundamental")
    
    print("="*70)
    
    # Return dictionary for use in figures
    return {
        'phase': worst_phase,
        'timestamp': worst_timestamp,
        'max_thd': max_thd,
        'load_condition': load_condition,
        'top_harmonics': top_harmonics
    }
'''

def find_insertion_point(nb, after_func_name):
    """Find cell index after the specified function."""
    for i, cell in enumerate(nb['cells']):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            if f'def {after_func_name}(' in source:
                return i + 1
    return None

def add_new_cell(nb, cell_idx, source_code, cell_id):
    """Add a new code cell at the specified index."""
    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": source_code.splitlines(keepends=True) if isinstance(source_code, str) else source_code
    }
    nb['cells'].insert(cell_idx, new_cell)
    return nb

def main():
    for notebook_path in NOTEBOOKS:
        if not os.path.exists(notebook_path):
            print(f"Warning: Notebook not found: {notebook_path}")
            continue
        
        print(f"Processing {notebook_path}...")
        
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        # Check if functions already exist
        all_source = ''.join([''.join(cell.get('source', [])) for cell in nb['cells'] if cell.get('cell_type') == 'code'])
        
        if 'def analyze_worst_case_current_harmonics(' in all_source:
            print(f"  Worst case current function already exists, skipping")
        else:
            # Find insertion point (after calculate_time_varying_harmonics)
            insert_idx = find_insertion_point(nb, 'calculate_time_varying_harmonics')
            if insert_idx:
                nb = add_new_cell(nb, insert_idx, WORST_CASE_CURRENT_FUNCTION, 'worst_case_current_func')
                print(f"  Added analyze_worst_case_current_harmonics function")
            else:
                print(f"  Warning: Could not find insertion point for current function")
        
        if 'def analyze_worst_case_voltage_harmonics(' in all_source:
            print(f"  Worst case voltage function already exists, skipping")
        else:
            # Find insertion point (after calculate_time_varying_voltage_harmonics)
            insert_idx = find_insertion_point(nb, 'calculate_time_varying_voltage_harmonics')
            if insert_idx:
                nb = add_new_cell(nb, insert_idx, WORST_CASE_VOLTAGE_FUNCTION, 'worst_case_voltage_func')
                print(f"  Added analyze_worst_case_voltage_harmonics function")
            else:
                print(f"  Warning: Could not find insertion point for voltage function")
        
        # Write back
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        
        print(f"  Saved notebook")

if __name__ == '__main__':
    main()
