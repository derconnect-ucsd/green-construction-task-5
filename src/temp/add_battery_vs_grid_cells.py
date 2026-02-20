"""Add battery vs grid harmonics extraction cells to 9B and 9C notebooks."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_9B = PROJECT_ROOT / "src" / "analysis" / "harmonics-study_test_9B_moxion.ipynb"
NOTEBOOK_9C = PROJECT_ROOT / "src" / "analysis" / "harmonics-study_test_9C.ipynb"

CELL_9B = '''# --- Battery vs Grid Harmonics: Extract no-load voltage harmonics for comparison ---
import sys
_analysis_dir = Path(__file__).parent if "__file__" in dir() else Path.cwd() / "src" / "analysis"
sys.path.insert(0, str(_analysis_dir))
try:
    from battery_vs_grid_harmonics import extract_and_save_battery_vs_grid_harmonics
except ImportError:
    sys.path.insert(0, str(Path.cwd() / "src" / "analysis"))
    from battery_vs_grid_harmonics import extract_and_save_battery_vs_grid_harmonics
from pathlib import Path

loadbank_for_extract = loadbank_phase1 if "loadbank_phase1" in dir() else (aligned_data.get("loadbank", pd.DataFrame()) if "aligned_data" in dir() else pd.DataFrame())
battery_vs_grid_9B = extract_and_save_battery_vs_grid_harmonics(
    test_id=TEST_ID,
    source_name="Moxion battery",
    time_varying_voltage_harmonics_df=time_varying_voltage_harmonics_df,
    thd_by_condition_df=thd_by_condition_df,
    get_load_at_timestamps=get_load_at_timestamps,
    loadbank_df=loadbank_for_extract,
    phase1_start=phase1_start,
    phase1_end=phase1_end,
    load_profile_df=load_profile_df,
    output_dir=OUTPUT_DIR,
)'''

CELL_9B_SIMPLE = '''# --- Battery vs Grid Harmonics: Extract no-load voltage harmonics for comparison ---
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)) if "__file__" in dir() else sys.path.insert(0, str(Path.cwd() / "src" / "analysis"))
try:
    from battery_vs_grid_harmonics import extract_and_save_battery_vs_grid_harmonics
except ImportError:
    import os
    sys.path.insert(0, os.path.join(os.getcwd(), "src", "analysis"))
    from battery_vs_grid_harmonics import extract_and_save_battery_vs_grid_harmonics

loadbank_for_extract = loadbank_phase1 if "loadbank_phase1" in dir() else (aligned_data.get("loadbank", pd.DataFrame()) if "aligned_data" in dir() else pd.DataFrame())
battery_vs_grid_9B = extract_and_save_battery_vs_grid_harmonics(
    test_id=TEST_ID,
    source_name="Moxion battery",
    time_varying_voltage_harmonics_df=time_varying_voltage_harmonics_df,
    thd_by_condition_df=thd_by_condition_df,
    get_load_at_timestamps=get_load_at_timestamps,
    loadbank_df=loadbank_for_extract,
    phase1_start=phase1_start,
    phase1_end=phase1_end,
    load_profile_df=load_profile_df,
    output_dir=OUTPUT_DIR,
)'''

CELL_9B_FINAL = '''# --- Battery vs Grid Harmonics: Extract no-load voltage harmonics for comparison ---
import sys, os
if os.path.exists("battery_vs_grid_harmonics.py"):
    sys.path.insert(0, os.getcwd())
elif os.path.exists(os.path.join("src", "analysis", "battery_vs_grid_harmonics.py")):
    sys.path.insert(0, os.path.join(os.getcwd(), "src", "analysis"))
from battery_vs_grid_harmonics import extract_and_save_battery_vs_grid_harmonics

loadbank_for_extract = loadbank_phase1 if "loadbank_phase1" in dir() else (aligned_data.get("loadbank", pd.DataFrame()) if "aligned_data" in dir() else pd.DataFrame())
battery_vs_grid_9B = extract_and_save_battery_vs_grid_harmonics(
    test_id=TEST_ID,
    source_name="Moxion battery",
    time_varying_voltage_harmonics_df=time_varying_voltage_harmonics_df,
    thd_by_condition_df=thd_by_condition_df,
    get_load_at_timestamps=get_load_at_timestamps,
    loadbank_df=loadbank_for_extract,
    phase1_start=phase1_start,
    phase1_end=phase1_end,
    load_profile_df=load_profile_df,
    output_dir=OUTPUT_DIR,
)'''

CELL_9C_FINAL = '''# --- Battery vs Grid Harmonics: Extract no-load voltage harmonics for comparison ---
import sys, os
if os.path.exists("battery_vs_grid_harmonics.py"):
    sys.path.insert(0, os.getcwd())
elif os.path.exists(os.path.join("src", "analysis", "battery_vs_grid_harmonics.py")):
    sys.path.insert(0, os.path.join(os.getcwd(), "src", "analysis"))
from battery_vs_grid_harmonics import extract_and_save_battery_vs_grid_harmonics

loadbank_for_extract = loadbank_range if "loadbank_range" in dir() else aligned_data.get("loadbank", pd.DataFrame())
phase_start = data_start if "data_start" in dir() else phase1_start
phase_end = data_end if "data_end" in dir() else phase1_end
battery_vs_grid_9C = extract_and_save_battery_vs_grid_harmonics(
    test_id=TEST_ID,
    source_name="Grid only",
    time_varying_voltage_harmonics_df=time_varying_voltage_harmonics_df,
    thd_by_condition_df=thd_by_condition_df,
    get_load_at_timestamps=get_load_at_timestamps,
    loadbank_df=loadbank_for_extract,
    phase1_start=phase_start,
    phase1_end=phase_end,
    load_profile_df=load_profile_df,
    output_dir=OUTPUT_DIR,
)'''


def add_cell(nb_path, cell_source, after_pattern, new_cell_id="battery-vs-grid-extract"):
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    insert_idx = None
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell.get("source", []))
        if after_pattern in src:
            insert_idx = i + 1
            break
    if insert_idx is None:
        print(f"Pattern not found in {nb_path}")
        return False
    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "id": new_cell_id,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in cell_source.strip().split("\n")],
    }
    # Remove trailing newline from last line
    if new_cell["source"]:
        new_cell["source"][-1] = new_cell["source"][-1].rstrip("\n")
    nb["cells"].insert(insert_idx, new_cell)
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"Added cell at index {insert_idx} in {nb_path.name}")
    return True


def main():
    add_cell(NOTEBOOK_9B, CELL_9B_FINAL, "thd_by_condition_df = summarize_thd_by_condition", "battery-vs-grid-9b")
    add_cell(NOTEBOOK_9C, CELL_9C_FINAL, "thd_by_condition_df = summarize_thd_by_condition", "battery-vs-grid-9c")
    print("Done.")


if __name__ == "__main__":
    main()
