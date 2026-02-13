"""Remove duplicate LOADBANK_FILENAME/EVENT_LOG and RUN_START/RUN_END from config cell."""
NOTEBOOK_PATH = "src/analysis/harmonics-study_test_9B_moxion.ipynb"

def main():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove duplicate "LOADBANK_FILENAME = ...\n", "EVENT_LOG_FILENAME = ...\n", (keep first)
    # Exact format from file: \n    "LOADBANK_FILENAME = \"...\"\n",\n    "EVENT_LOG_FILENAME = \"...\"\n",\n    "LOADBANK_FILENAME
    _q, _nl = '\\"', '\\n'
    # Replace each duplicate (LOADBANK+EVENT_LOG) pair with a full LOAD_PROFILE_PATH line so structure stays valid
    _pload_line = 'os.path.join(\'..\', \'..\', \'data\', \'raw-inputs\', \'load-profiles\', \'load_profile_moxion_mp75.csv\')' + _nl + '",'
    dup_pair = ('\n    "LOADBANK_FILENAME = ' + _q + 'loadbank_log_20260213_223111_second run.csv' + _q + _nl + '",\n    "EVENT_LOG_FILENAME = ' + _q + 'event_log_test_9b.csv' + _q + _nl + '",\n    "LOADBANK_FILENAME')
    repl = '\n    "LOAD_PROFILE_PATH = ' + _pload_line + '\n    "LOADBANK_FILENAME'
    n = 0
    while dup_pair in content and n < 20:
        content = content.replace(dup_pair, repl, 1)
        n += 1
    # Remove duplicate LOAD_PROFILE_PATH lines (we inserted one per duplicate pair; keep only one)
    dup_pload = '\n    "LOAD_PROFILE_PATH = ' + _pload_line + '\n    "LOAD_PROFILE_PATH = '
    while dup_pload in content:
        content = content.replace(dup_pload, '\n    "LOAD_PROFILE_PATH = ', 1)

    # Remove duplicate "# Second run window... RUN_START ... RUN_END ..." block (replace with empty)
    dup_run = ('\n    "# Second run window (battery faulted on first run)' + _nl + '",\n    "RUN_START = datetime(2026, 2, 13, 14, 31, 12, tzinfo=TIMEZONE_SD)' + _nl + '",\n    "RUN_END = datetime(2026, 2, 13, 14, 37, 17, tzinfo=TIMEZONE_SD)' + _nl + '",\n    "' + _nl + '",\n    "    "# Second run window')
    n = 0
    while dup_run in content and n < 20:
        content = content.replace(dup_run, '', 1)
        n += 1
    # Fix any "    "    "# Second run that might remain (double prefix)
    content = content.replace('"    "    "# Second run window', '"    "# Second run window', 1)

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("Deduplicated config cell.")

if __name__ == "__main__":
    main()
