import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline import process_single_image

def good_client(i,p):
    return {"width_mm": 10.0, "height_mm": 5.0, "unit": "mm", "attributes": {"color": "red"}}

print(process_single_image("img.jpg","prompt",client=good_client))
