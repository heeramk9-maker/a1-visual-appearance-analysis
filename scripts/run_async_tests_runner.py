"""Utility to run async pipeline tests without pytest (for CI-less validation)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
# Ensure project root is on PYTHONPATH so test imports like `from app...` work
sys.path.insert(0, str(project_root))

p = project_root / "tests" / "test_pipeline_async.py"
spec = importlib.util.spec_from_file_location("test_pipeline_async", str(p))
mod = importlib.util.module_from_spec(spec)
sys.modules["test_pipeline_async"] = mod
spec.loader.exec_module(mod)


def main():
    mod.test_async_process_multiple_images_success()
    mod.test_async_isolated_error_handling()
    print("OK: async tests passed")


if __name__ == "__main__":
    main()
