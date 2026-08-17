import json
import tempfile
from pathlib import Path

from build_video import file_sha256, voice_cache_matches


with tempfile.TemporaryDirectory() as tmp_name:
    tmp = Path(tmp_name)
    audio = tmp / "narration.wav"
    timing = tmp / "narration-timing.json"
    cache = tmp / "narration-cache.json"
    audio.write_bytes(b"audio")
    timing.write_text("{}", encoding="utf-8")
    cache.write_text(json.dumps({
        "version": 2,
        "key": "same",
        "audio_sha256": file_sha256(audio),
        "timing_sha256": file_sha256(timing),
    }), encoding="utf-8")

    assert voice_cache_matches(cache, "same", [audio, timing])
    assert not voice_cache_matches(cache, "changed", [audio, timing])
    audio.write_bytes(b"changed")
    assert not voice_cache_matches(cache, "same", [audio, timing])
    audio.unlink()
    assert not voice_cache_matches(cache, "same", [audio, timing])

print("build_cache=passed")
