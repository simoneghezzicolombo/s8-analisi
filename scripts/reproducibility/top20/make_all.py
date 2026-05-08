import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
scripts = [
    "calculate_lombardia_annualization.py",
    "plot_static_bar_slide.py",
]

for script in scripts:
    print(f"\n--- Running {script} ---")
    subprocess.check_call([sys.executable, str(SCRIPT_DIR / script)], cwd=ROOT)
