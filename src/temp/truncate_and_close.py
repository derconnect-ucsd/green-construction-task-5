"""Truncate notebook at broken string and append valid JSON closure, then apply edits."""
import json
import re
import sys

BASE = "c:/Users/kchia/Documents/Github/green-construction-task-5/src/analysis"

# From apply_figure_edits
def edit_cell(src, test_id):
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
    return src

def main():
    for nb_name, test_id in [("harmonics-study_test_9B_moxion.ipynb", "9B"), ("harmonics-study_test_9C.ipynb", "9C")]:
        path = f"{BASE}/{nb_name}"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        trunc = '"2026-02-13T14:34:26.96'
        pos = content.rfind(trunc)
        if pos >= 0 and pos + len(trunc) >= len(content) - 2:
            # Truncate and close: close string, close x array, close nested objects and arrays
            # Close x array, add empty y, close trace and data array, add layout and metadata, close output and cell and notebook
            closure = ('"2026-02-13T14:34:26.960666-08:00"\n                    ],\n                    "y": []\n                  }\n                ]\n              },\n              "layout": {},\n              "metadata": {}\n            }\n          }\n        }\n      ]\n    }\n  ]\n}\n')
            content = content[:pos] + closure
        try:
            nb = json.loads(content)
        except json.JSONDecodeError as e:
            print(nb_name, "still invalid after truncate:", e)
            continue
        for cell in nb.get("cells", []):
            if cell.get("cell_type") != "code" or not cell.get("source"):
                continue
            src = "".join(cell["source"])
            new_src = edit_cell(src, test_id)
            if new_src != src:
                lines = new_src.split("\n")
                cell["source"] = [x + "\n" for x in lines[:-1]]
                if lines[-1]:
                    cell["source"].append(lines[-1] + "\n")
        for cell in nb.get("cells", []):
            cell["outputs"] = []
            cell["execution_count"] = None
        with open(path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
        print("Updated", nb_name)
    return 0

if __name__ == "__main__":
    main()
