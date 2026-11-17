from pathlib import Path
import sys

# Exercise the same import layout as the directly executable build scripts.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
