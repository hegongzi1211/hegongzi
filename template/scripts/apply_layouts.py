#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from plan_layouts import compile_document


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply semantic content routing to real Remotion scenes.")
    parser.add_argument("--outline", default="content-outline.json")
    parser.add_argument("--scenes", default="layout-scenes.json")
    args = parser.parse_args()

    outline_path = (ROOT / args.outline).resolve()
    scenes_path = (ROOT / args.scenes).resolve()
    if not outline_path.exists():
        raise SystemExit(f"缺少内容结构文件：{outline_path}")
    current = json.loads(scenes_path.read_text(encoding="utf-8"))
    document = json.loads(outline_path.read_text(encoding="utf-8"))
    resolved = compile_document(document, current)
    scenes_path.write_text(json.dumps(resolved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("layout_types=" + ",".join(scene["type"] for scene in resolved))


if __name__ == "__main__":
    main()
