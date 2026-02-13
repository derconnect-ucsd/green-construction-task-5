"""Patch harmonics-study_test_9B_moxion.ipynb for Test 9B via text replacement (no JSON parse)."""
NOTEBOOK_PATH = "src/analysis/harmonics-study_test_9B_moxion.ipynb"

def main():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Title and description
    content = content.replace(
        '"# Harmonics Study - Test 9C\\n",',
        '"# Harmonics Study - Test 9B (Moxion)\\n",',
        1
    )
    content = content.replace(
        '"This notebook performs harmonics analysis on mobile battery power data from test 9C (Loadbank + Grid only). Load profile: **load_profile_moxion_mp75.csv** (data/raw-inputs/load-profiles); the **Notes** column describes each subtest. We use **Phase 1** (10-second holds at various R/L/C loads) for harmonics and THD study. Data: waveform and PMU CSVs in test-data/data_test_9c."',
        '"This notebook performs harmonics analysis on mobile battery power data from **test 9B** (Moxion MP75 with load bank, no grid). Load profile: **load_profile_moxion_mp75.csv** (data/raw-inputs/load-profiles); the **Notes** column describes each subtest. We use **Phase 1** (10-second holds at various R/L/C loads) for harmonics and THD study. Data: waveform and PMU CSVs in test-data/data_test_9b. Analysis is limited to the **second run** (14:31:12-14:37:17) because the battery faulted on the first run."',
        1
    )

    # 2. Config: data_test_9c -> data_test_9b (if still present)
    content = content.replace(
        "data_test_9c')",
        "data_test_9b')",
        1
    )
    # Data files comment and filenames
    content = content.replace(
        '"# Data files (re-run test 9C; filename base from export timestamp 20260214,015631 0800)\\n",',
        '"# Data files (Test 9B; second run only; filename base from export timestamp 20260214,062236 0800)\\n",',
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
    # Add LOADBANK_FILENAME and EVENT_LOG_FILENAME after PMU_FILENAME line
    content = content.replace(
        '"LOAD_PROFILE_PATH = os.path.join(\'..\', \'..\', \'data\', \'raw-inputs\', \'load-profiles\', \'load_profile_moxion_mp75.csv\')\\n",',
        '"LOADBANK_FILENAME = \\"loadbank_log_20260213_223111_second run.csv\\"\\n",\n    "EVENT_LOG_FILENAME = \\"event_log_test_9b.csv\\"\\n",\n    "LOAD_PROFILE_PATH = os.path.join(\'..\', \'..\', \'data\', \'raw-inputs\', \'load-profiles\', \'load_profile_moxion_mp75.csv\')\\n",',
        1
    )
    # Add RUN_START and RUN_END before os.makedirs
    content = content.replace(
        '"\\n",\n    "os.makedirs(OUTPUT_DIR, exist_ok=True)"',
        '"\\n",\n    "# Second run window (battery faulted on first run)\\n",\n    "RUN_START = datetime(2026, 2, 13, 14, 31, 12, tzinfo=TIMEZONE_SD)\\n",\n    "RUN_END = datetime(2026, 2, 13, 14, 37, 17, tzinfo=TIMEZONE_SD)\\n",\n    "\\n",\n    "os.makedirs(OUTPUT_DIR, exist_ok=True)"',
        1
    )

    # 3. Loadbank loader (in notebook JSON the quote is escaped as \")
    content = content.replace(
        'loadbank_file = os.path.join(DATA_DIR, \\"loadbank_log_20251205_test9c.csv\\")',
        'loadbank_file = os.path.join(DATA_DIR, LOADBANK_FILENAME)',
        1
    )

    # 4. Event log file
    content = content.replace(
        'event_file = os.path.join(DATA_DIR, \\"event_log_test_9c.csv\\")',
        'event_file = os.path.join(DATA_DIR, EVENT_LOG_FILENAME)',
        1
    )

    # 4b. Event log date format: support M.D.YYYY (e.g. 2.13.2026)
    content = content.replace(
        '                # Try YYYY.M.D first (e.g. 2026.2.13)\\n",\n    "                if \\".\\" in date_str and len(date_str) <= 10:\\n",\n    "                    date_obj = datetime.strptime(date_str, \\"%Y.%m.%d\\")\\n",\n    "                else:\\n",\n    "                    date_part = datetime.strptime(date_str, \\"%d-%b\\")\\n",\n    "                    date_obj = date_part.replace(year=date_part.year if date_part.year > 1900 else 2025)',
        '                # Try M.D.YYYY (e.g. 2.13.2026), then YYYY.M.D (e.g. 2026.2.13), else 31-Oct\\n",\n    "                parts = date_str.split(\\".\\")\\n",\n    "                if \\".\\" in date_str and len(parts) == 3 and len(parts[0]) <= 2 and len(parts[1]) <= 2 and len(parts[2]) == 4:\\n",\n    "                    date_obj = datetime.strptime(date_str, \\"%m.%d.%Y\\")\\n",\n    "                elif \\".\\" in date_str and len(date_str) <= 10:\\n",\n    "                    date_obj = datetime.strptime(date_str, \\"%Y.%m.%d\\")\\n",\n    "                else:\\n",\n    "                    date_part = datetime.strptime(date_str, \\"%d-%b\\")\\n",\n    "                    date_obj = date_part.replace(year=date_part.year if date_part.year > 1900 else 2025)',
        1
    )

    # 5. Restrict to second-run window: add slice before return in each load function
    # In notebook JSON: \" is one backslash+quote; \\n inside string is backslash+n (use \\n in Python)
    _nl = "\\n"   # in Python \\n is backslash then n (not newline)
    _q = '\\"'    # escaped quote in notebook
    # load_waveform_data (unique: "Sampling rate" line)
    old1 = ('Sampling rate: ~{1.0 / (result_df.index[1] - result_df.index[0]).total_seconds():.1f} Hz' + _q + ')' + _nl + '",\n    "    print(f' + _q + 'Columns: {list(result_df.columns)}' + _q + ')' + _nl + '",\n    "    ' + _nl + '",\n    "    return result_df' + _nl + '",\n    "')
    new1 = ('Sampling rate: ~{1.0 / (result_df.index[1] - result_df.index[0]).total_seconds():.1f} Hz' + _q + ')' + _nl + '",\n    "    print(f' + _q + 'Columns: {list(result_df.columns)}' + _q + ')' + _nl + '",\n    "    ' + _nl + '",\n    "    # Restrict to second run window' + _nl + '",\n    "    result_df = result_df[(result_df.index >= RUN_START) & (result_df.index <= RUN_END)]' + _nl + '",\n    "    print(f' + _q + 'Trimmed to second run: {RUN_START} to {RUN_END}' + _q + ')' + _nl + '",\n    "    ' + _nl + '",\n    "    return result_df' + _nl + '",\n    "')
    content = content.replace(old1, new1, 1)
    # load_pmu_data
    old2 = ('    print(f' + _q + 'Time range: {result_df.index[0]} to {result_df.index[-1]}' + _q + ')' + _nl + '",\n    "    print(f' + _q + 'Columns: {list(result_df.columns)}' + _q + ')' + _nl + '",\n    "    ' + _nl + '",\n    "    return result_df' + _nl + '",\n    "')
    new2 = ('    print(f' + _q + 'Time range: {result_df.index[0]} to {result_df.index[-1]}' + _q + ')' + _nl + '",\n    "    print(f' + _q + 'Columns: {list(result_df.columns)}' + _q + ')' + _nl + '",\n    "    ' + _nl + '",\n    "    # Restrict to second run window' + _nl + '",\n    "    result_df = result_df[(result_df.index >= RUN_START) & (result_df.index <= RUN_END)]' + _nl + '",\n    "    print(f' + _q + 'Trimmed to second run: {RUN_START} to {RUN_END}' + _q + ')' + _nl + '",\n    "    ' + _nl + '",\n    "    return result_df' + _nl + '",\n    "')
    content = content.replace(old2, new2, 1)
    # load_loadbank_data
    old3 = ('    print(f' + _q + 'Loaded {len(df)} data points' + _q + ')' + _nl + '",\n    "    print(f' + _q + 'Time range: {df.index[0]} to {df.index[-1]}' + _q + ')' + _nl + '",\n    "    ' + _nl + '",\n    "    return df' + _nl + '",\n    "')
    new3 = ('    print(f' + _q + 'Loaded {len(df)} data points' + _q + ')' + _nl + '",\n    "    print(f' + _q + 'Time range: {df.index[0]} to {df.index[-1]}' + _q + ')' + _nl + '",\n    "    ' + _nl + '",\n    "    # Restrict to second run window' + _nl + '",\n    "    df = df[(df.index >= RUN_START) & (df.index <= RUN_END)]' + _nl + '",\n    "    print(f' + _q + 'Trimmed to second run: {RUN_START} to {RUN_END}' + _q + ')' + _nl + '",\n    "    ' + _nl + '",\n    "    return df' + _nl + '",\n    "')
    content = content.replace(old3, new3, 1)

    # 6. Outputs and references: Test 9C -> Test 9B, FDR01 -> FDR08, scenario text for 9B
    content = content.replace("Test 9C", "Test 9B")
    content = content.replace("FDR01", "FDR08")
    content = content.replace(
        "**Test 9B Scenario**: In this test, the loadbank is connected to the grid, allowing us to observe harmonics coming from the grid itself.",
        "**Test 9B Scenario**: In this test, the Moxion MP75 supplies the load bank only (no grid), allowing us to observe harmonics from the battery system."
    )

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("Patch done (title, config, loadbank, event log, time slice, Test 9B/FDR08 refs).")

if __name__ == "__main__":
    main()
