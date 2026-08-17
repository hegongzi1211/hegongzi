#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from check_voice_policy import validate_config


ROOT = Path(__file__).resolve().parents[1]
WHISPER_MODEL = Path(os.environ.get("WHISPER_MODEL_PATH", "models/ggml-small.bin"))
LOCAL_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def compact(text: str) -> str:
    normalized = text.lower().translate(str.maketrans({"圖": "图", "視": "视", "頻": "频", "來": "来", "個": "个", "說": "说", "開": "开", "關": "关", "學": "学"}))
    return "".join(char for char in normalized if char.isalnum() or "\u4e00" <= char <= "\u9fff")


def _normalize_for_match(text: str) -> str:
    """去除阿拉伯数字与中文数字，避免 '10'↔'十个' 等转写方差导致口播开头定位失败。"""
    s = compact(text)
    drop = set("零一二三四五六七八九拾百千万亿两〇0123456789")
    return "".join(ch for ch in s if ch not in drop)


def find_spoken_start(raw: Path, intended_text: str, tmp: Path) -> float:
    mono = tmp / "raw-16k.wav"
    transcript_base = tmp / "raw-transcript"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-ac", "1", "-ar", "16000", str(mono)], check=True)
    subprocess.run([
        "whisper-cli", "-m", str(WHISPER_MODEL), "-l", "zh", "-f", str(mono),
        "-ojf", "-of", str(transcript_base), "--no-prints",
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    transcription = json.loads(transcript_base.with_suffix(".json").read_text(encoding="utf-8"))["transcription"]
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
    print("warn: 未在转写中定位口播正文开头，回退 trim_start=0.0（可能存在轻微对齐偏移）")
    return 0.0


def get_json(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with LOCAL_OPENER.open(request, timeout=30) as response:
        return json.loads(response.read())


def post_json(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload or {}, ensure_ascii=False).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with LOCAL_OPENER.open(request, timeout=30) as response:
        raw = response.read()
        return json.loads(raw) if raw else {}


def ensure_service(url: str) -> None:
    try:
        get_json(f"{url}/health")
    except (urllib.error.URLError, http.client.RemoteDisconnected) as error:
        try:
            subprocess.run(["open", "-a", "Voicebox"], check=True)
        except subprocess.CalledProcessError as open_error:
            raise SystemExit(
                f"Voicebox 服务不可用：无法连接 {url}，并且无法自动启动 Voicebox.app。"
                "请手动启动 Voicebox.app 后重试。"
            ) from open_error
        time.sleep(3)
        try:
            get_json(f"{url}/health")
        except (urllib.error.URLError, http.client.RemoteDisconnected) as retry_error:
            raise SystemExit(
                f"Voicebox 服务不可用：已尝试启动 Voicebox.app，但 {url} 仍未响应。"
                "请确认应用已打开、本地 HTTP 服务已启用并监听 17493 端口。"
            ) from retry_error


def qwen_tts_model_name(model_size: str) -> str:
    return f"qwen-tts-{model_size}"


def cancel_model_download(base: str, model_name: str) -> None:
    try:
        post_json(f"{base}/models/download/cancel", {"model_name": model_name})
    except Exception:
        pass


def ensure_voicebox_model(base: str, model_size: str) -> None:
    expected = qwen_tts_model_name(model_size)
    try:
        active_tasks = get_json(f"{base}/tasks/active")
    except Exception:
        active_tasks = {}
    for task in active_tasks.get("downloads", []):
        model_name = task.get("model_name")
        if model_name and model_name.startswith("qwen-tts-") and model_name != expected:
            cancel_model_download(base, model_name)

    query = urllib.parse.urlencode({"model_size": model_size})
    post_json(f"{base}/models/load?{query}")
    health = get_json(f"{base}/health")
    if not health.get("model_loaded") or health.get("model_size") != model_size:
        raise SystemExit(f"Voicebox未加载锁定模型：需要{model_size}，当前={health.get('model_size')}")
    print(f"voicebox_model_ready={model_size}")


def ensure_generation_queue_idle(active_tasks: dict) -> None:
    generations = active_tasks.get("generations", [])
    if generations:
        raise SystemExit("Voicebox已有配音任务正在运行，已停止本次构建，避免继续排队")


def cancel_generation(base: str, generation_id: str) -> None:
    request = urllib.request.Request(
        f"{base}/generate/{generation_id}/cancel",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with LOCAL_OPENER.open(request, timeout=10) as response:
        response.read()


def generate_one(base: str, payload_template: dict, text: str, out_path: Path, deadline_seconds: int | None = None) -> None:
    """一次生成完整旁白，并在服务异常时取消任务后重试。"""
    if deadline_seconds is None:
        deadline_seconds = int(os.environ.get("VOICEBOX_DEADLINE", "2400"))
    payload = dict(payload_template)
    payload["text"] = text
    last_id = None
    for attempt in range(3):
        try:
            generation = get_json(f"{base}/generate", payload)
            last_id = generation["id"]
            deadline = time.time() + deadline_seconds
            while time.time() < deadline:
                state = get_json(f"{base}/history/{generation['id']}")
                if state["status"] == "completed":
                    with LOCAL_OPENER.open(f"{base}/audio/{generation['id']}", timeout=60) as r:
                        out_path.write_bytes(r.read())
                    return
                if state["status"] == "failed":
                    raise RuntimeError(f"生成失败: {state.get('error')}")
                time.sleep(2)
            raise RuntimeError("生成超时")
        except Exception as e:
            if attempt == 2:
                raise SystemExit(f"Voicebox连续旁白生成失败：{e}")
            if last_id:
                try:
                    cancel_generation(base, last_id)
                except Exception:
                    pass
            time.sleep(3)


def split_text_for_generation(text: str, max_chars: int = 500) -> list[str]:
    """按句切分，保证每段不超过 max_chars，绝不跨句截断。"""
    sentences = [s.strip() for s in re.split(r"(?<=[。！？!?])", text) if s.strip()]
    chunks: list[str] = []
    current = ""
    for s in sentences:
        if current and len(current) + len(s) > max_chars:
            chunks.append(current)
            current = s
        else:
            current = current + s if current else s
    if current:
        chunks.append(current)
    return chunks


def concat_wavs(seg_paths: list[Path], out_path: Path) -> None:
    """用 ffmpeg concat demuxer 拼接同格式 WAV（Voicebox 各段输出格式一致）。"""
    list_file = out_path.with_suffix(".concat.txt")
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in seg_paths), encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out_path),
    ], check=True)


