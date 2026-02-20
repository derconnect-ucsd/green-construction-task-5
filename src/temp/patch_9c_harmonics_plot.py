"""Patch harmonics-study_test_9C: use load_profile_moxion_mp75.csv for current harmonics Plot 3 (R, L, C)."""
import json
import os

nb_path = os.path.join(os.path.dirname(__file__), '..', 'analysis', 'harmonics-study_test_9C.ipynb')
with open(nb_path, encoding='utf-8') as f:
    nb = json.load(f)

# Restored 9C has plot_harmonics_vs_time in cell 22 with simpler signature (no worst_case_current)
cell_idx = 22
cell = nb['cells'][cell_idx]
src = ''.join(cell['source'])

# 1) Signature and docstring / t_min,t_max - use exact content from notebook
old_sig = "".join(nb['cells'][cell_idx]['source'][:12])  # lines 0-11: def through "    # Create subplots\n"
new_sig = old_sig.replace(
    'def plot_harmonics_vs_time(time_varying_harmonics_df, power_df, loadbank_df):',
    'def plot_harmonics_vs_time(time_varying_harmonics_df, power_df, loadbank_df, worst_case_current=None, load_profile_path=None):',
    1
).replace(
    'loadbank_df: DataFrame with loadbank data\n',
    'loadbank_df: DataFrame with loadbank data (unused for load profile subplot; use load_profile_path)\n        load_profile_path: Path to load_profile_moxion_mp75.csv for R, L, C vs time subplot\n',
    1
).replace(
    '    print("\\nCreating time-varying current harmonics visualization...")\n    \n    # Create subplots',
    '    print("\\nCreating time-varying current harmonics visualization...")\n    t_min = time_varying_harmonics_df.index.min() if not time_varying_harmonics_df.empty else None\n    t_max = time_varying_harmonics_df.index.max() if not time_varying_harmonics_df.empty else None\n    \n    # Create subplots',
    1
)

if old_sig not in src:
    raise SystemExit("Old signature block not found in cell 22")
src = src.replace(old_sig, new_sig, 1)

# 2) Replace Plot 3 block (notebook has "    )\n    \n    # Plot 4" between Plot 3 and 4)
old_plot3 = '''    # Plot 3: Loadbank load profile
    if loadbank_df is not None and not loadbank_df.empty:
        if 'resistive_kw (kW)' in loadbank_df.columns:
            fig.add_trace(
                go.Scatter(x=loadbank_df.index, y=loadbank_df['resistive_kw (kW)'],
                          name='Resistive Load (kW)', line=dict(color='orange', width=2)),
                row=3, col=1
    )

    # Plot 4: Top 5 harmonics vs time (show average across phases)'''.replace('\n\n    # Plot 4', '\n    \n    # Plot 4')

new_plot3 = '''    # Plot 3: Load profile from load_profile_moxion_mp75.csv (R, L, C) aligned to THD time range
    if load_profile_path and t_min is not None and t_max is not None and os.path.exists(load_profile_path):
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

    # Plot 4: Top 5 harmonics vs time (show average across phases)'''.replace('\n\n    # Plot 4', '\n    \n    # Plot 4')

if old_plot3 not in src:
    raise SystemExit("Old Plot 3 block not found")
src = src.replace(old_plot3, new_plot3, 1)

# 3) Y-axis label row 3
src = src.replace(
    'fig.update_yaxes(title_text="Load (kW)", row=3, col=1)',
    'fig.update_yaxes(title_text="R (kW), L/C (kVAR)", row=3, col=1)',
    1
)

# 4) X-axis range alignment (notebook has "    \n    \n    # Display" between)
old_axes = '''    fig.update_yaxes(title_text="Harmonic Magnitude (% of Fundamental)", row=4, col=1)

    # Display figure in notebook'''.replace(')\n\n    # Display', ')\n    \n    # Display')

new_axes = '''    fig.update_yaxes(title_text="Harmonic Magnitude (% of Fundamental)", row=4, col=1)
    if t_min is not None and t_max is not None:
        for r in range(1, 5):
            fig.update_xaxes(range=[t_min, t_max], row=r, col=1)

    # Display figure in notebook'''.replace(')\n\n    # Display', ')\n    \n    # Display')

if old_axes not in src:
    raise SystemExit("Axes block not found")
src = src.replace(old_axes, new_axes, 1)

# Write back: split into lines and add newline for notebook format
cell['source'] = [line + '\n' for line in src.split('\n')]
if cell['source']:
    cell['source'][-1] = cell['source'][-1].rstrip('\n')  # last line often no trailing newline in nb

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Patched cell 22 (plot_harmonics_vs_time) in harmonics-study_test_9C.ipynb")

# Patch call site (find cell that calls plot_harmonics_vs_time)
with open(nb_path, encoding='utf-8') as f:
    nb = json.load(f)
call_cell_idx = None
for i, c in enumerate(nb['cells']):
    if c['cell_type'] == 'code' and c.get('source'):
        s = ''.join(c['source'])
        if 'plot_harmonics_vs_time(time_varying_harmonics_df, plot_power_df, loadbank_for_plot' in s:
            call_cell_idx = i
            break
if call_cell_idx is None:
    raise SystemExit("Call site not found")
cell_call = nb['cells'][call_cell_idx]
src30 = ''.join(cell_call['source'])
# Restored 9C has no worst_case_current in call
old_call = 'plot_harmonics_vs_time(time_varying_harmonics_df, plot_power_df, loadbank_for_plot)'
new_call = 'plot_harmonics_vs_time(time_varying_harmonics_df, plot_power_df, loadbank_for_plot, worst_case_current=worst_case_current if "worst_case_current" in locals() else None, load_profile_path=LOAD_PROFILE_PATH)'
if old_call not in src30:
    raise SystemExit("Call site not found in cell " + str(call_cell_idx))
src30 = src30.replace(old_call, new_call, 1)
cell_call['source'] = [line + '\n' for line in src30.split('\n')]
if cell_call['source']:
    cell_call['source'][-1] = cell_call['source'][-1].rstrip('\n')
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("Patched cell", call_cell_idx, "(call site) in harmonics-study_test_9C.ipynb")
