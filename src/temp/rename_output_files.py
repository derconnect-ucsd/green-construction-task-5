"""
Rename output files in harmonics notebooks to include 'current' in filename.
"""
import json
import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
NOTEBOOKS = [
    os.path.join(REPO_ROOT, 'src', 'analysis', 'harmonics-study_test_9B_moxion.ipynb'),
    os.path.join(REPO_ROOT, 'src', 'analysis', 'harmonics-study_test_9C.ipynb'),
]

def update_output_filename(nb):
    """Update harmonics_study_time_variation to harmonics_study_current_time_variation."""
    modified = False
    for cell in nb['cells']:
        if cell.get('cell_type') == 'code':
            source_lines = cell.get('source', [])
            source = ''.join(source_lines)
            
            # Replace the output filename
            if 'harmonics_study_time_variation_' in source and 'harmonics_study_current_time_variation_' not in source:
                new_source = source.replace(
                    'harmonics_study_time_variation_',
                    'harmonics_study_current_time_variation_'
                )
                if new_source != source:
                    # Preserve notebook source format (list of strings)
                    new_lines = new_source.split('\n')
                    cell['source'] = [line + '\n' for line in new_lines[:-1]] + ([new_lines[-1]] if new_lines[-1] else [])
                    modified = True
    
    return modified

def main():
    for notebook_path in NOTEBOOKS:
        if not os.path.exists(notebook_path):
            print(f"Warning: Notebook not found: {notebook_path}")
            continue
        
        print(f"Processing {notebook_path}...")
        
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        # Update output filename
        modified = update_output_filename(nb)
        
        if modified:
            # Write back
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(nb, f, indent=1, ensure_ascii=False)
            
            print(f"  Updated output filename to include 'current'")
        else:
            print(f"  No changes needed (may already be updated)")

if __name__ == '__main__':
    main()
