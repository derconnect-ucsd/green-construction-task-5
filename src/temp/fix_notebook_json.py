"""Fix truncated JSON in harmonics-study_test_9B_moxion.ipynb by removing the truncated output."""
import json

NOTEBOOK = "src/analysis/harmonics-study_test_9B_moxion.ipynb"

ROOT_TAIL = '''
 ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
'''

def main():
    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the last complete output: boundary '    },\n    {' before the truncated plotly output
    boundary = "    },\n    {"
    idx = content.rfind(boundary)
    if idx < 0:
        raise SystemExit("Could not find output boundary")
    # Truncate after the closing } of the previous output (keep "    },")
    truncate_at = idx + len("    }")
    # Keep content up to and including that }, then close outputs array, cell, cells, and add metadata
    fixed = content[:truncate_at] + ROOT_TAIL

    with open(NOTEBOOK, "w", encoding="utf-8") as f:
        f.write(fixed)

    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        obj = json.load(f)
    print("JSON is valid. Cells:", len(obj["cells"]))

if __name__ == "__main__":
    main()
