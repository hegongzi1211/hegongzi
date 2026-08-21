#!/usr/bin/env python3
"""火山引擎（Volcano Engine）云端配音后端，作为本机 Voicebox 的可替换方案。

与 voicebox_generate.py 保持**完全一致**的命令行契约，因此 build_video.py 可以直接切换：

    python3 scripts/ve_generate.py --text-file <旁白.txt> --output <out.wav>

仅在 audio-pipeline.json 的 provider == "volcengine" 时可用。

合成走 V3 单向流式（SSE）：
  - 请求头 X-Api-Key 鉴权 + X-Api-Resource-Id 选择「声音复刻 2.0」模型；
  - 请求体 req_params.speaker 填复刻流程得到的 icl_/S_ 开头音色 ID；
  - 响应按 SSE 帧流式返回 base64 音频，客户端解码拼接后落盘。
只用 Python 标准库（与模板其它脚本一致，无需 pip 安装 requests）。
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_voice_policy import validate_config  # noqa: E402

# V3 单向流式 SSE 合成端点（声音复刻 2.0 用 seed-icl-2.0）
TTS_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional/sse"
DEFAULT_RESOURCE_ID = "seed-icl-2.0"
WHISPER_MODEL = Path(os.environ.get("WHISPER_MODEL_PATH", "models/ggml-small.bin"))
LOCAL_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def compact(text: str) -> str:
    normalized = text.lower().translate(str.maketrans({"圖": "图", "視": "视", "頻": "频", "來": "来", "個": "个", "說": "说", "開": "开", "關": "关", "學": "学"}))
    return "".join(char for char in normalized if char.isalnum() or "\u4e00" <= char <= "\u9fff")


def _normalize_for_match(text: str) -> str:
    s = compact(text)
    drop = set("零一二三四五六七八九拾百千万亿两〇0123456789")
    return "".join(ch for ch in s if ch not in drop)


def find_spoken_start(raw: Path, intended_text: str, tmp: Path) -> float:
    """用 Whisper 定位口播正文开头，裁掉模型可能带出的前导静音/气口（非致命）。"""
    mono = tmp / "raw-16k.wav"
    transcript_base = tmp / "raw-transcript"
    try:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-ac", "1", "-ar", "16000", str(mono)], check=True)
        subprocess.run([
            "whisper-cli", "-m", str(WHISPER_MODEL), "-l", "zh", "-f", str(mono),
            "-ojf", "-of", str(transcript_base), "--no-prints",
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0.0
    try:
        transcription = json.loads(transcript_base.with_suffix(".json").read_text(encoding="utf-8"))["transcription"]
    except (OSError, KeyError, json.JSONDecodeError):
        return 0.0
    opening = compact(intended_text)[:6]
    opening_n = _normalize_for_match(intended_text)[:6]
    for item in transcription:
        spoken = compact(item["text"])
        spoken_n = _normalize_for_match(item["text"])
        if (opening in spoken
                or (len(spoken) >= 4 and spoken[:4] in opening)
                or opening_n in spoken_n
                or (len(spoken_n) >= 4 and spoken_n[:4] in opening_n)):
            return max(0.0, item["offsets"]["from"] / 1000 - 0.04)
    return 0.0


def synth_mp3(api_key: str, resource_id: str, speaker_id: str, text: str,
              sample_rate: int, speed: float, volume: float, pitch: int) -> bytes:
    """调用 V3 单向流式 SSE 接口，返回合成出的 mp3 字节。"""
    headers = {
        "X-Api-Key": api_key,
        "X-Api-Resource-Id": resource_id,
        "Content-Type": "application/json",
    }
    payload = {
        "user": {"uid": "hegongzi-student"},
        "req_params": {
            "text": text,
            "speaker": speaker_id,
            "audio_params": {
                "format": "mp3",
                "sample_rate": sample_rate,
                "speech_rate": speed,
                "loudness_rate": volume,
            },
            "additions": {
                "silence_duration": 0,
                "post_process": {"pitch": pitch},
            },
        },
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(TTS_URL, data=data, headers=headers, method="POST")
    chunks: list[bytes] = []
    with LOCAL_OPENER.open(request, timeout=180) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            if line.startswith("data:"):
                line = line[5:].strip()
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            code = obj.get("code")
            if code is not None and code != 1000:
                raise SystemExit(f"火山引擎合成失败：code={code} message={obj.get('message')}")
            data_b64 = obj.get("data")
            if data_b64:
                chunks.append(base64.b64decode(data_b64))
    if not chunks:
        raise SystemExit("火山引擎未返回任何音频数据，请检查 speaker_id / api_key / 账户额度")
    return b"".join(chunks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-pending-audition", action="store_true")
    args = parser.parse_args()

    config = json.loads((ROOT / "audio-pipeline.json").read_text(encoding="utf-8"))
    validate_config(config)
    provider = config.get("provider")
    if provider != "volcengine":
        raise SystemExit("当前 audio-pipeline.json 的 provider 不是 volcengine，已拒绝生成")

    api_key = config.get("api_key") or os.environ.get("VOLCENGINE_API_KEY")
    if not api_key:
        raise SystemExit("缺少火山引擎 API Key：请在 audio-pipeline.json 填 api_key，或设置环境变量 VOLCENGINE_API_KEY")
    speaker_id = config.get("speaker_id")
    if not speaker_id:
        raise SystemExit("audio-pipeline.json 缺少 speaker_id（复刻得到的 icl_/S_ 开头音色 ID）")
    resource_id = config.get("resource_id") or DEFAULT_RESOURCE_ID
    language = config.get("language", "zh")
    speed = float(config.get("speed", 0))
    volume = float(config.get("volume", 0))
    pitch = int(config.get("pitch", 0))
    sample_rate = int(config.get("sample_rate", 24000))
    postprocess_filter = config.get("postprocess_filter", "aresample=48000")

    full_text = args.text_file.read_text(encoding="utf-8").strip()
    if not full_text:
        raise SystemExit("旁白文本为空")

    print("narration_mode=volcengine")
    mp3_bytes = synth_mp3(api_key, resource_id, speaker_id, full_text, sample_rate, speed, volume, pitch)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ve-chunk-") as tmp_name:
        tmp = Path(tmp_name)
        mp3_path = tmp / "tts.mp3"
        mp3_path.write_bytes(mp3_bytes)
        normalized = tmp / "normalized.wav"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(mp3_path), "-ar", "48000", "-ac", "1", str(normalized),
        ], check=True)
        trim_start = find_spoken_start(normalized, full_text, tmp)
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(normalized), "-af",
            f"atrim=start={trim_start:.3f},asetpts=PTS-STARTPTS,{postprocess_filter}",
            "-ar", "48000", "-ac", "1", str(args.output),
        ], check=True)

    print(f"voice_source=volcengine:{speaker_id}")
    print(f"voice_model={resource_id}")
    print(f"prefix_trim_seconds={trim_start:.3f}")


if __name__ == "__main__":
    main()
