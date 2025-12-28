import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import prompts


def run():
    # Basic smoke tests: constants exist and are non-empty strings
    names = ["SYSTEM_PROMPT", "TASK_PROMPT", "ATTRIBUTE_PROMPT", "MULTI_IMAGE_INSTRUCTION"]
    for n in names:
        v = getattr(prompts, n, None)
        if not isinstance(v, str) or not v.strip():
            print(f"ERROR: {n} missing or empty")
            return 1
    print("OK: prompt constants present and non-empty")
    return 0


if __name__ == '__main__':
    raise SystemExit(run())