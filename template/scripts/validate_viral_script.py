#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED = ["Hook", "Retention Promise", "Pain", "Open Loop", "Value", "Memory Phrase", "CTA", "正式口播"]
FLAT_PHRASES = ["本文主要介绍", "首先我们来了解", "综上所述", "随着科技的发展"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the required short-video spoken-script stage.")
    parser.add_argument("script", type=Path)
    args = parser.parse_args()
    text = args.script.read_text(encoding="utf-8")
    missing = [name for name in REQUIRED if not re.search(rf"^##\s+{re.escape(name)}\s*$", text, re.M)]
    if missing:
        raise SystemExit(f"口播脚本缺少阶段：{', '.join(missing)}")
    spoken = text.split("## 正式口播", 1)[-1].strip()
    if len(spoken) < 180:
        raise SystemExit("正式口播过短，不能进入配音阶段")
    found = [phrase for phrase in FLAT_PHRASES if phrase in spoken]
    if found:
        raise SystemExit(f"口播仍是文章摘要语气：{', '.join(found)}")
    if "我是【你的名字】" not in spoken or "关注我" not in spoken:
        raise SystemExit("正式口播缺少锁定 CTA")
    print("viral_script=passed")


if __name__ == "__main__":
    main()
