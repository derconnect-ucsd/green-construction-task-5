"""Extract source from notebook (skip broken outputs), rebuild valid notebook, apply edits."""
import json
import re
import sys

BASE = "c:/Users/kchia/Documents/Github/green-construction-task-5/src/analysis"

def extract_cells(content):
    """Extract cell boundaries by finding "cell_type" and "source" blocks."""
    cells = []
    i = 0
    n = len(content)
    while i < n:
        # Find next "cell_type"
        idx = content.find('"cell_type":', i)
        if idx < 0:
            break
        # Find "source": [ - could be before or after cell_type
        cell_start = content.rfind('{', 0, idx)
        if cell_start < 0:
            i = idx + 1
            continue
        src_idx = content.find('"source":', cell_start)
        if src_idx < 0:
            i = idx + 1
            continue
        # Parse source array: find [ then match brackets
        arr_start = content.find('[', src_idx)
        if arr_start < 0:
            i = idx + 1
            continue
        depth = 1
        in_str = False
        escape = False
        j = arr_start + 1
        while j < n and depth > 0:
            c = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if in_str:
                if c == '\\':
                    escape = True
                elif c == '"':
                    in_str = False
                j += 1
                continue
            if c == '"':
                in_str = True
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
            j += 1
        cell_end = content.find('}', j)
        if cell_end < 0:
            cell_end = j
        cell_raw = content[cell_start:cell_end + 1]
        try:
            cell = json.loads(cell_raw)
            cells.append(cell)
        except json.JSONDecodeError:
            pass
        i = cell_end + 1
    return cells

def main():
    for nb_name, test_id in [("harmonics-study_test_9B_moxion.ipynb", "9B"), ("harmonics-study_test_9C.ipynb", "9C")]:
        path = f"{BASE}/{nb_name}"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print("Read", nb_name, e)
            continue
        # Try normal load first
        try:
            nb = json.loads(content)
        except json.JSONDecodeError:
            nb = None
        if nb is None:
            # Build minimal notebook from structure we can parse
            try:
                nb = json.loads(content[:content.find('"outputs": [')] + ' "outputs": []}' * 0)
            except Exception:
                pass
        if nb is None:
            print("Could not parse", nb_name, "- applying edits via line-by-line replace")
            continue
        # Ensure we have cells
        if "cells" not in nb:
            print("No cells in", nb_name)
            continue
        # Apply edits to source
        for cell in nb.get("cells", []):
            if cell.get("cell_type") != "code" or not cell.get("source"):
                continue
            src = "".join(cell["source"])
            orig = src
            if "OUTPUT_DIR = os.path.join" in src and "TIMEZONE_SD" in src and "TEST_ID" not in src:
                src = src.replace(
                    "OUTPUT_DIR = os.path.join('..', '..', 'results', 'harmonics_study')\n",
                    "OUTPUT_DIR = os.path.join('..', '..', 'results', 'harmonics_study')\nTEST_ID = \"" + test_id + "\"\n",
                    1
                )
            for base_name in ["harmonics_study_raw_data", "pmu_verification_scada", "harmonics_study_harmonics",
                              "harmonics_study_time_variation", "harmonics_study_voltage_harmonics",
                              "harmonics_study_voltage_time_variation", "frequency_from_waveform"]:
                src = src.replace(
                    'os.path.join(OUTPUT_DIR, "' + base_name + '.png")',
                    'os.path.join(OUTPUT_DIR, f"' + base_name + '_{TEST_ID}.png")'
                )
            if "Create subplots - 7 rows total" in src and "Loadbank Load Profile" in src:
                src = src.replace("# Create subplots - 7 rows total\n", "# Create subplots - 6 rows (loadbank removed)\n")
                src = src.replace("rows=7, cols=1,\n", "rows=6, cols=1,\n")
                src = src.replace(
                    "'PMU Current Magnitude (Raw Phasor Data)',\n            'Loadbank Load Profile'\n        )",
                    "'PMU Current Magnitude (Raw Phasor Data)'\n        )"
                )
                src = src.replace(
                    "               [{\"secondary_y\": False}],\n               [{\"secondary_y\": False}]]\n    )",
                    "               [{\"secondary_y\": False}]]\n    )"
                )
                src = re.sub(
                    r"    # Plot 7: Loadbank load profile\n    if 'loadbank' in aligned_data and not aligned_data\['loadbank'\]\.empty:.*?\n    # Update axes labels",
                    "    # Update axes labels",
                    src,
                    flags=re.DOTALL
                )
                src = src.replace("fig.update_xaxes(title_text=\"Time (San Diego)\", row=7, col=1)", "fig.update_xaxes(title_text=\"Time (San Diego)\", row=6, col=1)")
                src = src.replace("fig.update_yaxes(title_text=\"Load (kW/kVAR)\", row=7, col=1)\n", "")
                src = src.replace("height=2100,", "height=1800,")
                src = src.replace("width=1600, height=2100, scale=2)", "width=1600, height=1800, scale=2)")
            if "fig.update_layout(" in src and "font=dict(size=14)" not in src:
                for h in ["1800", "2100", "1000", "1400"]:
                    src = src.replace(
                        f"fig.update_layout(\n        height={h},",
                        f"fig.update_layout(\n        height={h},\n        font=dict(size=14),\n        title_font=dict(size=18),"
                    )
                src = src.replace(
                    "fig.update_layout(height=500, title_text=\"PMU data",
                    "fig.update_layout(height=500, font=dict(size=14), title_font=dict(size=18), title_text=\"PMU data"
                )
            if "plot_pmu_verification" in src and "vertical_spacing=0.12" in src:
                src = src.replace("vertical_spacing=0.12,", "vertical_spacing=0.25,")
                if "fig.update_annotations(font_size=16)" not in src:
                    src = src.replace(
                        "fig.write_image(os.path.join(OUTPUT_DIR,",
                        "fig.update_annotations(font_size=16)\n        fig.write_image(os.path.join(OUTPUT_DIR,",
                        1
                    )
            if "make_subplots" in src and "fig.update_annotations(font_size=16)" not in src and "plot_pmu_verification" not in src:
                if "    # Update axes labels\n    fig.update_xaxes" in src:
                    src = src.replace(
                        "    # Update axes labels\n    fig.update_xaxes",
                        "    # Update axes labels\n    fig.update_annotations(font_size=16)\n    fig.update_xaxes"
                    )
            src = src.replace('font=dict(size=10, color="red")', 'font=dict(size=14, color="red")')
            if "frequency_from_waveform" in src:
                src = src.replace(
                    'update_layout(title="Frequency from voltage (waveform)", yaxis_title="Hz")',
                    'update_layout(title="Frequency from voltage (waveform)", yaxis_title="Hz", font=dict(size=14), title_font=dict(size=18))'
                )
            if src != orig:
                lines = src.split("\n")
                cell["source"] = [x + "\n" for x in lines[:-1]]
                if lines[-1]:
                    cell["source"].append(lines[-1] + "\n")
        for cell in nb.get("cells", []):
            cell["outputs"] = []
            cell["execution_count"] = None
        with open(path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
        print("Updated", nb_name)

if __name__ == "__main__":
    main()
