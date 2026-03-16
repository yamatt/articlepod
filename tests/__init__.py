from pathlib import Path
import sys

# Make src and repository-root packages importable when running tests directly.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PYTHON = REPO_ROOT / "src" / "python"

if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
if str(SRC_PYTHON) not in sys.path:
    sys.path.append(str(SRC_PYTHON))
