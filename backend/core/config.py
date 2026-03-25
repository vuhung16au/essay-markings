"""Environment loading for later backend phases."""

from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]

for candidate in (".env.local", ".env", ".env.example"):
    env_path = ROOT_DIR / candidate
    if env_path.exists():
        load_dotenv(env_path, override=False)
