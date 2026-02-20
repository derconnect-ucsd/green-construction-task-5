"""
Compare Battery vs Grid Harmonics

Reads exported results from 9B (Moxion battery) and 9C (Grid only) harmonics analysis
and produces a comparison report and figure. Run this after executing both notebooks
to generate the battery_vs_grid_harmonics_9B.json and battery_vs_grid_harmonics_9C.json
files.

Usage:
    python src/analysis/compare_battery_grid_harmonics.py

Or from project root:
    python -m src.analysis.compare_battery_grid_harmonics
"""

import json
import os
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_result(test_id: str, results_dir: Path) -> dict | None:
    """Load battery_vs_grid_harmonics_{test_id}.json if it exists."""
    path = results_dir / f"battery_vs_grid_harmonics_{test_id}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compare_no_load(data_9b: dict | None, data_9c: dict | None) -> None:
    """Print no-load voltage harmonics comparison."""
    print("\n" + "=" * 70)
    print("1) NO-LOAD VOLTAGE HARMONICS COMPARISON")
    print("   (Inherent source distortion - battery vs grid)")
    print("=" * 70)

    if not data_9b or not data_9b.get("no_load"):
        print("   9B (Moxion battery): No no-load data available.")
    else:
        nl = data_9b["no_load"]
        v_mean = nl.get("voltage_thd_mean")
        v_max = nl.get("voltage_thd_max")
        print(f"   9B (Moxion battery): Voltage THD mean = {v_mean:.2f}%, max = {v_max:.2f}%")

    if not data_9c or not data_9c.get("no_load"):
        print("   9C (Grid only): No no-load data available.")
    else:
        nl = data_9c["no_load"]
        v_mean = nl.get("voltage_thd_mean")
        v_max = nl.get("voltage_thd_max")
        print(f"   9C (Grid only):      Voltage THD mean = {v_mean:.2f}%, max = {v_max:.2f}%")

    if data_9b and data_9c and data_9b.get("no_load") and data_9c.get("no_load"):
        v9b = data_9b["no_load"].get("voltage_thd_mean") or data_9b["no_load"].get("voltage_thd_max")
        v9c = data_9c["no_load"].get("voltage_thd_mean") or data_9c["no_load"].get("voltage_thd_max")
        if v9b is not None and v9c is not None and v9c > 0:
            diff = v9b - v9c
            print(f"\n   Difference (9B - 9C): {diff:+.2f}%")
            if diff > 0.5:
                print("   -> Battery produces more inherent voltage distortion than grid.")
            elif diff < -0.5:
                print("   -> Grid produces more inherent voltage distortion than battery.")
            else:
                print("   -> Similar inherent voltage quality at no-load.")


def compare_loaded_conditions(data_9b: dict | None, data_9c: dict | None) -> None:
    """Print loaded condition comparison for key R/L/C combinations."""
    print("\n" + "=" * 70)
    print("2) LOADED CONDITIONS COMPARISON (same load bank)")
    print("   Extra voltage distortion = response to harmonic currents (source impedance)")
    print("=" * 70)

    key_conditions = ["R45kW_L0kVAR_C0kVAR", "R75kW_L0kVAR_C0kVAR", "R60kW_L0kVAR_C0kVAR"]
    loaded_9b = (data_9b or {}).get("loaded_conditions", {})
    loaded_9c = (data_9c or {}).get("loaded_conditions", {})

    # Find conditions present in either
    all_conds = sorted(set(loaded_9b.keys()) | set(loaded_9c.keys()))
    # Prefer key conditions first
    for kc in key_conditions:
        if kc in all_conds:
            all_conds.remove(kc)
    conds_to_show = [c for c in key_conditions if c in loaded_9b or c in loaded_9c]
    conds_to_show += [c for c in all_conds if c not in conds_to_show][:5]

    if not conds_to_show:
        print("   No common loaded conditions found.")
        return

    print(f"\n   {'Condition':<25} {'9B (Battery)':<18} {'9C (Grid)':<18} {'Diff (9B-9C)':<12}")
    print("   " + "-" * 75)

    for cond in conds_to_show:
        v9b = (loaded_9b.get(cond) or {}).get("voltage_thd_max")
        v9c = (loaded_9c.get(cond) or {}).get("voltage_thd_max")
        v9b_str = f"{v9b:.2f}%" if v9b is not None else "N/A"
        v9c_str = f"{v9c:.2f}%" if v9c is not None else "N/A"
        if v9b is not None and v9c is not None:
            diff_str = f"{v9b - v9c:+.2f}%"
        else:
            diff_str = "N/A"
        print(f"   {cond:<25} {v9b_str:<18} {v9c_str:<18} {diff_str:<12}")

    print("\n   Interpretation: Higher 9B voltage THD at same load suggests the battery")
    print("   inverter has higher output impedance, causing more voltage distortion")
    print("   when the load bank draws harmonic currents.")


