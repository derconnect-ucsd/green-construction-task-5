"""Apply width/margin to fig.update_layout in 9B notebook. Edits only first N lines (code section)."""
import re

NOTEBOOK = "src/analysis/harmonics-study_test_9B_moxion.ipynb"
# Only edit in first 4000 lines (source code); outputs are later
CODE_SECTION_LINES = 4000
LAYOUT_LINES = '''        "        width=1200,\\n",
        "        autosize=False,\\n",
        "        margin=dict(l=80, r=80, t=100, b=80),\\n",
'''

def main():
    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Replacements: (pattern, replacement) - pattern is line content to find, we add after height line
    # 1. PMU: single line update_layout
    for i, line in enumerate(lines[:CODE_SECTION_LINES]):
        if i >= CODE_SECTION_LINES:
            break
        if 'fig.update_layout(height=500,' in line and 'width=1200' not in line and 'PMU' in line:
            lines[i] = line.replace(
                'fig.update_layout(height=500, title_text=',
                'fig.update_layout(height=500, width=1200, autosize=False, margin=dict(l=80, r=80, t=100, b=80), title_text='
            )
            print("Updated PMU layout at line", i + 1)
            break

    # 2-5. Multi-line update_layout: after "        height=1000,\n" or "        height=1400,\n" add width/margin
    # (only when not already present)
    i = 0
    replacements_done = {"1000_Current": False, "1400_Current": False, "1000_Voltage": False, "1400_Voltage": False}
    while i < min(len(lines), CODE_SECTION_LINES) - 2:
        line = lines[i]
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        # Check for height=1000 or height=1400 followed by title_text (and no width=1200 yet)
        if 'height=1000,' in line and 'height=1000,\\n' in line:
            if i + 1 < len(lines) and 'width=1200' not in next_line and 'Current Harmonics Analysis' in next_line and not replacements_done["1000_Current"]:
                # Insert after this line
                indent = "        "
                lines.insert(i + 1, indent + '"        width=1200,\\n",\n')
                lines.insert(i + 2, indent + '"        autosize=False,\\n",\n')
                lines.insert(i + 3, indent + '"        margin=dict(l=80, r=80, t=100, b=80),\\n",\n')
                replacements_done["1000_Current"] = True
                print("Updated Current Harmonics (1000) at line", i + 1)
                i += 4
                continue
            if i + 1 < len(lines) and 'width=1200' not in next_line and 'Voltage Harmonics Analysis' in next_line and not replacements_done["1000_Voltage"]:
                indent = "        "
                lines.insert(i + 1, indent + '"        width=1200,\\n",\n')
                lines.insert(i + 2, indent + '"        autosize=False,\\n",\n')
                lines.insert(i + 3, indent + '"        margin=dict(l=80, r=80, t=100, b=80),\\n",\n')
                replacements_done["1000_Voltage"] = True
                print("Updated Voltage Harmonics (1000) at line", i + 1)
                i += 4
                continue
        if 'height=1400,' in line and 'height=1400,\\n' in line:
            if i + 1 < len(lines) and 'width=1200' not in next_line and 'Current Harmonics vs Time' in next_line and not replacements_done["1400_Current"]:
                indent = "        "
                lines.insert(i + 1, indent + '"        width=1200,\\n",\n')
                lines.insert(i + 2, indent + '"        autosize=False,\\n",\n')
                lines.insert(i + 3, indent + '"        margin=dict(l=80, r=80, t=100, b=80),\\n",\n')
                replacements_done["1400_Current"] = True
                print("Updated Current Harmonics vs Time at line", i + 1)
                i += 4
                continue
            if i + 1 < len(lines) and 'width=1200' not in next_line and 'Voltage Harmonics vs Time' in next_line and not replacements_done["1400_Voltage"]:
                indent = "        "
                lines.insert(i + 1, indent + '"        width=1200,\\n",\n')
                lines.insert(i + 2, indent + '"        autosize=False,\\n",\n')
                lines.insert(i + 3, indent + '"        margin=dict(l=80, r=80, t=100, b=80),\\n",\n')
                replacements_done["1400_Voltage"] = True
                print("Updated Voltage Harmonics vs Time at line", i + 1)
                i += 4
                continue
        i += 1

    with open(NOTEBOOK, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Done. Updated", NOTEBOOK)
    return 0

if __name__ == "__main__":
    main()
