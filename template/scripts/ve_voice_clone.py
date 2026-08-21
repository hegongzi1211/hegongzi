#!/usr/bin/env python3
"""火山引擎「声音复刻」一次性工具：上传样本训练音色 + 查询训练状态。

不做正式合成（合成由 ve_generate.py 完成），只负责把你的声音变成可复用的 speaker_id。

子命令：
    train   上传一段干净人声样本，训练自定义音色，返回 speaker_id / status
    query   查询某个 speaker_id 的训练状态（2=成功 / 4=已激活 即可用于合成）

鉴权只用新版控制台的 X-Api-Key（从 API Key 管理页获取），无需 AppID/Token。
只用 Python 标准库。
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import uuid
from pathlib import Path

import urllib.request

CLONE_URL = "https://openspeech.bytedance.com/api/v3/tts/voice_clone"
QUERY_URL = "https://openspeech.bytedance.com/api/v3/tts/get_voice"
STATUS_NAMES = {0: "NotFound", 1: "Training", 2: "Success", 3: "Failed", 4: "Active"}


def _api_key(config_path: Path, cli_key: str | None) -> str:
    if cli_key:
        return cli_key
    key = os.environ.get("VOLCENGINE_API_KEY")
    if key:
        return key
    cfg = Path(config_path)
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            if data.get("api_key"):
                return data["api_key"]
        except (OSError, json.JSONDecodeError):
            pass
    raise SystemExit("缺少火山引擎 API Key：用 --api-key、环境变量 VOLCENGINE_API_KEY，或在 audio-pipeline.json 填 api_key")


def _headers(api_key: str) -> dict:
    return {
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
        "X-Api-Request-Id": str(uuid.uuid4()),
    }


def _detect_format(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    if ext in ("wav", "mp3", "ogg", "m4a", "aac", "pcm"):
        return ext
    raise SystemExit(f"不支持的音频格式：{path.suffix}，仅支持 wav/mp3/ogg/m4a/aac/pcm")


def train(args: argparse.Namespace) -> None:
    api_key = _api_key(args.config, args.api_key)
    sample = Path(args.sample)
    if not sample.exists():
        raise SystemExit(f"样本文件不存在：{sample}")
    if sample.stat().st_size > 10 * 1024 * 1024:
        raise SystemExit("样本文件超过 10MB 上限，请裁剪或更短的干净人声")

    fmt = _detect_format(sample)
    b64 = base64.b64encode(sample.read_bytes()).decode("ascii")

    body: dict = {"audio": {"data": b64, "format": fmt}, "language": args.language}
    if args.custom_speaker_id:
        # 后付费音色：speaker_id 固定为 custom_speaker_id，真实名称写在 custom_speaker_id
        body["speaker_id"] = "custom_speaker_id"
        body["custom_speaker_id"] = args.custom_speaker_id
    else:
        if not args.speaker_id:
            raise SystemExit("预付费音色必须指定 --speaker-id（在控制台音色库创建的 ID）")
        body["speaker_id"] = args.speaker_id
    if args.text:
        body["text"] = args.text
    extra: dict = {}
    if args.demo_text:
        extra["demo_text"] = args.demo_text
    if args.denoise:
        extra["enable_audio_denoise"] = True
    if extra:
        body["extra_params"] = extra

    req = urllib.request.Request(CLONE_URL, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers=_headers(api_key), method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())

    print("=== 训练提交结果 ===")
    print(f"code={result.get('code')} message={result.get('message')}")
    print(f"speaker_id={result.get('speaker_id')}")
    print(f"status={result.get('status')} ({STATUS_NAMES.get(result.get('status'), '?')})")
    print(f"available_training_times={result.get('available_training_times')}")
    demo = result.get("demo_audio")
    if demo:
        print(f"demo_audio(1小时有效)={demo}")
    print("\n下一步：训练是异步的，用下面命令轮询状态，直到 status=Success(2) 或 Active(4)")
    print(f"  python3 scripts/ve_voice_clone.py query --speaker-id {result.get('speaker_id')}")


def query(args: argparse.Namespace) -> None:
    api_key = _api_key(args.config, args.api_key)
    if args.custom_speaker_id:
        body = {"speaker_id": "custom_speaker_id", "custom_speaker_id": args.custom_speaker_id}
    else:
        if not args.speaker_id:
            raise SystemExit("必须指定 --speaker-id 或 --custom-speaker-id")
        body = {"speaker_id": args.speaker_id}

    req = urllib.request.Request(QUERY_URL, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers=_headers(api_key), method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())

    status = result.get("status")
    print("=== 音色查询 ===")
    print(f"code={result.get('code')} message={result.get('message')}")
    print(f"speaker_id={result.get('speaker_id')}")
    print(f"status={status} ({STATUS_NAMES.get(status, '?')})")
    print(f"available_training_times={result.get('available_training_times')}")
    demo = result.get("demo_audio")
    if demo:
        print(f"demo_audio(1小时有效)={demo}")
    if status in (2, 4):
        print("\n✅ 可合成：把上面的 speaker_id 填入 audio-pipeline.json 的 speaker_id 字段即可")
    else:
        print("\n⏳ 尚未就绪（Training=1 训练中 / Failed=3 失败），稍后重试 query")


def main() -> None:
    parser = argparse.ArgumentParser(description="火山引擎声音复刻：训练 / 查询")
    parser.add_argument("--config", default="audio-pipeline.json", help="可选，用于读取 api_key")
    parser.add_argument("--api-key", default=None, help="火山引擎 API Key（也可走环境变量 VOLCENGINE_API_KEY）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_train = sub.add_parser("train", help="上传样本训练音色")
    p_train.add_argument("--sample", required=True, help="干净人声样本（wav/mp3，<10MB，建议 10~60s 无背景音）")
    p_train.add_argument("--speaker-id", default=None, help="预付费音色：控制台音色库创建的 ID")
    p_train.add_argument("--custom-speaker-id", default=None, help="后付费音色：自定义 ID（8~256 位字母数字-_，字母开头）")
    p_train.add_argument("--text", default=None, help="参考文本，建议与样本内容一致，提升复刻精度")
    p_train.add_argument("--demo-text", default="这是我的声音复刻测试。", help="试听文本（4~300 字）")
    p_train.add_argument("--language", type=int, default=0, help="语种：0=中文(默认) 1=英文 ...")
    p_train.add_argument("--denoise", action="store_true", help="样本噪声大时开启降噪")

    p_query = sub.add_parser("query", help="查询训练状态")
    p_query.add_argument("--speaker-id", default=None)
    p_query.add_argument("--custom-speaker-id", default=None)

    args = parser.parse_args()
    if args.cmd == "train":
        train(args)
    else:
        query(args)


if __name__ == "__main__":
    main()
