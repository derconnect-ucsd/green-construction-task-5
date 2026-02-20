"""Move the Plot 5 (worst case table) block to before fig.show() in plot_voltage_harmonics_vs_time."""
nb_path = r"c:\Users\kchia\Documents\Github\green-construction-task-5\src\analysis\harmonics-study_test_9B_moxion.ipynb"

with open(nb_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the Plot 5 block that is AFTER Export (the one without "before show" in same cell as voltage_time_variation)
# So: line containing "    # Plot 5: Worst case summary table\n" and "(before show" not in line
plot5_start = None
for i, line in enumerate(lines):
    if '    # Plot 5: Worst case summary table' in line and '(before show' not in line:
        plot5_start = i
        break
if plot5_start is None:
    print("Plot 5 block not found")
    exit(1)

# End of block: the second "    \n", before "    return fig"
plot5_end = None
for i in range(plot5_start, min(plot5_start + 35, len(lines))):
    if '    return fig' in lines[i]:
        plot5_end = i - 1
        break
if plot5_end is None:
    print("End of block not found")
    exit(1)

# Include the blank line(s) before Plot 5 in what we remove (so return fig is right after export's "    \n",)
remove_start = plot5_start
while remove_start > 0 and ('    \\n"' in lines[remove_start - 1] or '"\\n"' in lines[remove_start - 1]):
    remove_start -= 1

plot5_block = lines[plot5_start : plot5_end + 1]

# Remove block from current position
without_block = lines[:remove_start] + lines[plot5_end + 1:]

# Find "    # Display figure in notebook" in the voltage cell (same cell has harmonics_study_voltage_time_variation a few lines later)
display_idx = None
for i, line in enumerate(without_block):
    if '    # Display figure in notebook' not in line:
        continue
    for j in range(i + 1, min(i + 30, len(without_block))):
        if 'harmonics_study_voltage_time_variation' in without_block[j]:
            display_idx = i
            break
    if display_idx is not None:
        break
if display_idx is None:
    print("Display figure line not found")
    exit(1)

# Insert Plot 5 block (and one blank) before Display
new_lines = without_block[:display_idx] + plot5_block + ['        "    \\n",\n'] + without_block[display_idx:]
with open(nb_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Moved Plot 5 block before Display figure. Only one figure (with worst case table) will be shown.")
