"""Fix plot_harmonics_vs_time in 9B notebook: conditional layout and add table before show/write."""
import json
import sys

NOTEBOOK = "src/analysis/harmonics-study_test_9B_moxion.ipynb"

# Replacement for the make_subplots block: conditional rows/specs when worst_case_current is used
OLD_MAIN = '''    print("\\nCreating time-varying current harmonics visualization...")
    t_min = time_varying_harmonics_df.index.min() if not time_varying_harmonics_df.empty else None
    t_max = time_varying_harmonics_df.index.max() if not time_varying_harmonics_df.empty else None

    # Create subplots
    fig = make_subplots(
        rows=5, cols=1,
        subplot_titles=(
            'Current Total Harmonic Distortion (THD) vs Time',
            'Power Measurements vs Time',
            'Loadbank Load Profile vs Time',
            'Top 5 Harmonics vs Time',
            'Worst Case Summary'
        ),
        vertical_spacing=0.08,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"type": "table"}]]
    )'''

NEW_MAIN = '''    print("\\nCreating time-varying current harmonics visualization...")
    t_min = time_varying_harmonics_df.index.min() if not time_varying_harmonics_df.empty else None
    t_max = time_varying_harmonics_df.index.max() if not time_varying_harmonics_df.empty else None

    # Number of rows: 5 with worst-case table panel, 4 without (table trace requires type "table" subplot)
    has_worst_case = worst_case_current is not None and isinstance(worst_case_current, dict)
    n_rows = 5 if has_worst_case else 4
    subplot_titles = (
        'Current Total Harmonic Distortion (THD) vs Time',
        'Power Measurements vs Time',
        'Loadbank Load Profile vs Time',
        'Top 5 Harmonics vs Time',
        'Worst Case Summary'
    ) if has_worst_case else (
        'Current Total Harmonic Distortion (THD) vs Time',
        'Power Measurements vs Time',
        'Loadbank Load Profile vs Time',
        'Top 5 Harmonics vs Time'
    )
    specs = (
        [[{"secondary_y": False}],
         [{"secondary_y": False}],
         [{"secondary_y": False}],
         [{"secondary_y": False}],
         [{"type": "table"}]]
    ) if has_worst_case else (
        [[{"secondary_y": False}],
         [{"secondary_y": False}],
         [{"secondary_y": False}],
         [{"secondary_y": False}]]
    )

    # Create subplots
    fig = make_subplots(
        rows=n_rows, cols=1,
        subplot_titles=subplot_titles,
        vertical_spacing=0.08,
        specs=specs
    )'''

# Move worst-case table before show/write: remove from end and insert after "row=4, col=1" and before "# Update layout"
OLD_AFTER_PLOT4 = '''                    row=4, col=1
    )
    
    # Update layout'''

NEW_AFTER_PLOT4 = '''                    row=4, col=1
    )
    
    # Plot 5: Worst case summary table (before show/write so it appears in export)
    if has_worst_case:
        table_data = []
        table_data.append(['Phase', worst_case_current.get('phase', 'N/A')])
        table_data.append(['Timestamp', str(worst_case_current.get('timestamp', 'N/A'))])
        table_data.append(['Max THD', f"{worst_case_current.get('max_thd', 0):.2f}%"])
        top_harmonics = worst_case_current.get('top_harmonics', {})
        if top_harmonics:
            harmonics_str = ', '.join([f"{k}: {v:.1f}%" for k, v in sorted(top_harmonics.items(), key=lambda x: x[1], reverse=True)[:3]])
            table_data.append(['Top Harmonics', harmonics_str])
        load_cond = worst_case_current.get('load_condition')
        if load_cond:
            table_data.append(['Load Condition', f"R={load_cond.get('R_kw', 0):.1f}kW, L={load_cond.get('L_kvar', 0):.1f}kVAR, C={load_cond.get('C_kvar', 0):.1f}kVAR"])
        table_data.append(['Extra Current', f"{worst_case_current.get('extra_current_pct', 0):.2f}%"])
        table_data.append(['Heating Factor', f"{worst_case_current.get('heating_factor', 1):.2f}x"])
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'], fill_color='lightblue', align='left', font=dict(size=12)),
                cells=dict(values=[list(x) for x in zip(*table_data)], fill_color='white', align='left', font=dict(size=11)),
                columnwidth=[0.3, 0.7]
            ),
            row=5, col=1
        )
    
    # Update layout'''

# Remove the duplicate block at the end (from "# Plot 5: Worst case summary table" through "return fig")
OLD_END_BLOCK = '''
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
    
    
    return fig'''

NEW_END_BLOCK = '''
    return fig'''


def main():
    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        nb = json.load(f)
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell.get("source", []))
        if "def plot_harmonics_vs_time" not in src or "make_subplots" not in src:
            continue
        if OLD_MAIN not in src:
            print("Cell found but OLD_MAIN block not found; notebook may already be patched or format changed.")
            sys.exit(1)
        new_src = src.replace(OLD_MAIN, NEW_MAIN, 1)
        if OLD_AFTER_PLOT4 not in new_src:
            print("OLD_AFTER_PLOT4 not found after first replace.")
            sys.exit(1)
        new_src = new_src.replace(OLD_AFTER_PLOT4, NEW_AFTER_PLOT4, 1)
        if OLD_END_BLOCK not in new_src:
            print("OLD_END_BLOCK not found.")
            sys.exit(1)
        new_src = new_src.replace(OLD_END_BLOCK, NEW_END_BLOCK, 1)
        cell["source"] = new_src.splitlines(keepends=True)
        if cell["source"] and not cell["source"][-1].endswith("\n"):
            cell["source"][-1] += "\n"
        print(f"Patched cell {i} (plot_harmonics_vs_time).")
        break
    else:
        print("No cell with plot_harmonics_vs_time found.")
        sys.exit(1)
    with open(NOTEBOOK, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Done.")


if __name__ == "__main__":
    main()
