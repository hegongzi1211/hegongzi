#!/usr/bin/env python3
from build_video import caption_fits_policy, compact_len, split_captions


text = "你真的把它用透了吗？同样的工具，有人只当搜索引擎。今天这条视频，我把官方指南拆成十个核心技巧。"
captions = split_captions(text)

assert all(compact_len(item) <= 18 for item in captions), captions
assert not any("吗同样" in item for item in captions), captions
assert captions[0] == "你真的把它用透了吗", captions
assert "同样的工具" in captions[1], captions
assert any(item.endswith("拆成十个核心技巧") for item in captions), captions

english = split_captions("用了 Work Buddy 这么久，你真的把 Qwen3-TTS 0.6B 用透了吗？")
assert any("Work Buddy" in item for item in english), english
assert any("Qwen3-TTS 0.6B" in item for item in english), english
assert not any(item.endswith("Work Bu") or item.endswith("Qwen3-") for item in english), english
assert caption_fits_policy("Generative-Media-Skills")
assert not caption_fits_policy("这是一条明显超过十八个汉字而且无法放进两行的超长字幕内容")

print("caption_split=passed")
