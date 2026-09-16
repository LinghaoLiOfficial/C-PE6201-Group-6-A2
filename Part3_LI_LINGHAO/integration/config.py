"""Portable defaults. Importing this module never loads a key or makes a call."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = "scripted"
MODEL = "deepseek/deepseek-v3.2"
BASE_URL = "https://openrouter.ai/api/v1"
DATA_DIR = ROOT / "materials" / "A2_reference_data" / "data_A"
OUTPUT_DIR = ROOT / "output" / "step1"
PROMPT_VERSION = "v2"
STEP_CAP = 8
BUDGET_USD = 0.05
AUTONOMY = "confirm"
