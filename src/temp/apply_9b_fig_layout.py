"""Apply 9C-style figure layout (width, margin) to harmonics-study_test_9B_moxion.ipynb."""
import json
import sys

NOTEBOOK = "src/analysis/harmonics-study_test_9B_moxion.ipynb"
LAYOUT_ADD = [
    "        width=1200,\n",
    "        autosize=False,\n",
    "        margin=dict(l=80, r=80, t=100, b=80),\n",
]

def main():
    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        nb = json.load(f)

    replacements = [
        # (old line, new lines) - insert after "height=2100,"
        (
            ("        height=2100,\n", "        title_text=\"Raw Data Overview - Test 9B\",\n"),
            ("        height=2100,\n",) + tuple(LAYOUT_ADD) + ("        title_text=\"Raw Data Overview - Test 9B\",\n",),
        ),
        (
            ("    fig.update_layout(height=500, title_text=\"PMU data – SCADA verification (voltage, current)\")\n",),
            ("    fig.update_layout(height=500, width=1200, autosize=False, margin=dict(l=80, r=80, t=100, b=80), title_text=\"PMU data – SCADA verification (voltage, current)\")\n",),
        ),
        (
            ("        height=1000,\n", "        title_text=\"Current Harmonics Analysis - Test 9B\",\n"),
            ("        height=1000,\n",) + tuple(LAYOUT_ADD) + ("        title_text=\"Current Harmonics Analysis - Test 9B\",\n",),
        ),
        (
            ("        height=1400,\n", "        title_text=\"Current Harmonics vs Time - Test 9B\",\n"),
            ("        height=1400,\n",) + tuple(LAYOUT_ADD) + ("        title_text=\"Current Harmonics vs Time - Test 9B\",\n",),
        ),
        (
            ("        height=1000,\n", "        title_text=\"Voltage Harmonics Analysis - Test 9B\",\n"),
            ("        height=1000,\n",) + tuple(LAYOUT_ADD) + ("        title_text=\"Voltage Harmonics Analysis - Test 9B\",\n",),
        ),
        (
            ("        height=1400,\n", "        title_text=\"Voltage Harmonics vs Time - Test 9B\",\n"),
            ("        height=1400,\n",) + tuple(LAYOUT_ADD) + ("        title_text=\"Voltage Harmonics vs Time - Test 9B\",\n",),
        ),
    ]

    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = cell["source"]
        if isinstance(src, str):
            src = [src]
        new_src = []
        i = 0
        while i < len(src):
            line = src[i]
            replaced = False
            for (old_lines, new_lines) in replacements:
                if not isinstance(old_lines, tuple):
                    old_lines = (old_lines,)
                match = True
                for j, old in enumerate(old_lines):
                    if i + j >= len(src) or src[i + j] != old:
                        match = False
                        break
                if match:
                    new_src.extend(new_lines)
                    i += len(old_lines)
                    replaced = True
                    break
            if not replaced:
                new_src.append(line)
                i += 1
        cell["source"] = new_src

    with open(NOTEBOOK, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Updated", NOTEBOOK)
    return 0

if __name__ == "__main__":
    sys.exit(main())
