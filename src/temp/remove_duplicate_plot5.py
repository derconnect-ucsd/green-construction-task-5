"""Remove the duplicate Plot 5 block (the one after Export) in plot_voltage_harmonics_vs_time."""
nb_path = r"c:\Users\kchia\Documents\Github\green-construction-task-5\src\analysis\harmonics-study_test_9B_moxion.ipynb"

with open(nb_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the line index (0-based) of the duplicate "    # Plot 5: Worst case summary table\n"
# (the one WITHOUT "(before show/write" in the same cell as voltage_time_variation)
# We need the second occurrence of "    # Plot 5: Worst case summary table\n",
# i.e. the one that is just "    # Plot 5: Worst case summary table\n" with no extra text.
start_remove = None
for i, line in enumerate(lines):
    if '    # Plot 5: Worst case summary table\\n"' in line and '(before show/write' not in line:
        start_remove = i
        break

if start_remove is None:
    print("Duplicate Plot 5 block not found")
    exit(1)

# End of block: last "    \n" before "    return fig"
end_remove = None
for i in range(start_remove, min(start_remove + 35, len(lines))):
    if '    return fig' in lines[i]:
        end_remove = i - 1  # exclude return fig
        break

if end_remove is None:
    print("End of block not found")
    exit(1)

# Start: include the "    \n", and "\n", before "    # Plot 5" (duplicate)
while start_remove > 0 and ('    \\n"' in lines[start_remove - 1] or '"\\n"' in lines[start_remove - 1]):
    start_remove -= 1

new_lines = lines[:start_remove] + lines[end_remove + 1:]
with open(nb_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print(f"Removed duplicate Plot 5 block (lines {start_remove + 1} to {end_remove + 1}).")
