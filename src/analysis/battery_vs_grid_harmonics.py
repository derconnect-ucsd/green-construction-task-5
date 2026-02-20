"""
Battery vs Grid Harmonics Comparison

Extracts no-load voltage harmonics (inherent source distortion) and loaded-condition
stats from harmonics analysis. Results are saved to JSON for cross-test comparison.

Usage: Run from within the harmonics-study notebooks after thd_by_condition_df is computed.
"""

import json
import os

import numpy as np
import pandas as pd


def round_load_bin(x, bins=(0, 15, 30, 45, 60, 75)):
    """Round to nearest bin value for labeling."""
    if np.isnan(x) or x < 0:
        return 0
    b = np.asarray(bins)
    i = np.argmin(np.abs(b - x))
    return int(b[i])


def extract_and_save_battery_vs_grid_harmonics(
    test_id,
    source_name,
    time_varying_voltage_harmonics_df,
    thd_by_condition_df,
    get_load_at_timestamps,
    loadbank_df,
    phase1_start,
    phase1_end,
    load_profile_df,
    output_dir,
):
    """
    Extract no-load and loaded voltage harmonics, print report, save to JSON.

    Args:
        test_id: "9B" or "9C"
        source_name: "Moxion battery" or "Grid only"
        time_varying_voltage_harmonics_df: DataFrame with voltage harmonics by timestamp/phase
        thd_by_condition_df: DataFrame from summarize_thd_by_condition
        get_load_at_timestamps: Function to map timestamps to (R,L,C) load
        loadbank_df: Loadbank DataFrame (or empty)
        phase1_start, phase1_end: Phase 1 time range
        load_profile_df: Load profile DataFrame
        output_dir: Directory to save JSON results
    """
    result = {
        "test_id": test_id,
        "source": source_name,
        "no_load": None,
        "loaded_conditions": {},
        "has_no_load_data": False,
    }

    # --- No-load voltage harmonics ---
    no_load_cond = (0, 0, 0)
    no_load_row = None
    if thd_by_condition_df is not None and not thd_by_condition_df.empty:
        no_load_rows = thd_by_condition_df[
            thd_by_condition_df["condition"].apply(lambda c: c == no_load_cond)
        ]
        if len(no_load_rows) > 0:
            no_load_row = no_load_rows.iloc[0]
            result["has_no_load_data"] = True
            result["no_load"] = {
                "voltage_thd_max": float(no_load_row.get("voltage_thd_max", np.nan))
                if pd.notna(no_load_row.get("voltage_thd_max"))
                else None,
                "voltage_thd_mean": float(no_load_row.get("voltage_thd_mean", np.nan))
                if pd.notna(no_load_row.get("voltage_thd_mean"))
                else None,
                "voltage_thd_min": float(no_load_row.get("voltage_thd_min", np.nan))
                if pd.notna(no_load_row.get("voltage_thd_min"))
                else None,
                "current_thd_max": float(no_load_row.get("current_thd_max", np.nan))
                if pd.notna(no_load_row.get("current_thd_max"))
                else None,
                "n_points": int(no_load_row.get("n_points", 0)),
            }

    # Detailed no-load: filter voltage harmonics by timestamps with load (0,0,0)
    if (
        time_varying_voltage_harmonics_df is not None
        and not time_varying_voltage_harmonics_df.empty
        and phase1_start is not None
    ):
        volt_df = time_varying_voltage_harmonics_df.reset_index()
        ts_col = next((c for c in volt_df.columns if c in ("timestamp", "index") or "time" in c.lower()), volt_df.columns[0])
        ts_unique = volt_df[ts_col].unique() if ts_col in volt_df.columns else volt_df.index.unique()
        load_tuples = get_load_at_timestamps(
            list(ts_unique), loadbank_df, phase1_start, phase1_end, load_profile_df
        )
        no_load_ts = [
            t for t, (r, l, c) in zip(ts_unique, load_tuples)
            if round_load_bin(r) == 0 and round_load_bin(l) == 0 and round_load_bin(c) == 0
        ]
        if no_load_ts:
            if ts_col in volt_df.columns:
                no_load_volt = volt_df[volt_df[ts_col].isin(no_load_ts)]
            else:
                no_load_volt = volt_df[volt_df.index.isin(no_load_ts)]
            if not no_load_volt.empty:
                by_phase = no_load_volt.groupby("phase")["thd"].agg(["mean", "max", "min"])
                by_phase_dict = {
                    str(phase): {k: float(v) if pd.notna(v) else None for k, v in row.items()}
                    for phase, row in by_phase.to_dict("index").items()
                }
                result["no_load_detail"] = {
                    "n_windows": len(no_load_volt),
                    "voltage_thd_mean": float(no_load_volt["thd"].mean()),
                    "voltage_thd_max": float(no_load_volt["thd"].max()),
                    "voltage_thd_min": float(no_load_volt["thd"].min()),
                    "by_phase": by_phase_dict,
                }
                harmonic_cols = [c for c in no_load_volt.columns if c.startswith("H") and c[1:].isdigit()]
                if harmonic_cols:
                    top_h = no_load_volt[harmonic_cols].mean().sort_values(ascending=False).head(5)
                    result["no_load_detail"]["dominant_harmonics"] = {
                        k: float(v) for k, v in top_h.items()
                    }

    # --- Loaded conditions (key R/L/C combinations) ---
    if thd_by_condition_df is not None and not thd_by_condition_df.empty:
        for _, row in thd_by_condition_df.iterrows():
            c = row["condition"]
            if c == no_load_cond:
                continue
            cond_str = row.get("condition_str", f"R{c[0]}kW_L{c[1]}kVAR_C{c[2]}kVAR")
            result["loaded_conditions"][cond_str] = {
                "voltage_thd_max": float(row.get("voltage_thd_max", np.nan))
                if pd.notna(row.get("voltage_thd_max"))
                else None,
                "voltage_thd_mean": float(row.get("voltage_thd_mean", np.nan))
                if pd.notna(row.get("voltage_thd_mean"))
                else None,
                "current_thd_max": float(row.get("current_thd_max", np.nan))
                if pd.notna(row.get("current_thd_max"))
                else None,
                "n_points": int(row.get("n_points", 0)),
            }

    # --- Print report ---
    print("\n" + "=" * 70)
    print(f"BATTERY VS GRID HARMONICS EXTRACTION - Test {test_id} ({source_name})")
    print("=" * 70)
    print("\n1) NO-LOAD VOLTAGE HARMONICS (inherent source distortion)")
    if result["no_load"]:
        nl = result["no_load"]
        print(f"   Voltage THD:  max = {nl['voltage_thd_max']:.2f}%,  mean = {nl['voltage_thd_mean']:.2f}%,  min = {nl['voltage_thd_min']:.2f}%")
        print(f"   Windows: {nl['n_points']}")
        if "no_load_detail" in result and "dominant_harmonics" in result["no_load_detail"]:
            print("   Dominant harmonics (% of fundamental):")
            for h, v in result["no_load_detail"]["dominant_harmonics"].items():
                print(f"     {h}: {v:.2f}%")
    else:
        print("   No no-load data found in Phase 1.")
    print("\n2) LOADED CONDITIONS (sample)")
    for cond_str in list(result["loaded_conditions"].keys())[:5]:
        lc = result["loaded_conditions"][cond_str]
        vmax = lc["voltage_thd_max"] if lc["voltage_thd_max"] is not None else float("nan")
        print(f"   {cond_str}: Voltage THD max = {vmax:.2f}%")
    if len(result["loaded_conditions"]) > 5:
        print(f"   ... and {len(result['loaded_conditions']) - 5} more conditions")
    print("\n3) Results saved for comparison script")
    print("=" * 70)

    # --- Save to JSON ---
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"battery_vs_grid_harmonics_{test_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {out_path}")
    return result
