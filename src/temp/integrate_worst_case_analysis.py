"""
Integrate worst case analysis calls and add worst case tables to figures.
"""
import json
import os
import sys
import re

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
NOTEBOOKS = [
    os.path.join(REPO_ROOT, 'src', 'analysis', 'harmonics-study_test_9B_moxion.ipynb'),
    os.path.join(REPO_ROOT, 'src', 'analysis', 'harmonics-study_test_9C.ipynb'),
]

def find_cell_with_pattern(nb, pattern):
    """Find cell containing the pattern."""
    for i, cell in enumerate(nb['cells']):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            if pattern in source:
                return i, source
    return None, None

def add_worst_case_call_after_current(nb):
    """Add worst case analysis call after time_varying_harmonics_df calculation."""
    # Find cell that calculates time_varying_harmonics_df
    cell_idx, source = find_cell_with_pattern(nb, 'time_varying_harmonics_df = calculate_time_varying_harmonics')
    
    if cell_idx is None:
        return False
    
    # Check if call already exists
    if 'worst_case_current = analyze_worst_case_current_harmonics' in source:
        return False
    
    # Add call after the calculation
    # Find the end of the cell (look for next cell or end of source)
    lines = source.split('\n')
    new_lines = []
    added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        # Add after the assignment line
        if 'time_varying_harmonics_df = calculate_time_varying_harmonics' in line and not added:
            # Add blank line and worst case call
            new_lines.append('')
            new_lines.append('# Analyze worst case current harmonics')
            new_lines.append('worst_case_current = analyze_worst_case_current_harmonics(')
            new_lines.append('    time_varying_harmonics_df,')
            new_lines.append('    waveform_df=waveform_harmonics if \'waveform_harmonics\' in locals() else None,')
            new_lines.append('    loadbank_df=loadbank_df if \'loadbank_df\' in locals() else None')
            new_lines.append(')')
            added = True
    
    if added:
        nb['cells'][cell_idx]['source'] = [l + '\n' for l in new_lines[:-1]] + ([new_lines[-1]] if new_lines[-1] else [])
        return True
    
    return False

def add_worst_case_call_after_voltage(nb):
    """Add worst case analysis call after time_varying_voltage_harmonics_df calculation."""
    # Find cell that calculates time_varying_voltage_harmonics_df
    cell_idx, source = find_cell_with_pattern(nb, 'time_varying_voltage_harmonics_df = calculate_time_varying_voltage_harmonics')
    
    if cell_idx is None:
        return False
    
    # Check if call already exists
    if 'worst_case_voltage = analyze_worst_case_voltage_harmonics' in source:
        return False
    
    # Add call after the calculation
    lines = source.split('\n')
    new_lines = []
    added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        if 'time_varying_voltage_harmonics_df = calculate_time_varying_voltage_harmonics' in line and not added:
            new_lines.append('')
            new_lines.append('# Analyze worst case voltage harmonics')
            new_lines.append('worst_case_voltage = analyze_worst_case_voltage_harmonics(')
            new_lines.append('    time_varying_voltage_harmonics_df,')
            new_lines.append('    loadbank_df=loadbank_df if \'loadbank_df\' in locals() else None')
            new_lines.append(')')
            added = True
    
    if added:
        nb['cells'][cell_idx]['source'] = [l + '\n' for l in new_lines[:-1]] + ([new_lines[-1]] if new_lines[-1] else [])
        return True
    
    return False

