from pathlib import Path


source = (Path(__file__).resolve().parent / "voicebox_generate.py").read_text(encoding="utf-8")
assert "split_into_chunks" not in source, "Formal narration must not be split into separate Voicebox generations"
assert "narration_chunks=1" in source, "Formal narration must report one continuous generation"
assert "ProxyHandler({})" in source, "Local Voicebox calls must bypass system proxies"
assert "LOCAL_OPENER.open" in source, "Voicebox HTTP calls must use the no-proxy opener"

print("voice_generation_policy=passed")