def generate_with_fallback(base: str, payload_template: dict, text: str, out_path: Path, tmp: Path, deadline_seconds: int = 2400) -> None:
    """优先整段生成；若服务端返回 400（输入过长），自动切分后逐段生成并拼接。"""
    try:
        generate_one(base, payload_template, text, out_path, deadline_seconds=deadline_seconds)
        return
    except SystemExit as exc:
        msg = str(exc).lower()
        if "400" in msg or "input length" in msg or "too long" in msg:
            chunks = split_text_for_generation(text, max_chars=500)
            print(f"voicebox_split={len(chunks)}")
            seg_paths: list[Path] = []
            for i, ch in enumerate(chunks):
                seg = tmp / f"seg_{i}.wav"
                generate_one(base, payload_template, ch, seg, deadline_seconds=deadline_seconds)
                seg_paths.append(seg)
            concat_wavs(seg_paths, out_path)
            return
        raise




def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-pending-audition", action="store_true")
    args = parser.parse_args()
    config = json.loads((ROOT / "audio-pipeline.json").read_text(encoding="utf-8"))
    validate_config(config)
    provider = config.get("provider")
    if provider != "voicebox_local":
        raise SystemExit("当前Remotion模板禁止使用非Voicebox声音方案")
    if not config["locked"] and not args.allow_pending_audition:
        raise SystemExit("Voicebox新克隆尚未通过试听，拒绝生成正式旁白")
    base = config["service_url"].rstrip("/")
    ensure_service(base)
    ensure_voicebox_model(base, config["model_size"])
    ensure_generation_queue_idle(get_json(f"{base}/tasks/active"))
    profiles = get_json(f"{base}/profiles")
    profile = next((item for item in profiles if item.get("id") == config["profile_id"]), None)
    if profile is None:
        raise SystemExit(f"锁定的Voicebox档案不存在：{config['profile_id']}")
    if profile.get("name") != config["profile_name"]:
        raise SystemExit(
            f"Voicebox档案名称不一致，已拒绝生成：配置={config['profile_name']}，实际={profile.get('name')}"
        )
    samples = get_json(f"{base}/profiles/{config['profile_id']}/samples")
    if len(samples) != 1:
        raise SystemExit(f"锁定的Voicebox档案样本数异常：{len(samples)}")
    full_text = args.text_file.read_text(encoding="utf-8").strip()
    payload_template = {
        "profile_id": config["profile_id"],
        "language": config["language"],
        "seed": config["seed"],
        "model_size": config["model_size"],
        "engine": config["engine"],
        "max_chunk_chars": config["max_chunk_chars"],
        "crossfade_ms": config["crossfade_ms"],
        "normalize": config["normalize"],
    }
    print("narration_mode=voicebox")
    print("narration_chunks=1")
    with tempfile.TemporaryDirectory(prefix="voicebox-chunk-") as tmp_name:
        tmp = Path(tmp_name)
        raw = tmp / "raw.wav"
        normalized = tmp / "normalized.wav"
        generate_with_fallback(base, payload_template, full_text, raw, tmp)
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(raw), "-ar", "48000", "-ac", "1", str(normalized),
        ], check=True)
        trim_start = find_spoken_start(normalized, full_text, tmp)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(normalized), "-af",
            f"atrim=start={trim_start:.3f},asetpts=PTS-STARTPTS,{config['postprocess_filter']}",
            "-ar", "48000", "-ac", "1", str(args.output),
        ], check=True)
    print(f"voice_source=voicebox:{config['profile_id']}")
    print(f"voice_model={config['model_name']}:{config['model_size']}")
    print(f"prefix_trim_seconds={trim_start:.3f}")


if __name__ == "__main__":
    main()
