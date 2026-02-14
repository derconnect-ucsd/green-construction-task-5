"""
Update both harmonics-study notebooks:
- Add TEST_ID and use in all .png filenames
- Remove loadbank subplot from raw_data (6 rows), add font, fix axes
- PMU verification: more vertical_spacing, font, filename
- All figures: larger font sizes
"""
import json
import re
import sys

NOTEBOOKS = [
    ("harmonics-study_test_9B_moxion.ipynb", "9B"),
]
BASE = "c:/Users/kchia/Documents/Github/green-construction-task-5/src/analysis"


def join_source(cell):
    return "" if not cell.get("source") else "".join(cell["source"])


def set_source(cell, text):
    lines = text.split("\n")
    cell["source"] = [x + "\n" for x in lines[:-1]]
    if lines[-1]:
        cell["source"].append(lines[-1] + "\n")


def process_9b_cell(cell, test_id):
    src = join_source(cell)
    if "OUTPUT_DIR = os.path.join" in src and "TIMEZONE_SD" in src and "TEST_ID" not in src:
        src = src.replace(
            'OUTPUT_DIR = os.path.join(\'..\', \'..\', \'results\', \'harmonics_study\')\n',
            'OUTPUT_DIR = os.path.join(\'..\', \'..\', \'results\', \'harmonics_study\')\nTEST_ID = "' + test_id + '"\n',
            1
        )
        set_source(cell, src)
        return True

    # Filename replacements: use TEST_ID in output names
    for base in [
        "harmonics_study_raw_data",
        "pmu_verification_scada",
        "harmonics_study_harmonics",
        "harmonics_study_time_variation",
        "harmonics_study_voltage_harmonics",
        "harmonics_study_voltage_time_variation",
        "frequency_from_waveform",
    ]:
        old = '"' + base + '.png"'
        new = 'f"' + base + '_{TEST_ID}.png"'
        if base == "pmu_verification_scada":
            # write_image(os.path.join(OUTPUT_DIR, "pmu_verification_scada.png"))
            src = src.replace(
                'os.path.join(OUTPUT_DIR, "' + base + '.png")',
                'os.path.join(OUTPUT_DIR, f"' + base + '_{TEST_ID}.png")'
            )
        else:
            src = src.replace(
                'os.path.join(OUTPUT_DIR, "' + base + '.png")',
                'os.path.join(OUTPUT_DIR, f"' + base + '_{TEST_ID}.png")'
            )

    # Raw data plot: 7 -> 6 rows, remove loadbank row and Plot 7 block
    if "Create subplots - 7 rows total" in src and "'Loadbank Load Profile'" in src:
        src = src.replace("# Create subplots - 7 rows total\n", "# Create subplots - 6 rows (loadbank plot removed)\n")
        src = src.replace("rows=7, cols=1,\n", "rows=6, cols=1,\n")
        src = src.replace(
            "'PMU Current Magnitude (Raw Phasor Data)',\n            'Loadbank Load Profile'\n        )",
            "'PMU Current Magnitude (Raw Phasor Data)'\n        )"
        )
        src = src.replace(
            "               [{\"secondary_y\": False}],\n               [{\"secondary_y\": False}]]\n    )",
            "               [{\"secondary_y\": False}]]\n    )"
        )
        # Remove Plot 7 block (from "    # Plot 7: Loadbank" through to "    # Update axes labels")
        src = re.sub(
            r"    # Plot 7: Loadbank load profile\n    if 'loadbank' in aligned_data and not aligned_data\['loadbank'\]\.empty:.*?\n    # Update axes labels",
            "    # Update axes labels",
            src,
            flags=re.DOTALL
        )
        src = src.replace("fig.update_xaxes(title_text=\"Time (San Diego)\", row=7, col=1)", "fig.update_xaxes(title_text=\"Time (San Diego)\", row=6, col=1)")
        src = src.replace("fig.update_yaxes(title_text=\"Current (A)\", row=6, col=1)", "fig.update_yaxes(title_text=\"Current (A)\", row=6, col=1)")
        src = src.replace("fig.update_yaxes(title_text=\"Load (kW/kVAR)\", row=7, col=1)\n", "")
        src = src.replace("height=2100,", "height=1800,")
        src = src.replace("pio.write_image(fig, output_file, width=1600, height=2100, scale=2)", "pio.write_image(fig, output_file, width=1600, height=1800, scale=2)")

    # Common layout font (for raw data and all others)
    if "fig.update_layout(" in src and "height=1800" in src and "font=dict(size=14)" not in src:
        src = src.replace(
            "fig.update_layout(\n        height=1800,\n        title_text=",
            "fig.update_layout(\n        height=1800,\n        font=dict(size=14),\n        title_font=dict(size=18),\n        title_text="
        )
    if "fig.update_layout(\n        height=2100," in src:
        src = src.replace(
            "fig.update_layout(\n        height=2100,\n        title_text=",
            "fig.update_layout(\n        height=1800,\n        font=dict(size=14),\n        title_font=dict(size=18),\n        title_text="
        )
        src = src.replace("pio.write_image(fig, output_file, width=1600, height=2100, scale=2)", "pio.write_image(fig, output_file, width=1600, height=1800, scale=2)")

    # PMU verification: more vertical_spacing, font, update_annotations
    if "plot_pmu_verification" in src and "vertical_spacing=0.12" in src:
        src = src.replace("vertical_spacing=0.12,", "vertical_spacing=0.25,")
        src = src.replace(
            "fig.update_layout(height=500, title_text=\"PMU data",
            "fig.update_layout(height=500, font=dict(size=14), title_font=dict(size=18), title_text=\"PMU data"
        )
        # Add update_annotations before write_image in this cell only
        if "fig.update_annotations(font_size=16)" not in src:
            src = src.replace(
                "fig.write_image(os.path.join(OUTPUT_DIR, f\"pmu_verification_scada_{TEST_ID}.png\"))",
                "fig.update_annotations(font_size=16)\n        fig.write_image(os.path.join(OUTPUT_DIR, f\"pmu_verification_scada_{TEST_ID}.png\"))"
            )
            # In case TEST_ID replacement hasn't run yet (order of operations)
            src = src.replace(
                "fig.write_image(os.path.join(OUTPUT_DIR, \"pmu_verification_scada.png\"))",
                "fig.update_annotations(font_size=16)\n        fig.write_image(os.path.join(OUTPUT_DIR, f\"pmu_verification_scada_{TEST_ID}.png\"))"
            )

    # All other update_layout: add font
    for pattern, repl in [
        ("fig.update_layout(\n        height=1000,\n        title_text=", "fig.update_layout(\n        height=1000,\n        font=dict(size=14),\n        title_font=dict(size=18),\n        title_text="),
        ("fig.update_layout(\n        height=1400,\n        title_text=", "fig.update_layout(\n        height=1400,\n        font=dict(size=14),\n        title_font=dict(size=18),\n        title_text="),
    ]:
        if pattern in src and "font=dict(size=14)" not in src:
            src = src.replace(pattern, repl)

    # Add update_annotations after update_layout for multi-subplot figures (not PMU which we did above)
    if "make_subplots" in src and "fig.update_annotations(font_size=16)" not in src and "plot_pmu_verification" not in src:
        # Add before "    # Display figure" or "    # Export as PNG"
        if "    # Update axes labels" in src and "fig.update_annotations(font_size=16)" not in src:
            src = src.replace(
                "    # Update axes labels\n    fig.update_xaxes",
                "    # Update axes labels\n    fig.update_annotations(font_size=16)\n    fig.update_xaxes"
            )

    # IEEE 519 annotation font
    src = src.replace('font=dict(size=10, color="red")', 'font=dict(size=14, color="red")')

    # Frequency figure: add font and use TEST_ID (already in filename replacement)
    if "frequency_from_waveform.png" in src or "frequency_from_waveform_{TEST_ID}" in src:
        src = src.replace(
            "update_layout(title=\"Frequency from voltage (waveform)\", yaxis_title=\"Hz\")",
            "update_layout(title=\"Frequency from voltage (waveform)\", yaxis_title=\"Hz\", font=dict(size=14), title_font=dict(size=18))"
        )

    set_source(cell, src)
    return True


def main():
    for nb_name, test_id in NOTEBOOKS:
        path = f"{BASE}/{nb_name}"
        with open(path, "r", encoding="utf-8") as f:
            nb = json.load(f)
        for cell in nb.get("cells", []):
            if cell.get("cell_type") != "code" or not cell.get("source"):
                continue
            process_9b_cell(cell, test_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
        print("Updated", nb_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
