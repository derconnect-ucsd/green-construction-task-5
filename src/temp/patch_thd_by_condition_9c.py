"""Patch THD-by-condition cell in harmonics-study_test_9C.ipynb to include worst current cases."""
import json
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parents[1] / "analysis" / "harmonics-study_test_9C.ipynb"

OLD = r"""# Worst condition: by voltage THD max (primary for this analysis)
    if curr_by_cond['voltage_thd_max'].notna().any():
        curr_by_cond = curr_by_cond.sort_values('voltage_thd_max', ascending=False, na_position='last')
    else:
        curr_by_cond = curr_by_cond.sort_values('current_thd_max', ascending=False)
    worst_cond = curr_by_cond.iloc[0]['condition'] if len(curr_by_cond) else None
    no_load_cond = (0, 0, 0)
    no_load_row = curr_by_cond[curr_by_cond['condition'].apply(lambda c: c == no_load_cond)]
    worst_row = curr_by_cond.iloc[0] if len(curr_by_cond) else None
    # Print answers
    print("\n" + "="*70)
    print("THD BY LOAD CONDITION (entire test)")
    print("="*70)
    print("\n1) Conditions that cause the MOST voltage harmonics (worst voltage THD):")
    if worst_row is not None:
        wc = worst_row['condition']
        print(f"   Worst condition: R={wc[0]} kW, L={wc[1]} kVAR, C={wc[2]} kVAR  ({cond_label_str(wc)})")
        print(f"   Current THD:  max = {worst_row['current_thd_max']:.2f}%,  mean = {worst_row['current_thd_mean']:.2f}%")
        if pd.notna(worst_row.get('voltage_thd_max')):
            print(f"   Voltage THD: max = {worst_row['voltage_thd_max']:.2f}%,  mean = {worst_row['voltage_thd_mean']:.2f}%")
    print("\n2) Do the worst THD values exceed IEEE 519 limits (THD limit = 5%)?")
    if worst_row is not None:
        curr_exceed = worst_row['current_thd_max'] > ieee_limit
        volt_exceed = worst_row.get('voltage_thd_max', 0) > ieee_limit if pd.notna(worst_row.get('voltage_thd_max')) else False
        print(f"   Current THD max {worst_row['current_thd_max']:.2f}%:  {'EXCEEDS' if curr_exceed else 'Within'} limit (5%)")
        if pd.notna(worst_row.get('voltage_thd_max')):
            print(f"   Voltage THD max {worst_row['voltage_thd_max']:.2f}%: {'EXCEEDS' if volt_exceed else 'Within'} limit (5%)")
    print("\n3) No-load vs worst condition (sensitivity of THD to load):")
    if no_load_row is not None and len(no_load_row) > 0 and worst_row is not None:
        nl = no_load_row.iloc[0]
        print(f"   No load (0,0,0):  Current THD max = {nl['current_thd_max']:.2f}%,  mean = {nl['current_thd_mean']:.2f}%")
        if pd.notna(nl.get('voltage_thd_max')):
            print(f"                    Voltage THD max = {nl['voltage_thd_max']:.2f}%,  mean = {nl['voltage_thd_mean']:.2f}%")
        print(f"   Worst condition: Current THD max = {worst_row['current_thd_max']:.2f}%,  mean = {worst_row['current_thd_mean']:.2f}%")
        if pd.notna(worst_row.get('voltage_thd_max')):
            print(f"                    Voltage THD max = {worst_row['voltage_thd_max']:.2f}%,  mean = {worst_row['voltage_thd_mean']:.2f}%")
        curr_ratio = worst_row['current_thd_max'] / nl['current_thd_max'] if nl['current_thd_max'] > 0 else float('inf')
        print(f"   Ratio (worst / no-load) current THD max: {curr_ratio:.2f}x")
        if pd.notna(nl.get('voltage_thd_max')) and nl['voltage_thd_max'] > 0:
            print(f"   Ratio (worst / no-load) voltage THD max: {worst_row['voltage_thd_max'] / nl['voltage_thd_max']:.2f}x")
        volt_ratio = (worst_row["voltage_thd_max"] / nl["voltage_thd_max"]) if pd.notna(nl.get("voltage_thd_max")) and nl["voltage_thd_max"] > 0 else curr_ratio
        ratio_for_conclusion = volt_ratio if pd.notna(volt_ratio) and not np.isinf(volt_ratio) else curr_ratio
        print("   Conclusion: Voltage THD is " + ("strongly sensitive" if ratio_for_conclusion > 1.5 else "moderately sensitive" if ratio_for_conclusion > 1.1 else "not very sensitive") + " to load condition.")
    else:
        if no_load_row is None or len(no_load_row) == 0:
            print("   No-load condition (0,0,0) not found in this run's data.")
        else:
            print("   Could not compare (missing worst or no-load).")
    print("\nSummary table (all conditions, by voltage THD max):")
    print(curr_by_cond[['condition_str', 'current_thd_max', 'current_thd_mean', 'voltage_thd_max', 'voltage_thd_mean', 'n_points']].to_string(index=False))
    print("="*70)
    return curr_by_cond"""

