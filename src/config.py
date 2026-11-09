from pathlib import Path
import os
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = Path(os.getenv("GOVERNANCE_DB_PATH", str(DATA_DIR / "governance.db")))
DATA_DIR.mkdir(parents=True, exist_ok=True)
