# Figure and export edits for harmonics-study notebooks

The notebooks in `src/analysis/` (Test 9B and 9C) had invalid JSON due to truncated cell output, so automated edits were prepared but could not be applied directly.

## What the edits do

1. **Test ID in filenames** – Add `TEST_ID = "9B"` or `"9C"` and use it in all exported PNGs, e.g. `harmonics_study_raw_data_9B.png`, `pmu_verification_scada_9C.png`, `frequency_from_waveform_9B.png`, etc.
2. **Raw data plot** – Use 6 rows instead of 7; remove the Loadbank Load Profile subplot; set height to 1800; add larger fonts.
3. **PMU verification (SCADA)** – Increase `vertical_spacing` from 0.12 to 0.25; add `font=dict(size=14)`, `title_font=dict(size=18)`, and `fig.update_annotations(font_size=16)`.
4. **All figures** – Add `font=dict(size=14)` and `title_font=dict(size=18)` to `fig.update_layout(...)` and `fig.update_annotations(font_size=16)` for subplot titles; set IEEE annotation font from 10 to 14; frequency figure gets the same layout fonts.

## How to apply the edits

1. **Clear all outputs** so the notebook JSON is valid:
   - Open each notebook in Jupyter.
   - Use **Cell → All Output → Clear** (or **Kernel → Restart & Clear Output**).
   - Save the notebook.
2. **Run the script** from the repo root or from `src/temp`:
   ```bash
   python src/temp/apply_figure_edits.py
   ```
   Or from `src/temp`:
   ```bash
   python apply_figure_edits.py
   ```
3. Re-run the notebooks to regenerate figures; exported PNGs will use the new names and styling.

## Files

- `apply_figure_edits.py` – Applies all of the above edits to both notebooks (requires valid JSON).
- `truncate_and_close.py` – Attempts to fix truncated output and then run the same edits (9B/9C truncation was not fully fixed).
- `fix_notebook_json.py` – Earlier attempt to fix truncation and edit.
- `update_notebooks_figures.py` – Original edit logic (single-notebook version).
