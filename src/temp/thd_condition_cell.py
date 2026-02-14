# Cell source for THD-by-condition summary (to be inserted into notebook as one cell)
CELL_SOURCE = r'''
# --- THD by load condition: what conditions cause the most harmonics, IEEE compliance, no-load vs worst ---
IEEE519_THD_LIMIT_PERCENT = 5.0

def get_load_at_timestamps(timestamps, loadbank_df, phase1_start, phase1_end, load_profile_df=None):
    """Map each timestamp to load condition (R, L, C) from loadbank or load profile."""
    if loadbank_df is None or loadbank_df.empty:
        loadbank_df = pd.DataFrame()
    has_lb = not loadbank_df.empty and 'resistive_kw (kW)' in loadbank_df.columns
    r_col = 'resistive_kw (kW)' if has_lb else None
    l_col = 'inductive_kvar (kVAR)' in loadbank_df.columns and has_lb
    c_col = 'capacitive_kvar (kVAR)' in loadbank_df.columns and has_lb
    if has_lb:
        lb = loadbank_df[[c for c in ['resistive_kw (kW)', 'inductive_kvar (kVAR)', 'capacitive_kvar (kVAR)'] if c in loadbank_df.columns]]
        lb = lb.rename(columns={'resistive_kw (kW)': 'R_kw', 'inductive_kvar (kVAR)': 'L_kvar', 'capacitive_kvar (kVAR)': 'C_kvar'})
    else:
        lb = None
    # Build profile series if no loadbank: Phase 1 rows from load_profile_df
    profile_series = None
    if load_profile_df is not None and not load_profile_df.empty and phase1_start is not None:
        rcol = [c for c in load_profile_df.columns if 'Resistive' in c or c == 'Resistive Load (kW)']
        lcol = [c for c in load_profile_df.columns if 'Inductive' in c or c == 'Inductive Load (kVAR)']
        ccol = [c for c in load_profile_df.columns if 'Capacitive' in c or c == 'Capacitive Load (kVAR)']
        notes = load_profile_df.get('Notes', pd.Series(dtype=object)).fillna('')
        phase1_mask = notes.str.contains('Phase 1|Baseline & Harmonics', case=False, na=False)
        start_idx = phase1_mask.idxmax() if phase1_mask.any() else 0
        in_phase1, end_idx = False, start_idx
        for i in range(start_idx, len(load_profile_df)):
            n = str(load_profile_df.iloc[i].get('Notes', '')).strip()
            if 'Phase 1' in n or 'Baseline & Harmonics' in n:
                in_phase1 = True
                end_idx = i + 1
            elif in_phase1 and n and ('Phase 2' in n or 'Phase 3' in n):
                end_idx = i
                break
            elif in_phase1:
                end_idx = i + 1
        profile_slice = load_profile_df.iloc[start_idx:end_idx]
        if len(profile_slice) == 0:
            profile_series = None
        else:
            def num(s):
                try:
                    return float(s)
                except (TypeError, ValueError):
                    return np.nan
            R = profile_slice[rcol[0]].ffill().apply(num).fillna(0).values if rcol else np.zeros(len(profile_slice))
            L = profile_slice[lcol[0]].ffill().apply(num).fillna(0).values if lcol else np.zeros(len(profile_slice))
            C = profile_slice[ccol[0]].ffill().apply(num).fillna(0).values if ccol else np.zeros(len(profile_slice))
            profile_series = (R, L, C)  # index = elapsed second
    out = []
    for t in timestamps:
        if has_lb and lb is not None:
            # Nearest loadbank row
            idx = lb.index.get_indexer([t], method='nearest')[0]
            row = lb.iloc[idx]
            r, l, c = row.get('R_kw', 0), row.get('L_kvar', 0), row.get('C_kvar', 0)
        elif profile_series is not None and phase1_start is not None:
            elapsed = (t - phase1_start).total_seconds()
            idx = max(0, min(int(elapsed), len(profile_series[0]) - 1))
            r = profile_series[0][idx]
            l = profile_series[1][idx]
            c = profile_series[2][idx]
        else:
            r, l, c = np.nan, np.nan, np.nan
        out.append((float(r) if not np.isnan(r) else 0, float(l) if not np.isnan(l) else 0, float(c) if not np.isnan(c) else 0))
    return out

def round_load_bin(x, bins=(0, 15, 30, 45, 60, 75)):
    """Round to nearest bin value for labeling."""
    if np.isnan(x) or x < 0:
        return 0
    b = np.asarray(bins)
    i = np.argmin(np.abs(b - x))
    return int(b[i])

def summarize_thd_by_condition(time_varying_current_df, time_varying_voltage_df, loadbank_df,
                               phase1_start, phase1_end, load_profile_df=None, ieee_limit=5.0):
    """
    Answer: (1) Which conditions cause most current/voltage harmonics and do worst exceed IEEE limits?
            (2) How does no-load compare to worst condition (sensitivity)?
    """
    if time_varying_current_df is None or time_varying_current_df.empty:
        print("No time-varying current THD data.")
        return None
    # Unique timestamps (from current or voltage; use current as reference)
    ts = time_varying_current_df.index.unique()
    load_tuples = get_load_at_timestamps(ts, loadbank_df, phase1_start, phase1_end, load_profile_df)
    # Label each timestamp with (R_bin, L_bin, C_bin)
    cond_labels = [(round_load_bin(r), round_load_bin(l), round_load_bin(c)) for r, l, c in load_tuples]
    ts_to_cond = dict(zip(ts, cond_labels))
    # Add condition to current THD
    curr = time_varying_current_df.reset_index()
    curr['condition'] = curr['timestamp'].map(ts_to_cond)
    # Same for voltage
    if time_varying_voltage_df is not None and not time_varying_voltage_df.empty:
        volt = time_varying_voltage_df.reset_index()
        volt['condition'] = volt['timestamp'].map(ts_to_cond)
    else:
        volt = pd.DataFrame()
    # Aggregate by condition: max and mean THD (current: over all phases; voltage: over all phases)
    def cond_label_str(c):
        return f"R{c[0]}kW_L{c[1]}kVAR_C{c[2]}kVAR"
    curr_by_cond = curr.groupby('condition', dropna=False).agg(
        current_thd_max=('thd', 'max'),
        current_thd_mean=('thd', 'mean'),
        current_thd_min=('thd', 'min'),
        n_points=('thd', 'count')
    ).reset_index()
    curr_by_cond['condition_str'] = curr_by_cond['condition'].apply(cond_label_str)
    if not volt.empty:
        volt_by_cond = volt.groupby('condition', dropna=False).agg(
            voltage_thd_max=('thd', 'max'),
            voltage_thd_mean=('thd', 'mean'),
            voltage_thd_min=('thd', 'min'),
        ).reset_index()
        volt_by_cond['condition_str'] = volt_by_cond['condition'].apply(cond_label_str)
        curr_by_cond = curr_by_cond.merge(volt_by_cond[['condition', 'voltage_thd_max', 'voltage_thd_mean', 'voltage_thd_min']], on='condition', how='left')
    else:
        curr_by_cond['voltage_thd_max'] = np.nan
        curr_by_cond['voltage_thd_mean'] = np.nan
    # Worst condition: by current THD max (primary) or voltage
    curr_by_cond = curr_by_cond.sort_values('current_thd_max', ascending=False)
    worst_cond = curr_by_cond.iloc[0]['condition'] if len(curr_by_cond) else None
    no_load_cond = (0, 0, 0)
    no_load_row = curr_by_cond[curr_by_cond['condition'].apply(lambda c: c == no_load_cond)]
    worst_row = curr_by_cond.iloc[0] if len(curr_by_cond) else None
    # Print answers
    print("\n" + "="*70)
    print("THD BY LOAD CONDITION (Phase 1)")
    print("="*70)
    print("\n1) Conditions that cause the MOST current and voltage harmonics (worst THD):")
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
        print("   Conclusion: THD is " + ("strongly sensitive" if curr_ratio > 1.5 else "moderately sensitive" if curr_ratio > 1.1 else "not very sensitive") + " to load condition.")
    else:
        if no_load_row is None or len(no_load_row) == 0:
            print("   No-load condition (0,0,0) not found in Phase 1 data.")
        else:
            print("   Could not compare (missing worst or no-load).")
    print("\nSummary table (all conditions, by current THD max):")
    print(curr_by_cond[['condition_str', 'current_thd_max', 'current_thd_mean', 'voltage_thd_max', 'voltage_thd_mean', 'n_points']].to_string(index=False))
    print("="*70)
    return curr_by_cond

# Run the summary (uses loadbank aligned to Phase 1 if available, else load profile)
loadbank_phase1 = aligned_data.get('loadbank', pd.DataFrame())
if not loadbank_phase1.empty and phase1_start is not None and phase1_end is not None:
    loadbank_phase1 = loadbank_phase1[(loadbank_phase1.index >= phase1_start) & (loadbank_phase1.index <= phase1_end)]
load_profile_df, _ = load_load_profile()
thd_by_condition_df = summarize_thd_by_condition(
    time_varying_harmonics_df,
    time_varying_voltage_harmonics_df,
    loadbank_phase1,
    phase1_start,
    phase1_end,
    load_profile_df=load_profile_df,
    ieee_limit=IEEE519_THD_LIMIT_PERCENT,
)
'''
