"""
彻底修复音画字幕同步（幂等，可重复运行）。
根因：封面口播被并入 hook 画面 + voiceover.startFrame=45 把整条配音推迟 1.5s，
      导致每个画面里播放的字幕比该画面"应讲内容"整段错位约 1 个场景。

修复四步：
1. video-data.json: audio.voiceover.startFrame = 0  （配音从封面口播开始）
2. layout-scenes.json: 每个场景 durationFrames = round(真实音频秒*30)，1:1 不合并
   （intro=scene-00 时长, hook=scene-01 时长, ... outro 锁 105 帧不变）
3. VideoTemplate.tsx: hideBeforeFrame 必须 = 0（封面口播也要显字幕）—— 由组件改，本脚本只检查
4. 渲染必须直连 remotion CLI，绝不 npm run make:render（会覆盖本修复）
"""
import json
import glob
import os
import subprocess

TEMPLATE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFPROBE = "/opt/homebrew/bin/ffprobe"
FPS = 30


def scene_durations():
    files = sorted(glob.glob(os.path.join(TEMPLATE, "generated", "scene-*.wav")))
    durs = []
    for f in files:
        out = subprocess.check_output(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", f]
        ).decode().strip()
        durs.append(float(out))
    return durs


def main():
    durs = scene_durations()
    assert len(durs) == 14, f"expected 14 scene wavs, got {len(durs)}"

    layout_path = os.path.join(TEMPLATE, "layout-scenes.json")
    layout = json.load(open(layout_path))
    assert len(layout) == 15, f"expected 15 scenes, got {len(layout)}"

    for i in range(14):
        layout[i]["durationFrames"] = max(15, round(durs[i] * FPS))
    # outro(14) 保持
    json.dump(layout, open(layout_path, "w"), ensure_ascii=False, indent=2)

    vd_path = os.path.join(TEMPLATE, "video-data.json")
    vd = json.load(open(vd_path))
    vd["audio"]["voiceover"]["startFrame"] = 0
    json.dump(vd, open(vd_path, "w"), ensure_ascii=False, indent=2)

    total = sum(s["durationFrames"] for s in layout) / FPS
    print(f"[fix] scene wav durations = {[round(d,2) for d in durs]}")
    print(f"[fix] voiceover.startFrame = {vd['audio']['voiceover']['startFrame']}")
    print(f"[fix] total duration = {total:.2f}s  (narration.wav = {sum(durs):.2f}s, outro tail = {total-sum(durs):.2f}s)")
    for i in range(14):
        print(f"      scene[{i:2d}] {layout[i]['type']:11s} durF={layout[i]['durationFrames']:4d} (audio {durs[i]:.2f}s)")


if __name__ == "__main__":
    main()