NEW = r"""# Worst conditions: by voltage THD max and by current THD max
    by_voltage = curr_by_cond.sort_values('voltage_thd_max', ascending=False, na_position='last') if curr_by_cond['voltage_thd_max'].notna().any() else curr_by_cond.sort_values('current_thd_max', ascending=False)
    by_current = curr_by_cond.sort_values('current_thd_max', ascending=False)
    no_load_cond = (0, 0, 0)
    no_load_row = curr_by_cond[curr_by_cond['condition'].apply(lambda c: c == no_load_cond)]
    worst_row_voltage = by_voltage.iloc[0] if len(by_voltage) else None
    worst_row_current = by_current.iloc[0] if len(by_current) else None
    # Print answers
    print("\n" + "="*70)
    print("THD BY LOAD CONDITION (entire test)")
    print("="*70)
    print("\n1) Conditions that cause the MOST harmonics (worst voltage THD and worst current THD):")
    print("   --- Worst by VOLTAGE THD ---")
    if worst_row_voltage is not None:
        wc = worst_row_voltage['condition']
        print(f"   Worst condition: R={wc[0]} kW, L={wc[1]} kVAR, C={wc[2]} kVAR  ({cond_label_str(wc)})")
        print(f"   Current THD:  max = {worst_row_voltage['current_thd_max']:.2f}%,  mean = {worst_row_voltage['current_thd_mean']:.2f}%")
        if pd.notna(worst_row_voltage.get('voltage_thd_max')):
            print(f"   Voltage THD: max = {worst_row_voltage['voltage_thd_max']:.2f}%,  mean = {worst_row_voltage['voltage_thd_mean']:.2f}%")
    print("   --- Worst by CURRENT THD ---")
    if worst_row_current is not None:
        wc = worst_row_current['condition']
        print(f"   Worst condition: R={wc[0]} kW, L={wc[1]} kVAR, C={wc[2]} kVAR  ({cond_label_str(wc)})")
        print(f"   Current THD:  max = {worst_row_current['current_thd_max']:.2f}%,  mean = {worst_row_current['current_thd_mean']:.2f}%")
        if pd.notna(worst_row_current.get('voltage_thd_max')):
            print(f"   Voltage THD: max = {worst_row_current['voltage_thd_max']:.2f}%,  mean = {worst_row_current['voltage_thd_mean']:.2f}%")
    print("\n2) Do the worst THD values exceed IEEE 519 limits (THD limit = 5%)?")
    if worst_row_voltage is not None:
        volt_exceed = worst_row_voltage.get('voltage_thd_max', 0) > ieee_limit if pd.notna(worst_row_voltage.get('voltage_thd_max')) else False
        print(f"   At voltage-worst condition: Voltage THD max {worst_row_voltage.get('voltage_thd_max', 0):.2f}%: {'EXCEEDS' if volt_exceed else 'Within'} limit (5%)")
    if worst_row_current is not None:
        curr_exceed = worst_row_current['current_thd_max'] > ieee_limit
        print(f"   At current-worst condition: Current THD max {worst_row_current['current_thd_max']:.2f}%: {'EXCEEDS' if curr_exceed else 'Within'} limit (5%)")
    print("\n3) No-load vs worst condition (sensitivity of THD to load):")
    if no_load_row is not None and len(no_load_row) > 0:
        nl = no_load_row.iloc[0]
        print(f"   No load (0,0,0):  Current THD max = {nl['current_thd_max']:.2f}%,  mean = {nl['current_thd_mean']:.2f}%")
        if pd.notna(nl.get('voltage_thd_max')):
            print(f"                    Voltage THD max = {nl['voltage_thd_max']:.2f}%,  mean = {nl['voltage_thd_mean']:.2f}%")
        if worst_row_voltage is not None:
            print(f"   Worst (by voltage): Current THD max = {worst_row_voltage['current_thd_max']:.2f}%,  Voltage THD max = {worst_row_voltage.get('voltage_thd_max', np.nan):.2f}%")
            if pd.notna(nl.get('voltage_thd_max')) and nl['voltage_thd_max'] > 0 and pd.notna(worst_row_voltage.get('voltage_thd_max')):
                print(f"   Ratio (worst / no-load) voltage THD max: {worst_row_voltage['voltage_thd_max'] / nl['voltage_thd_max']:.2f}x")
        if worst_row_current is not None:
            print(f"   Worst (by current): Current THD max = {worst_row_current['current_thd_max']:.2f}%,  Voltage THD max = {worst_row_current.get('voltage_thd_max', np.nan):.2f}%")
            curr_ratio = worst_row_current['current_thd_max'] / nl['current_thd_max'] if nl['current_thd_max'] > 0 else float('inf')
            print(f"   Ratio (worst / no-load) current THD max: {curr_ratio:.2f}x")
            ratio_for_conclusion = curr_ratio if not np.isinf(curr_ratio) else (worst_row_voltage['voltage_thd_max'] / nl['voltage_thd_max'] if pd.notna(nl.get('voltage_thd_max')) and nl['voltage_thd_max'] > 0 else curr_ratio)
            print("   Conclusion: THD is " + ("strongly sensitive" if ratio_for_conclusion > 1.5 else "moderately sensitive" if ratio_for_conclusion > 1.1 else "not very sensitive") + " to load condition.")
    else:
        if no_load_row is None or len(no_load_row) == 0:
            print("   No-load condition (0,0,0) not found in this run's data.")
        else:
            print("   Could not compare (missing worst or no-load).")
    print("\nSummary table (all conditions, by voltage THD max):")
    print(by_voltage[['condition_str', 'current_thd_max', 'current_thd_mean', 'voltage_thd_max', 'voltage_thd_mean', 'n_points']].to_string(index=False))
    print("\nSummary table (all conditions, by current THD max):")
    print(by_current[['condition_str', 'current_thd_max', 'current_thd_mean', 'voltage_thd_max', 'voltage_thd_mean', 'n_points']].to_string(index=False))
    print("="*70)
    return curr_by_cond"""


def main():
    with open(NOTEBOOK, encoding="utf-8") as f:
        nb = json.load(f)
    cell_idx = 29
    src = "".join(nb["cells"][cell_idx]["source"])
    if OLD not in src:
        print("OLD block not found (already patched or different content)")
        return 1
    new_src = src.replace(OLD, NEW, 1)
    lines = new_src.split("\n")
    nb["cells"][cell_idx]["source"] = [line + "\n" for line in lines[:-1]] + ([lines[-1] + "\n"] if lines[-1] else [])
    with open(NOTEBOOK, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Patched", NOTEBOOK)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
