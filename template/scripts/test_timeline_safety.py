import math

from build_video import scene_duration_frames


timing = [{"text": "完整旁白", "offsets": {"from": 0, "to": 1501}}]
durations = scene_duration_frames(["完整旁白"], timing, 1501, tail_frames=15)

# Cover the fractional final audio frame and keep a short breathing hold before
# the locked outro starts.
assert sum(durations) >= math.ceil(1501 / 1000 * 30) + 15
assert durations[-1] == 61

print("timeline_safety=passed")