def print_summary(data_9b: dict | None, data_9c: dict | None) -> None:
    """Print overall summary and conclusions."""
    print("\n" + "=" * 70)
    print("3) SUMMARY: DETERMINING HARMONICS FROM THE MOBILE BATTERY")
    print("=" * 70)
    print("""
   - Current harmonics: Produced by the LOAD (load bank). The battery supplies
     whatever current the load demands. Both 9B and 9C show similar current
     harmonic patterns because the same load bank is used.

   - Voltage harmonics at no-load: Represent the INHERENT voltage quality of the
     source (battery inverter vs grid). Higher no-load voltage THD in 9B
     indicates the battery inverter adds more voltage distortion.

   - Voltage harmonics when loaded: Have two components:
     (1) Inherent source distortion
     (2) Voltage drop from harmonic currents flowing through source impedance
     (V_h = I_h * Z_source). The battery typically has higher Z than the grid,
     so loaded voltage THD is often higher in 9B.

   Next steps: Run both harmonics-study notebooks (9B and 9C) to generate the
   JSON result files, then re-run this comparison script.
""")


def _get_loaded_conditions_list(
    data_9b: dict | None, data_9c: dict | None, max_conditions: int = 5
) -> list[str]:
    """Get ordered list of load conditions to display."""
    key_conditions = ["R45kW_L0kVAR_C0kVAR", "R75kW_L0kVAR_C0kVAR", "R60kW_L0kVAR_C0kVAR"]
    loaded_9b = (data_9b or {}).get("loaded_conditions", {})
    loaded_9c = (data_9c or {}).get("loaded_conditions", {})
    all_conds = sorted(set(loaded_9b.keys()) | set(loaded_9c.keys()))
    for kc in key_conditions:
        if kc in all_conds:
            all_conds.remove(kc)
    conds = [c for c in key_conditions if c in loaded_9b or c in loaded_9c]
    conds += [c for c in all_conds if c not in conds][: max_conditions - len(conds)]
    return conds[:max_conditions]


