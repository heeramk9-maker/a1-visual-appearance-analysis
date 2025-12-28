import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.vision_client import analyze_image, mock_vision_client, VisionClient


def run():
    try:
        # No client
        try:
            analyze_image("img.jpg", "prompt")
            print("ERROR: missing client did not raise")
            return 1
        except NotImplementedError:
            pass

        # callable
        res = analyze_image("img.jpg", "prompt", client=mock_vision_client())
        if not isinstance(res, dict):
            print("ERROR: expected dict from mock client")
            return 1

        # infer object
        vc = VisionClient(mock_vision_client(return_json_string=True))
        res2 = analyze_image("img.jpg", "prompt", client=vc)
        if not isinstance(res2, dict):
            print("ERROR: expected dict from VisionClient infer")
            return 1

        print("OK: vision client tests passed")
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 2


if __name__ == '__main__':
    raise SystemExit(run())