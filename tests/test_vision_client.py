import pytest
import json

from app.vision_client import analyze_image, mock_vision_client, VisionClient


def test_no_client_raises():
    with pytest.raises(NotImplementedError):
        analyze_image("img.jpg", "prompt")


def test_callable_client_returns_dict():
    client = mock_vision_client(return_json_string=False)
    res = analyze_image("img.jpg", "prompt", client=client)
    assert isinstance(res, dict)
    assert "visual_measurements" in res


def test_callable_client_returns_json_string():
    client = mock_vision_client(return_json_string=True)
    res = analyze_image("img.jpg", "prompt", client=client)
    assert isinstance(res, dict)
    assert "visual_measurements" in res


def test_object_with_infer_method():
    client = VisionClient(mock_vision_client(return_json_string=False))
    res = analyze_image("img.jpg", "prompt", client=client)
    assert isinstance(res, dict)


def test_invalid_prompts_type_raises():
    client = mock_vision_client()
    with pytest.raises(TypeError):
        analyze_image("img.jpg", ["not", "allowed"], client=client)


def test_list_image_raises():
    client = mock_vision_client()
    with pytest.raises(TypeError):
        analyze_image(["img1.jpg", "img2.jpg"], "prompt", client=client)


def test_client_returns_invalid_json_string_raises():
    def bad_client(i, p):
        return "not a json"

    with pytest.raises(ValueError):
        analyze_image("img.jpg", "prompt", client=bad_client)


def test_client_returns_non_dict_json_raises():
    def bad_client(i, p):
        return json.dumps([1,2,3])

    with pytest.raises(TypeError):
        analyze_image("img.jpg", "prompt", client=bad_client)
