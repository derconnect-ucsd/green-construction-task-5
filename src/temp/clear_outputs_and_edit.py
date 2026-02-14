"""Clear all cell outputs from a notebook to fix broken JSON, then apply figure edits."""
import re
import sys

def clear_outputs(content):
    """Replace each "outputs": [ ... ] with "outputs": [] by bracket matching."""
    result = []
    i = 0
    n = len(content)
    while i < n:
        # Look for "      \"outputs\": [" (6 spaces)
        if content[i:i+22] == '      "outputs": [':
            result.append('      "outputs": []')
            i += 22
            depth = 1
            in_string = False
            escape = False
            string_start = 0
            j = i
            while j < n and depth > 0:
                c = content[j]
                if escape:
                    escape = False
                    j += 1
                    continue
                if in_string:
                    if (j - string_start) > 5000000:
                        in_string = False
                    elif c == '\\':
                        escape = True
                    elif c == '"':
                        in_string = False
                    j += 1
                    continue
                if c == '"':
                    in_string = True
                    string_start = j
                elif c == '[':
                    depth += 1
                elif c == ']':
                    depth -= 1
                j += 1
            i = j
            continue
        result.append(content[i])
        i += 1
    return "".join(result)

def main():
    base = "c:/Users/kchia/Documents/Github/green-construction-task-5/src/analysis"
    for nb_name, test_id in [("harmonics-study_test_9B_moxion.ipynb", "9B"), ("harmonics-study_test_9C.ipynb", "9C")]:
        path = f"{base}/{nb_name}"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print("Read error", nb_name, e)
            continue
        content = clear_outputs(content)
        try:
            import json
            nb = json.loads(content)
        except json.JSONDecodeError as e:
            print("JSON still invalid", nb_name, e)
            continue
        # Apply edits to cells
        for cell in nb.get("cells", []):
            if cell.get("cell_type") != "code" or not cell.get("source"):
                continue
            src = "".join(cell["source"])
            orig = src

            # Add TEST_ID in config cell
            if "OUTPUT_DIR = os.path.join" in src and "TIMEZONE_SD" in src and "TEST_ID" not in src:
                src = src.replace(
                    "OUTPUT_DIR = os.path.join('..', '..', 'results', 'harmonics_study')\n",
                    "OUTPUT_DIR = os.path.join('..', '..', 'results', 'harmonics_study')\nTEST_ID = \"" + test_id + "\"\n",
                    1
                )

            # Filenames with TEST_ID
            for base_name in ["harmonics_study_raw_data", "pmu_verification_scada", "harmonics_study_harmonics",
                              "harmonics_study_time_variation", "harmonics_study_voltage_harmonics",
                              "harmonics_study_voltage_time_variation", "frequency_from_waveform"]:
                src = src.replace(
                    'os.path.join(OUTPUT_DIR, "' + base_name + '.png")',
                    'os.path.join(OUTPUT_DIR, f"' + base_name + '_{TEST_ID}.png")'
                )
                src = src.replace(
                    'os.path.join(OUTPUT_DIR, \'' + base_name + '.png\')',
                    'os.path.join(OUTPUT_DIR, f"' + base_name + '_{TEST_ID}.png")'
                )

            # Raw data: 7 -> 6 rows, remove loadbank
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
                # Remove Plot 7 block
                src = re.sub(
                    r"    # Plot 7: Loadbank load profile\n    if 'loadbank' in aligned_data and not aligned_data\['loadbank'\]\.empty:.*?\n    # Update axes labels",
                    "    # Update axes labels",
                    src,
                    flags=re.DOTALL
                )
                src = src.replace("fig.update_xaxes(title_text=\"Time (San Diego)\", row=7, col=1)", "fig.update_xaxes(title_text=\"Time (San Diego)\", row=6, col=1)")
                src = src.replace("fig.update_yaxes(title_text=\"Load (kW/kVAR)\", row=7, col=1)\n", "")
                src = src.replace("height=2100,", "height=1800,")
                src = src.replace("height=2100)", "height=1800)")
                src = src.replace("width=1600, height=2100, scale=2)", "width=1600, height=1800, scale=2)")

            # Layout font
            for h in ["1800", "2100", "1000", "1400", "500"]:
                if f"height={h}," in src or f"height={h})" in src:
                    if "font=dict(size=14)" not in src:
                        src = src.replace(
                            f"fig.update_layout(\n        height={h},",
                            "fig.update_layout(\n        height=" + h + ",\n        font=dict(size=14),\n        title_font=dict(size=18),"
                        )
                        src = src.replace(
                            f"fig.update_layout(\n        height={h})",
                            "fig.update_layout(\n        height=" + h + ",\n        font=dict(size=14),\n        title_font=dict(size=18))"
                        )
                    break

            # PMU vertical_spacing
            if "plot_pmu_verification" in src and "vertical_spacing=0.12" in src:
                src = src.replace("vertical_spacing=0.12,", "vertical_spacing=0.25,")
                if "fig.update_annotations(font_size=16)" not in src:
                    src = src.replace(
                        "fig.write_image(os.path.join(OUTPUT_DIR,",
                        "fig.update_annotations(font_size=16)\n        fig.write_image(os.path.join(OUTPUT_DIR,",
                        1
                    )

            # Subplot titles font (other figures)
            if "make_subplots" in src and "fig.update_annotations(font_size=16)" not in src and "plot_pmu_verification" not in src:
                if "    # Update axes labels\n    fig.update_xaxes" in src:
                    src = src.replace(
                        "    # Update axes labels\n    fig.update_xaxes",
                        "    # Update axes labels\n    fig.update_annotations(font_size=16)\n    fig.update_xaxes"
                    )

            # IEEE annotation
            src = src.replace('font=dict(size=10, color="red")', 'font=dict(size=14, color="red")')

            # Frequency figure font
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

        # Clear outputs for real
        for cell in nb.get("cells", []):
            cell["outputs"] = []
            if "execution_count" in cell:
                cell["execution_count"] = None

        with open(path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
        print("Updated", nb_name)
    return 0

if __name__ == "__main__":
    sys.exit(main())
