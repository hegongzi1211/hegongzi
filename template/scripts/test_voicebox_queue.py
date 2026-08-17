from unittest.mock import patch

from voicebox_generate import cancel_generation, ensure_generation_queue_idle, ensure_voicebox_model


ensure_generation_queue_idle({"generations": []})
try:
    ensure_generation_queue_idle({"generations": [{"id": "busy"}]})
except SystemExit:
    pass
else:
    raise AssertionError("An occupied Voicebox queue must stop a new build")

with patch("voicebox_generate.LOCAL_OPENER.open") as open_url:
    cancel_generation("http://127.0.0.1:17493", "stuck")
    request = open_url.call_args.args[0]
    assert request.full_url.endswith("/generate/stuck/cancel")
    assert request.get_method() == "POST"

with patch("voicebox_generate.get_json") as get_json, patch("voicebox_generate.post_json") as post_json:
    get_json.side_effect = [
        {"downloads": [{"model_name": "qwen-tts-1.7B"}], "generations": []},
        {"model_loaded": True, "model_size": "0.6B"},
    ]
    ensure_voicebox_model("http://127.0.0.1:17493", "0.6B")
    calls = [(call.args[0], call.args[1] if len(call.args) > 1 else None) for call in post_json.call_args_list]
    assert ("http://127.0.0.1:17493/models/download/cancel", {"model_name": "qwen-tts-1.7B"}) in calls
    assert any(url.endswith("/models/load?model_size=0.6B") for url, _ in calls)

print("voicebox_queue=passed")
