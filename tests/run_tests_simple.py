import tempfile
import os
import sys
from pathlib import Path
import warnings

# Make project root importable when running this script directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.input_handler import load_images


def run():
    try:
        # empty list should raise
        try:
            load_images([])
            print("ERROR: empty list did not raise")
            return 1
        except ValueError:
            pass

        # create temp file
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "img1.jpg"
            p.write_bytes(b"JPEG")
            inputs = [str(p), "http://example.com/path/pic.png", "http://example.com/invalid.txt", "/non/existent.jpg", ""]
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                res = load_images(inputs)
            if len(res) != 2:
                print(f"ERROR: expected 2 valid entries, got {len(res)}")
                return 1

            # deterministic id
            r1 = load_images([str(p)])[0]
            r2 = load_images([str(p)])[0]
            if r1['id'] != r2['id']:
                print("ERROR: ids not deterministic")
                return 1

        print("OK: all simple tests passed")
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 2

if __name__ == '__main__':
    sys.exit(run())
