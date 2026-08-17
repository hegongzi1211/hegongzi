"""
根治字幕"超前半句"：放弃 build_video.make_timeline 的全局字符比例映射
（whisper 文本与脚本文本字符分布不同 -> 累积前移），改为
【按场景真实音频段分段映射】：每句字幕的时间严格限制在本场景画面窗口
[a_i, b_i] 内，绝不过界到下一屏。文字仍取自脚本原意（Work Buddy 正确）。
"""
import json
import glob
import os
import subprocess
import sys

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_video as bv  # reuse compact_len / split_captions / ratio_to_time

WHISPER_MODEL = "/.cache/hyperframes/whisper/models/ggml-small.bin"


def scene_durations():
    files = sorted(glob.glob(os.path.join(ROOT, "generated", "scene-*.wav")))
    durs = []
    for f in files:
        out = subprocess.check_output(
            ["/opt/homebrew/bin/ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "default=nw=1:nk=1", f]
        ).decode().strip()
        durs.append(float(out))
    return durs


def make_timeline_scened(narrations, transcription, durs):
    # 场景真实音频时间边界（秒）
    bounds = [0.0]
    for d in durs:
        bounds.append(bounds[-1] + d)

    # 把 transcription 条目按时间分配到对应场景
    scene_trans = [[] for _ in range(len(narrations))]
    for item in transcription:
        t = item["offsets"]["from"] / 1000.0
        si = len(bounds) - 2
        for k in range(len(bounds) - 1):
            if bounds[k] <= t < bounds[k + 1]:
                si = k
                break
        scene_trans[si].append(item)

    caps = []
    for i, nar in enumerate(narrations):
        chunks = bv.split_captions(nar)
        a, b = bounds[i], bounds[i + 1]
        trans = scene_trans[i]
        if not trans:
            # 无转录回退：场景内均分
            total_c = max(1, sum(bv.compact_len(c) for c in chunks))
            consumed = 0
            for ch in chunks:
                s = a + (consumed / total_c) * (b - a)
                consumed += bv.compact_len(ch)
                e = a + (consumed / total_c) * (b - a)
                caps.append({"text": ch, "startMs": max(350, round(s * 1000)),
                             "endMs": max(round(s * 1000) + 300, round(e * 1000))})
            continue
        total_c = max(1, sum(bv.compact_len(c) for c in chunks))
        consumed = 0
        for ch in chunks:
            sr = consumed / total_c
            consumed += bv.compact_len(ch)
            er = consumed / total_c
            # 在【本场景 transcription 子集】内按字符比例定位真实时间
            s = bv.ratio_to_time(sr, trans, (b - a) * 1000) / 1000.0
            e = bv.ratio_to_time(er, trans, (b - a) * 1000) / 1000.0
            s = max(a, min(b, s))
            e = max(a, min(b, e))
            if e <= s:
                e = s + 0.3
            caps.append({"text": ch, "startMs": max(350, round(s * 1000)),
                         "endMs": max(round(s * 1000) + 300, round(e * 1000))})
    return caps


def main():
    layout = json.load(open(os.path.join(ROOT, "layout-scenes.json")))
    body = [s for s in layout if s["type"] != "outro"]
    narrations = [s.get("narration", "") or "" for s in body]
    durs = scene_durations()
    assert len(durs) == len(narrations), f"{len(durs)} wavs vs {len(narrations)} scenes"

    timing = json.load(open(os.path.join(ROOT, "generated", "narration-timing.json")))
    transcription = timing["transcription"]

    caps = make_timeline_scened(narrations, transcription, durs)

    # 校验：每句字幕必须锁在本场景窗口 [bounds[i], bounds[i+1]] 内
    bounds = [0.0]
    for d in durs:
        bounds.append(bounds[-1] + d)
    bad = 0
    for c in caps:
        mid = (c["startMs"] + c["endMs"]) / 2 / 1000.0
        si = len(bounds) - 2
        for k in range(len(bounds) - 1):
            if bounds[k] <= mid < bounds[k + 1]:
                si = k
                break
        if not (bounds[si] - 0.02 <= c["startMs"] / 1000 <= bounds[si + 1] + 0.02):
            bad += 1
            print("OUT-OF-WINDOW:", si, c["text"][:24], "start=%.2f" % (c["startMs"] / 1000),
                  "win=[%.2f,%.2f]" % (bounds[si], bounds[si + 1]))
    print(f"[caps] total={len(caps)} out-of-window={bad}")

    data = json.load(open(os.path.join(ROOT, "video-data.json")))
    data["captions"] = caps
    json.dump(data, open(os.path.join(ROOT, "video-data.json"), "w"), ensure_ascii=False, indent=2)
    json.dump(caps, open(os.path.join(ROOT, "generated", "captions.json"), "w"), ensure_ascii=False, indent=2)
    print("[caps] written to video-data.json + generated/captions.json")


if __name__ == "__main__":
    main()