def create_comparison_figure(
    data_9b: dict | None, data_9c: dict | None, results_dir: Path
):
    """Create a multi-panel figure with no-load comparison, loaded comparison, and summary."""
    # Use fixed axes positions for no overlap: [left, bottom, width, height] in figure coords
    # Section 1 (top), Section 2 (middle), Section 3 (bottom) with clear gaps
    fig = plt.figure(figsize=(12, 16), facecolor="white")
    fig.suptitle("Battery vs Grid Harmonics Comparison", fontsize=16, fontweight="bold", y=0.98)

    # --- Panel 1: No-load voltage harmonics ---
    ax1 = fig.add_axes((0.12, 0.74, 0.76, 0.18))  # top section
    sources = ["9B (Moxion Battery)", "9C (Grid Only)"]
    mean_vals = []
    max_vals = []
    for data in [data_9b, data_9c]:
        if data and data.get("no_load"):
            nl = data["no_load"]
            mean_vals.append(nl.get("voltage_thd_mean") or 0)
            max_vals.append(nl.get("voltage_thd_max") or 0)
        else:
            mean_vals.append(0)
            max_vals.append(0)

    x = np.arange(len(sources))
    w = 0.35
    bars1 = ax1.bar(x - w / 2, mean_vals, w, label="Mean", color=["#e74c3c", "#3498db"])
    bars2 = ax1.bar(x + w / 2, max_vals, w, label="Max", color=["#c0392b", "#2980b9"])
    ax1.set_ylabel("Voltage THD (%)", fontsize=11)
    ax1.set_title("1) No-Load Voltage Harmonics Comparison", fontsize=12, fontweight="bold", pad=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(sources)
    ax1.legend(loc="upper right", fontsize=9)
    ax1.set_ylim(0, max(max(max_vals) if max_vals else 1, 1) * 1.3)
    ax1.grid(axis="y", alpha=0.3)
    for bar in bars1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}%", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}%", ha="center", va="bottom", fontsize=9)

    # --- Panel 2: Loaded conditions ---
    ax2 = fig.add_axes((0.12, 0.40, 0.76, 0.26))  # middle section, 0.08 gap below section 1
    conds = _get_loaded_conditions_list(data_9b, data_9c)
    loaded_9b = (data_9b or {}).get("loaded_conditions", {})
    loaded_9c = (data_9c or {}).get("loaded_conditions", {})

    v9b_vals = [(loaded_9b.get(c) or {}).get("voltage_thd_max") or 0 for c in conds]
    v9c_vals = [(loaded_9c.get(c) or {}).get("voltage_thd_max") or 0 for c in conds]
    cond_labels = [c.replace("kW_L", " L").replace("kVAR_C", " C").replace("_", " ").replace("kVAR", "") for c in conds]

    x = np.arange(len(cond_labels))
    bars_b = ax2.bar(x - w / 2, v9b_vals, w, label="9B (Battery)", color="#e74c3c")
    bars_c = ax2.bar(x + w / 2, v9c_vals, w, label="9C (Grid)", color="#3498db")
    ax2.set_ylabel("Voltage THD Max (%)", fontsize=11)
    ax2.set_xlabel("Load Condition (R, L, C)", fontsize=11)
    ax2.set_title("2) Loaded Conditions Comparison", fontsize=12, fontweight="bold", pad=8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(cond_labels, rotation=-25, ha="left")
    ax2.legend(loc="upper right", fontsize=9)
    ax2.set_ylim(0, max(max(v9b_vals + v9c_vals) if (v9b_vals or v9c_vals) else 1, 1) * 1.25)
    ax2.grid(axis="y", alpha=0.3)
    for bar in bars_b:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}" if h else "N/A", ha="center", va="bottom", fontsize=8)
    for bar in bars_c:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}" if h else "N/A", ha="center", va="bottom", fontsize=8)

    # --- Panel 3: Summary table ---
    ax3 = fig.add_axes((0.12, 0.02, 0.76, 0.30))  # bottom section, 0.08 gap below section 2
    ax3.axis("off")

    wrap_width = 55
    summary_rows = [
        ("Current harmonics", "Produced by the LOAD (load bank). The battery supplies whatever current the load demands."),
        ("Voltage at no-load", "Represents INHERENT voltage quality. Higher 9B THD indicates battery adds more distortion."),
        ("Voltage when loaded", "Two components: (1) Inherent distortion, (2) V_h = I_h × Z_source. Higher Z → more distortion."),
        ("Interpretation", "Higher 9B voltage THD at same load suggests battery has higher output impedance."),
    ]
    table_data = [["Topic", "Summary"]] + [
        (topic, textwrap.fill(summary, width=wrap_width)) for topic, summary in summary_rows
    ]
    table = ax3.table(
        cellText=table_data,
        loc="upper center",
        cellLoc="left",
        colWidths=[0.22, 0.78],
        bbox=[0, 0, 1, 0.92],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.0)
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_facecolor("#34495e")
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor("#ecf0f1" if i % 2 == 1 else "white")
    ax3.set_title("3) Summary: Determining Harmonics from the Mobile Battery", fontsize=12, fontweight="bold", pad=-4)

    return fig


def main():
    # Find results directory (from script location or cwd)
    script_dir = Path(__file__).resolve().parent  # src/analysis
    project_root = script_dir.parent.parent  # project root (src/analysis -> src -> project)
    results_dir = project_root / "results" / "harmonics_study"
    if not results_dir.exists():
        results_dir = Path.cwd() / "results" / "harmonics_study"
    if not results_dir.exists():
        results_dir = Path.cwd()

    data_9b = load_result("9B", results_dir)
    data_9c = load_result("9C", results_dir)

    print("=" * 70)
    print("BATTERY VS GRID HARMONICS COMPARISON")
    print("=" * 70)
    print(f"\nResults directory: {results_dir}")
    print(f"9B (Moxion battery): {'Found' if data_9b else 'NOT FOUND - run harmonics-study_test_9B notebook first'}")
    print(f"9C (Grid only):      {'Found' if data_9c else 'NOT FOUND - run harmonics-study_test_9C notebook first'}")

    if not data_9b and not data_9c:
        print("\nNo result files found. Run both harmonics-study notebooks (9B and 9C)")
        print("to completion, then run this script again.")
        return

    compare_no_load(data_9b, data_9c)
    compare_loaded_conditions(data_9b, data_9c)
    print_summary(data_9b, data_9c)

    # Create and save figure
    fig = create_comparison_figure(data_9b, data_9c, results_dir)
    os.makedirs(results_dir, exist_ok=True)
    fig_path = results_dir / "battery_vs_grid_harmonics_comparison.png"
    fig.savefig(str(fig_path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"\nFigure saved to {fig_path}")


if __name__ == "__main__":
    main()