def add_worst_case_table_to_current_plot(nb):
    """Add worst case table to current harmonics plot."""
    cell_idx, source = find_cell_with_pattern(nb, 'def plot_harmonics_vs_time')
    
    if cell_idx is None:
        return False
    
    # Check if table already added
    if 'go.Table' in source and 'worst_case_current' in source:
        return False
    
    # Find where to add the table (before the return statement)
    # We'll add it as a 5th subplot row
    if 'rows=4, cols=1' in source:
        # Change to 5 rows
        source = source.replace('rows=4, cols=1', 'rows=5, cols=1')
        source = source.replace(
            'specs=[[{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}]]',
            'specs=[[{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}]]'
        )
        # Update subplot titles
        source = source.replace(
            "subplot_titles=(\n            'Current Total Harmonic Distortion (THD) vs Time',\n            'Power Measurements vs Time',\n            'Loadbank Load Profile vs Time',\n            'Top 5 Harmonics vs Time'\n        ),",
            "subplot_titles=(\n            'Current Total Harmonic Distortion (THD) vs Time',\n            'Power Measurements vs Time',\n            'Loadbank Load Profile vs Time',\n            'Top 5 Harmonics vs Time',\n            'Worst Case Summary'\n        ),"
        )
    
    # Add table before return statement
    table_code = '''
    # Plot 5: Worst case summary table
    if worst_case_current is not None and isinstance(worst_case_current, dict):
        # Create table data
        table_data = []
        table_data.append(['Phase', worst_case_current.get('phase', 'N/A')])
        table_data.append(['Timestamp', str(worst_case_current.get('timestamp', 'N/A'))])
        table_data.append(['Max THD', f"{worst_case_current.get('max_thd', 0):.2f}%"])
        
        # Add top harmonics
        top_harmonics = worst_case_current.get('top_harmonics', {})
        if top_harmonics:
            harmonics_str = ', '.join([f"{k}: {v:.1f}%" for k, v in sorted(top_harmonics.items(), key=lambda x: x[1], reverse=True)[:3]])
            table_data.append(['Top Harmonics', harmonics_str])
        
        # Add load condition if available
        load_cond = worst_case_current.get('load_condition')
        if load_cond:
            table_data.append(['Load Condition', f"R={load_cond.get('R_kw', 0):.1f}kW, L={load_cond.get('L_kvar', 0):.1f}kVAR, C={load_cond.get('C_kvar', 0):.1f}kVAR"])
        
        # Add impact metrics
        table_data.append(['Extra Current', f"{worst_case_current.get('extra_current_pct', 0):.2f}%"])
        table_data.append(['Heating Factor', f"{worst_case_current.get('heating_factor', 1):.2f}x"])
        
        # Create table
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'], fill_color='lightblue', align='left', font=dict(size=12)),
                cells=dict(values=list(zip(*table_data)), fill_color='white', align='left', font=dict(size=11)),
                columnwidth=[0.3, 0.7]
            ),
            row=5, col=1
        )
    '''
    
    # Insert before return statement
    if 'return fig' in source and table_code.strip() not in source:
        source = source.replace('    return fig', table_code + '\n    \n    return fig')
        nb['cells'][cell_idx]['source'] = source.splitlines(keepends=True) if isinstance(source, str) else source
        return True
    
    return False

def add_worst_case_table_to_voltage_plot(nb):
    """Add worst case table to voltage harmonics plot."""
    cell_idx, source = find_cell_with_pattern(nb, 'def plot_voltage_harmonics_vs_time')
    
    if cell_idx is None:
        return False
    
    # Similar to current plot but simpler (no impact metrics)
    if 'rows=4, cols=1' in source and 'worst_case_voltage' not in source:
        source = source.replace('rows=4, cols=1', 'rows=5, cols=1')
        source = source.replace(
            'specs=[[{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}]]',
            'specs=[[{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}],\n               [{"secondary_y": False}]]'
        )
        source = source.replace(
            "subplot_titles=(\n            'Voltage Total Harmonic Distortion (THD) vs Time',\n            'Power Measurements vs Time',\n            'Loadbank Load Profile vs Time',\n            'Top 5 Harmonics vs Time'\n        ),",
            "subplot_titles=(\n            'Voltage Total Harmonic Distortion (THD) vs Time',\n            'Power Measurements vs Time',\n            'Loadbank Load Profile vs Time',\n            'Top 5 Harmonics vs Time',\n            'Worst Case Summary'\n        ),"
        )
        
        table_code = '''
    # Plot 5: Worst case summary table
    if worst_case_voltage is not None and isinstance(worst_case_voltage, dict):
        table_data = []
        table_data.append(['Phase', worst_case_voltage.get('phase', 'N/A')])
        table_data.append(['Timestamp', str(worst_case_voltage.get('timestamp', 'N/A'))])
        table_data.append(['Max THD', f"{worst_case_voltage.get('max_thd', 0):.2f}%"])
        
        top_harmonics = worst_case_voltage.get('top_harmonics', {})
        if top_harmonics:
            harmonics_str = ', '.join([f"{k}: {v:.1f}%" for k, v in sorted(top_harmonics.items(), key=lambda x: x[1], reverse=True)[:3]])
            table_data.append(['Top Harmonics', harmonics_str])
        
        load_cond = worst_case_voltage.get('load_condition')
        if load_cond:
            table_data.append(['Load Condition', f"R={load_cond.get('R_kw', 0):.1f}kW, L={load_cond.get('L_kvar', 0):.1f}kVAR, C={load_cond.get('C_kvar', 0):.1f}kVAR"])
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'], fill_color='lightblue', align='left', font=dict(size=12)),
                cells=dict(values=list(zip(*table_data)), fill_color='white', align='left', font=dict(size=11)),
                columnwidth=[0.3, 0.7]
            ),
            row=5, col=1
        )
    '''
        
        if 'return fig' in source:
            source = source.replace('    return fig', table_code + '\n    \n    return fig')
            nb['cells'][cell_idx]['source'] = source.splitlines(keepends=True) if isinstance(source, str) else source
            return True
    
    return False

