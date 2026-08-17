#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_ID = "你的Voicebox档案ID"
PROFILE_NAME = "【你的名字】终稿原声-Remotion专用"
REFERENCE_AUDIO = Path("/Downloads/终稿-音频.wav")
CLOUD_MARKERS = (
    "\u706b\u5c71",
    "volc" + "engine",
    "volcano" + "_icl",
    "mega" + "tts",
    "dou" + "bao",
    "s_x6g5" + "zef72",
)
ACTIVE_FILES = (
    "audio-pipeline.json",
    "scripts/build_video.py",
    "scripts/voicebox_generate.py",
    "README.md",
    "VOICE_POLICY.md",
    "WORKBUDDY.md",
    "COMPONENT_LIBRARY.md",
    "LAYOUT_GUIDE.md",
)
LOCAL_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def validate_config(config: dict) -> None:
    _validate_voicebox_config(config)


def _validate_voicebox_config(config: dict) -> None:
    """学员版通用校验：只检查结构合法性，不绑定任何人的音色/文件。"""
    if not isinstance(config, dict):
        raise SystemExit("audio-pipeline.json 必须是对象")
    required = {
        "provider": str,
        "service_url": str,
        "profile_id": str,
        "profile_name": str,
        "engine": str,
        "model_name": str,
        "model_size": str,
        "seed": int,
        "language": str,
        "generation_mode": str,
        "max_chunk_chars": int,
        "crossfade_ms": int,
        "normalize": bool,
        "locked": bool,
        "postprocess_filter": str,
    }
    for key, typ in required.items():
        if key not in config:
            raise SystemExit(f"audio-pipeline.json 缺少必填字段：{key}")
        value = config[key]
        ok = isinstance(value, typ) and not (typ is bool and not isinstance(value, bool))
        if typ is int:
            ok = isinstance(value, int) and not isinstance(value, bool)
        if typ is str:
            ok = isinstance(value, str) and str(value).strip() != ""
        if not ok:
            raise SystemExit(
                f"audio-pipeline.json 字段 {key} 不合法（应为 {typ.__name__} 且非空）"
            )
    if config["provider"] != "voicebox_local":
        raise SystemExit("当前模板只支持 voicebox_local（本机 Voicebox.app）方案")
    if not config["profile_id"].strip():
        raise SystemExit("profile_id 不能为空，请填你自己的 Voicebox 档案 ID")
    outro = config.get("outro_voice")
    if not isinstance(outro, dict) or not str(outro.get("text", "")).strip():
        raise SystemExit("outro_voice.text 不能为空，请填你的片尾口播文案")


def validate_active_files() -> None:
    for relative in ACTIVE_FILES:
        path = ROOT / relative
        text = path.read_text(encoding="utf-8").lower()
        found = [marker for marker in CLOUD_MARKERS if marker in text]
        if found:
            raise SystemExit(f"活动模板仍包含其他声音链路：{relative}: {', '.join(found)}")


def validate_live_profile(config: dict) -> None:
    base = config["service_url"].rstrip("/")
    try:
        with LOCAL_OPENER.open(f"{base}/profiles", timeout=5) as response:
            profiles = json.load(response)
    except (urllib.error.URLError, http.client.RemoteDisconnected) as error:
        raise SystemExit(
            f"Voicebox 服务不可用：无法连接 {base}。"
            "请先启动 Voicebox.app，并确认本地 HTTP 服务监听 17493 端口。"
        ) from error
    profile = next((item for item in profiles if item.get("id") == PROFILE_ID), None)
    if not profile or profile.get("name") != PROFILE_NAME or profile.get("default_engine") != "qwen":
        raise SystemExit("Voicebox 实时档案与锁定配置不一致")
    try:
        with LOCAL_OPENER.open(f"{base}/profiles/{PROFILE_ID}/samples", timeout=5) as response:
            samples = json.load(response)
    except (urllib.error.URLError, http.client.RemoteDisconnected) as error:
        raise SystemExit(
            f"Voicebox 服务不可用：无法读取锁定档案样本 {PROFILE_ID}。"
            "请确认 Voicebox.app 已启动且档案存在。"
        ) from error
    if len(samples) != 1:
        raise SystemExit(f"锁定档案样本数异常：{len(samples)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    config = json.loads((ROOT / "audio-pipeline.json").read_text(encoding="utf-8"))
    validate_config(config)
    validate_active_files()
    if args.live:
        validate_live_profile(config)
    print(f"voice_source=voicebox:{PROFILE_ID}")
    print("voice_model=qwen3-tts:1.7B")
    print(f"reference_audio={REFERENCE_AUDIO}")
    print(f"outro_voice_source=voicebox:{PROFILE_ID}")
    print("voice_policy=locked")


if __name__ == "__main__":
    main()
