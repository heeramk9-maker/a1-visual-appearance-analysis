from app.cache import ResultCache
from app.pipeline import process_single_image


def test_pipeline_uses_cache_and_skips_reanalysis():
    cache = ResultCache()

    # Counting client to assert it is called only once
    calls = {"n": 0}

    def counting_client(image, prompts):
        calls["n"] += 1
        # minimal A1.0-style payload
        return {
            "visual_measurements": {
                "gender_expression": {"score": 0.5, "justification": "x", "uncertain": False},
                "visual_weight": {"score": -1.0, "justification": "x", "uncertain": False},
                "embellishment": {"score": -2.0, "justification": "x", "uncertain": False},
                "unconventionality": {"score": -1.0, "justification": "x", "uncertain": False},
                "formality": {"score": 0.0, "justification": "x", "uncertain": False},
            },
            "attributes": {},
        }

    image = {"id": "img-cache-1", "source": "sample", "type": "local"}

    # first call -> populates cache
    out1 = process_single_image(image, prompts="p", client=counting_client, cache=cache)
    assert calls["n"] == 1
    assert out1["image_id"] == "img-cache-1"
    # cache get was called once and should have recorded one miss
    assert cache.stats()["misses"] == 1
    assert cache.stats()["hits"] == 0

    # second call -> served from cache (client not called again)
    out2 = process_single_image(image, prompts="p", client=counting_client, cache=cache)
    assert calls["n"] == 1
    assert out2 == out1
    assert cache.stats()["misses"] == 1
    assert cache.stats()["hits"] == 1

    # clear cache and re-run -> client called again
    cache.clear()
    out3 = process_single_image(image, prompts="p", client=counting_client, cache=cache)
    assert calls["n"] == 2
    assert out3 == out1
    assert cache.stats()["misses"] == 1
    assert cache.stats()["hits"] == 0