def update_plot_function_signatures(nb):
    """Update plot function signatures to accept worst_case parameters."""
    # Update plot_harmonics_vs_time signature
    cell_idx, source = find_cell_with_pattern(nb, 'def plot_harmonics_vs_time')
    if cell_idx and 'worst_case_current=None' not in source:
        source = source.replace(
            'def plot_harmonics_vs_time(time_varying_harmonics_df, power_df, loadbank_df):',
            'def plot_harmonics_vs_time(time_varying_harmonics_df, power_df, loadbank_df, worst_case_current=None):'
        )
        nb['cells'][cell_idx]['source'] = source.splitlines(keepends=True) if isinstance(source, str) else source
    
    # Update plot_voltage_harmonics_vs_time signature
    cell_idx, source = find_cell_with_pattern(nb, 'def plot_voltage_harmonics_vs_time')
    if cell_idx and 'worst_case_voltage=None' not in source:
        source = source.replace(
            'def plot_voltage_harmonics_vs_time(time_varying_harmonics_df, power_df, loadbank_df):',
            'def plot_voltage_harmonics_vs_time(time_varying_harmonics_df, power_df, loadbank_df, worst_case_voltage=None):'
        )
        nb['cells'][cell_idx]['source'] = source.splitlines(keepends=True) if isinstance(source, str) else source

def update_plot_calls(nb):
    """Update plot function calls to pass worst_case parameters."""
    # Find calls to plot_harmonics_vs_time
    for cell in nb['cells']:
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            if 'plot_harmonics_vs_time(' in source and 'worst_case_current=' not in source:
                # Add worst_case_current parameter
                source = re.sub(
                    r'plot_harmonics_vs_time\(([^)]+)\)',
                    r'plot_harmonics_vs_time(\1, worst_case_current=worst_case_current if \'worst_case_current\' in locals() else None)',
                    source
                )
                cell['source'] = source.splitlines(keepends=True) if isinstance(source, str) else source
            
            if 'plot_voltage_harmonics_vs_time(' in source and 'worst_case_voltage=' not in source:
                source = re.sub(
                    r'plot_voltage_harmonics_vs_time\(([^)]+)\)',
                    r'plot_voltage_harmonics_vs_time(\1, worst_case_voltage=worst_case_voltage if \'worst_case_voltage\' in locals() else None)',
                    source
                )
                cell['source'] = source.splitlines(keepends=True) if isinstance(source, str) else source

def main():
    for notebook_path in NOTEBOOKS:
        if not os.path.exists(notebook_path):
            print(f"Warning: Notebook not found: {notebook_path}")
            continue
        
        print(f"Processing {notebook_path}...")
        
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        modified = False
        
        # Add worst case analysis calls
        if add_worst_case_call_after_current(nb):
            print("  Added worst case current analysis call")
            modified = True
        
        if add_worst_case_call_after_voltage(nb):
            print("  Added worst case voltage analysis call")
            modified = True
        
        # Update plot function signatures
        update_plot_function_signatures(nb)
        
        # Add worst case tables to plots
        if add_worst_case_table_to_current_plot(nb):
            print("  Added worst case table to current harmonics plot")
            modified = True
        
        if add_worst_case_table_to_voltage_plot(nb):
            print("  Added worst case table to voltage harmonics plot")
            modified = True
        
        # Update plot calls
        update_plot_calls(nb)
        
        if modified:
            # Write back
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(nb, f, indent=1, ensure_ascii=False)
            print("  Saved notebook")
        else:
            print("  No changes needed")

if __name__ == '__main__':
    main()
