This repository includes an `environment.yml` to create a conda environment for development.

Quick start (Windows, cmd.exe):

```bat
conda env create -f environment.yml
conda activate loda-env
python -m pip install -r requirements.txt  # ensures optional pip packages are installed
```

Notes:
- `python=3.11` chosen for compatibility; change if needed.
- For GPU PyTorch, install from the official PyTorch instructions after activating the environment.
