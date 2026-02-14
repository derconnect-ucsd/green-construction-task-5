"""
Update plot_voltage_harmonics_vs_time in both notebooks to:
1. Use load_profile_moxion_mp75.csv for the load subplot with R, L, C traces
2. Align x-axis range across all subplots to THD time range
"""
import json
import os
import re

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

def update_cell_26(src):
    # 1) Change signature: loadbank_df -> load_profile_path
    src = src.replace(
        'def plot_voltage_harmonics_vs_time(time_varying_harmonics_df, power_df, loadbank_df):',
        'def plot_voltage_harmonics_vs_time(time_varying_harmonics_df, power_df, load_profile_path):'
    )
    src = src.replace(
        '    loadbank_df: DataFrame with loadbank data',
        '    load_profile_path: Path to load_profile_moxion_mp75.csv for R, L, C vs time subplot'
    )

    # 2) Add t_min, t_max right after the print statement
    old_print = '    print("\\nCreating time-varying voltage harmonics visualization...")'
    new_print = '''    print("\\nCreating time-varying voltage harmonics visualization...")
    t_min = time_varying_harmonics_df.index.min()
    t_max = time_varying_harmonics_df.index.max()'''
    src = src.replace(old_print, new_print)

    # 3) Trim power_df to THD range before Plot 2 (add right before "# Plot 2")
    old_plot2_start = "    # Plot 2: Power measurements vs time\n    if power_df is not None and not power_df.empty:"
    new_plot2_start = """    # Plot 2: Power measurements vs time (trimmed to THD time range)
    plot_power = power_df[(power_df.index >= t_min) & (power_df.index <= t_max)] if power_df is not None and not power_df.empty else pd.DataFrame()
    if plot_power is not None and not plot_power.empty:
        power_df = plot_power
    if power_df is not None and not power_df.empty:"""
    src = src.replace(old_plot2_start, new_plot2_start)

    # 4) Replace Plot 3 block with load profile CSV and R, L, C traces
    old_plot3 = """# Plot 3: Loadbank load profile
    if loadbank_df is not None and not loadbank_df.empty:
        if 'resistive_kw (kW)' in loadbank_df.columns:
            fig.add_trace(
                go.Scatter(x=loadbank_df.index, y=loadbank_df['resistive_kw (kW)'],
                          name='Resistive Load (kW)', line=dict(color='orange', width=2)),
                row=3, col=1
    )
    
    """

    new_plot3 = """# Plot 3: Load profile from load_profile_moxion_mp75.csv (R, L, C) aligned to THD time range
    if load_profile_path and os.path.exists(load_profile_path):
        try:
            profile_df = pd.read_csv(load_profile_path, encoding='cp1252')
            profile_df.columns = [c.strip() for c in profile_df.columns]
            rcol = [c for c in profile_df.columns if 'Resistive' in c or c == 'Resistive Load (kW)'][:1]
            lcol = [c for c in profile_df.columns if 'Inductive' in c or c == 'Inductive Load (kVAR)'][:1]
            ccol = [c for c in profile_df.columns if 'Capacitive' in c or c == 'Capacitive Load (kVAR)'][:1]
            n_seconds = max(1, int((t_max - t_min).total_seconds()) + 1)
            r_vals = profile_df[rcol[0]].ffill().fillna(0).astype(float).values if rcol else np.zeros(n_seconds)
            l_vals = profile_df[lcol[0]].ffill().fillna(0).astype(float).values if lcol else np.zeros(n_seconds)
            c_vals = profile_df[ccol[0]].ffill().fillna(0).astype(float).values if ccol else np.zeros(n_seconds)
            r_vals = np.resize(r_vals, n_seconds)
            l_vals = np.resize(l_vals, n_seconds)
            c_vals = np.resize(c_vals, n_seconds)
            ts_index = pd.date_range(start=t_min, periods=n_seconds, freq='s')
            fig.add_trace(go.Scatter(x=ts_index, y=r_vals, name='R (kW)', line=dict(color='orange', width=2)), row=3, col=1)
            fig.add_trace(go.Scatter(x=ts_index, y=l_vals, name='L (kVAR)', line=dict(color='green', width=2)), row=3, col=1)
            fig.add_trace(go.Scatter(x=ts_index, y=c_vals, name='C (kVAR)', line=dict(color='blue', width=2)), row=3, col=1)
        except Exception as e:
            print(f"Warning: Could not load profile for plot: {e}")

    """

    src = src.replace(old_plot3, new_plot3)

    # 5) Row 3 y-axis title: Load (kW) -> R (kW), L/C (kVAR)
    src = src.replace(
        'fig.update_yaxes(title_text="Load (kW)", row=3, col=1)',
        'fig.update_yaxes(title_text="R (kW), L/C (kVAR)", row=3, col=1)'
    )

    # 6) Add x-axis range alignment after the y-axis updates (before "# Display figure")
    old_axes_end = """    fig.update_yaxes(title_text="Harmonic Magnitude (% of Fundamental)", row=4, col=1)
    
    # Display figure in notebook"""
    new_axes_end = """    fig.update_yaxes(title_text="Harmonic Magnitude (% of Fundamental)", row=4, col=1)
    # Align x-axis range across all subplots to THD time range
    for r in range(1, 5):
        fig.update_xaxes(range=[t_min, t_max], row=r, col=1)

    # Display figure in notebook"""
    src = src.replace(old_axes_end, new_axes_end)

    return src

def update_cell_28_call(src):
    # Change plot_voltage_harmonics_vs_time(..., loadbank_for_plot) to (..., LOAD_PROFILE_PATH)
    src = re.sub(
        r'plot_voltage_harmonics_vs_time\(time_varying_voltage_harmonics_df,\s*plot_power_df,\s*loadbank_for_plot\)',
        'plot_voltage_harmonics_vs_time(time_varying_voltage_harmonics_df, plot_power_df, LOAD_PROFILE_PATH)',
        src
    )
    return src

def process_notebook(path):
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    # Cell 26: plot function
    cell26_src = ''.join(nb['cells'][26].get('source', []))
    nb['cells'][26]['source'] = update_cell_26(cell26_src).splitlines(True)
    if not nb['cells'][26]['source'][-1].endswith('\n'):
        nb['cells'][26]['source'][-1] += '\n'
    # Cell 28: call site
    cell28_src = ''.join(nb['cells'][28].get('source', []))
    nb['cells'][28]['source'] = update_cell_28_call(cell28_src).splitlines(True)
    if not nb['cells'][28]['source'][-1].endswith('\n'):
        nb['cells'][28]['source'][-1] += '\n'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"Updated {path}")

if __name__ == '__main__':
    for name in ['harmonics-study_test_9C.ipynb', 'harmonics-study_test_9B_moxion.ipynb']:
        path = os.path.join(REPO_ROOT, 'src', 'analysis', name)
        if os.path.exists(path):
            process_notebook(path)
        else:
            print(f"Skip (not found): {path}")
