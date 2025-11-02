- Both data files **must** be placed inside the `data/` folder in the root directory.  
- The filenames **must match exactly** (case-sensitive):
  - `F1CleanedFinal.csv`
  - `f1sim-ref-line.csv`
- Do **not** rename or move these files — several scripts reference them directly using relative paths (e.g. `data/F1CleanedFinal.csv`).

- Once repo has the following strucutre

data3001-modelling-f1-7

|-data

    |-F1CleanedFinal.csv

    |-f1sim-ref-line.csv

|-create_data.py


simply run create_data.py in the root of the directory