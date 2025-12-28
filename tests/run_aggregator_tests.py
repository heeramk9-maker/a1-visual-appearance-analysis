import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.aggregator import aggregate_results


def run():
    try:
        imgs = [
            {"visual_measurements": {"gender_expression": {"score": 1}}, "attributes": {"color": "blue"}},
            {"visual_measurements": {"gender_expression": {"score": 2}}, "attributes": {"color": "blue"}},
            {"visual_measurements": {"gender_expression": {"score": 3}}, "attributes": {"color": "red"}},
        ]
        agg = aggregate_results(imgs)
        # using gender_expression as the sample dimension
        if agg["visual_consensus"]["gender_expression"]["mean"] != 2.0:
            print("ERROR: mean wrong")
            return 1
        if agg["attribute_summary"]["color"]["value"] != "blue":
            print("ERROR: attribute majority wrong")
            return 1

        imgs2 = [
            {"visual_measurements": {"gender_expression": {"score": 1}}},
            {"visual_measurements": {"gender_expression": {"score": 1}}},
            {"visual_measurements": {"gender_expression": {"score": 10}}},
        ]
        agg2 = aggregate_results(imgs2)
        if not agg2["visual_consensus"]["gender_expression"]["disagreement"]:
            print("ERROR: expected score disagreement")
            return 1

        print("OK: aggregator tests passed")
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 2


if __name__ == '__main__':
    raise SystemExit(run())