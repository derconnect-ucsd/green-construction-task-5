"""Update harmonics-study_test_9B_moxion.ipynb for Test 9B: paths, filenames, titles."""
import re

NOTEBOOK = "src/analysis/harmonics-study_test_9B_moxion.ipynb"

def main():
    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Title and description
    content = content.replace(
        '"# Harmonics Study - Test 9C\\n",',
        '"# Harmonics Study - Test 9B (Moxion)\\n",',
        1
    )
    content = content.replace(
        'This notebook performs harmonics analysis on mobile battery power data from test 9C (Loadbank + Grid only). Load profile: **load_profile_moxion_mp75.csv** (data/raw-inputs/load-profiles); the **Notes** column describes each subtest. We use **Phase 1** (10-second holds at various R/L/C loads) for harmonics and THD study. Data: waveform and PMU CSVs in test-data/data_test_9c.',
        'This notebook performs harmonics analysis on mobile battery power data from **test 9B** (Moxion MP75 with load bank, no grid). Load profile: **load_profile_moxion_mp75.csv** (data/raw-inputs/load-profiles); the **Notes** column describes each subtest. We use **Phase 1** (10-second holds at various R/L/C loads) for harmonics and THD study. Data: waveform and PMU CSVs in test-data/data_test_9b. Analysis is limited to the **second run** (14:31:12-14:37:17) because the battery faulted on the first run.'
    )

    # 2. Config: DATA_DIR
    content = content.replace(
        "data_test_9c')",
        "data_test_9b')",
        1
    )
    # Data files comment and filenames
    content = content.replace(
        '"# Data files (re-run test 9C; filename base from export timestamp 20260214,015631 0800)\\n",',
        '"# Data files (Test 9B; second run only; export 20260214,062236 0800)\\n",',
        1
    )
    content = content.replace(
        'DataExport_Waveform_FDR01_20260214,015631 0800.CSV',
        'DataExport_Waveform_FDR08_20260214,062236 0800.CSV',
        1
    )
    content = content.replace(
        'DataExport_Phasor_FDR01_20260214,015631 0800.CSV',
        'DataExport_Phasor_FDR08_20260214,062236 0800.CSV',
        1
    )
    # Insert LOADBANK_FILENAME, EVENT_LOG_FILENAME, RUN_START, RUN_END before LOAD_PROFILE_PATH
    content = content.replace(
        '"LOAD_PROFILE_PATH = os.path.join(\'..\', \'..\', \'data\', \'raw-inputs\', \'load-profiles\', \'load_profile_moxion_mp75.csv\')\\n",',
        '"LOADBANK_FILENAME = \\"loadbank_log_20260213_223111_second run.csv\\"\\n",\n    "EVENT_LOG_FILENAME = \\"event_log_test_9b.csv\\"\\n",\n    "LOAD_PROFILE_PATH = os.path.join(\'..\', \'..\', \'data\', \'raw-inputs\', \'load-profiles\', \'load_profile_moxion_mp75.csv\')\\n",',
        1
    )
    content = content.replace(
        '"\\n",\n    "os.makedirs(OUTPUT_DIR, exist_ok=True)"',
        '"\\n",\n    "# Second run window (battery faulted on first run)\\n",\n    "RUN_START = datetime(2026, 2, 13, 14, 31, 12, tzinfo=TIMEZONE_SD)\\n",\n    "RUN_END = datetime(2026, 2, 13, 14, 37, 17, tzinfo=TIMEZONE_SD)\\n",\n    "\\n",\n    "os.makedirs(OUTPUT_DIR, exist_ok=True)"',
        1
    )

    # 3. Loadbank and event log loaders (in JSON, inner quotes are \")
    content = content.replace(
        'loadbank_file = os.path.join(DATA_DIR, \\"loadbank_log_20251205_test9c.csv\\")',
        'loadbank_file = os.path.join(DATA_DIR, LOADBANK_FILENAME)',
        1
    )
    content = content.replace(
        'event_file = os.path.join(DATA_DIR, \\"event_log_test_9c.csv\\")',
        'event_file = os.path.join(DATA_DIR, EVENT_LOG_FILENAME)',
        1
    )

    # 4. All figure and markdown titles: Test 9C -> Test 9B
    content = content.replace("Test 9C", "Test 9B")

    # 5. Scenario text for 9B (load bank only, no grid)
    content = content.replace(
        "**Test 9B Scenario**: In this test, the loadbank is connected to the grid, allowing us to observe harmonics coming from the grid itself.",
        "**Test 9B Scenario**: In this test, the Moxion MP75 supplies the load bank only (no grid), allowing us to observe harmonics from the battery system."
    )

    with open(NOTEBOOK, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated notebook for Test 9B: paths, filenames, titles, time slice.")

if __name__ == "__main__":
    main()
