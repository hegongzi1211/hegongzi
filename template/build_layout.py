# -*- coding: utf-8 -*-
"""重建 layout-scenes.json（渲染真正读取的文件）+ video-data.json（audio/captions）。
- intro/hook/workflow/outro 复用模板现有正确内容，narration 改为干净版
- 10 个 skill_detail 从 clean skill_content.json 生成，每技能 6 大块全保留
- 帧数按各场景旁白字数比例分配，总帧 = 音频时长*30，与 narration.wav 对齐
"""
import json, subprocess, os

D = "/WorkBuddy/2026-07-09-11-00-55/hgz-sp-moban-remotion"
FPS = 30

# 读取干净内容
content = json.load(open(os.path.join(D, "skill_content.json"), encoding="utf-8"))
SKILLS = content["skills"]
INTRO = content["intro"]; HOOK = content["hook"]; WORKFLOW = content["workflow"]; OUTRO = content["outro"]

# 复用现有 layout-scenes 的 intro/hook/workflow/outro 字段结构
old = json.load(open(os.path.join(D, "layout-scenes.json"), encoding="utf-8"))
old_by_type = {}
for s in old:
    old_by_type.setdefault(s["type"], []).append(s)
intro_tpl = old_by_type["intro"][0]
hook_tpl = old_by_type["hook"][0]
workflow_tpl = old_by_type["workflow"][0]
outro_tpl = old_by_type["outro"][0]

# 每个 skill 的旁白文本（与 narration.txt 完全一致）
def skill_narration(s):
    return (f"第 {s['num']} 个必装 Skill，{s['name']}。{s['oneLine']}。"
            f"我觉得最有用的点：{s['useful']}"
            f"它像什么？{s['like']}"
            f"主要用途：{s['usage']}。"
            f"推荐搭配：{s['pairing']}"
            f"注意事项：{s['caution']}"
            f"我的结论：{s['conclusion']}")

MAIN_COLORS = ["#FFA500", "#00FFFF", "#39FF14", "#FF1493", "#8B5CF6",
               "#FFD700", "#FF6B6B", "#4ECDC4", "#FF69B4", "#A78BFA"]
DETAIL_COLORS = ["#39FF14", "#00FFFF", "#FF1493", "#FFA500", "#FF69B4", "#FFFF00"]
DETAIL_LABELS = ["我觉得最有用的点", "像什么", "主要用途", "推荐搭配", "注意事项", "我的结论"]

# 构建场景
scenes = []

# intro
intro = dict(intro_tpl)
intro["narration"] = INTRO
scenes.append(intro)

# hook
hook = dict(hook_tpl)
hook["narration"] = HOOK
scenes.append(hook)

# workflow
wf = dict(workflow_tpl)
wf["narration"] = WORKFLOW
scenes.append(wf)

# 10 个 skill_detail
for i, s in enumerate(SKILLS):
    details = []
    vals = [s["useful"], s["like"], s["usage"], s["pairing"], s["caution"], s["conclusion"]]
    for j, (lab, val) in enumerate(zip(DETAIL_LABELS, vals)):
        details.append({"text": lab, "color": DETAIL_COLORS[j], "label": "说明", "value": val})
    scenes.append({
        "type": "skill_detail",
        "durationFrames": 0,  # 占位，后面按比例填
        "showSubtitle": True,
        "skillNum": s["num"],
        "skillName": s["name"],
        "desc": s["oneLine"],
        "mainColor": MAIN_COLORS[i % len(MAIN_COLORS)],
        "details": details,
        "supportText": s["conclusion"],
        "narration": skill_narration(s),
    })

# outro
outro = dict(outro_tpl)
scenes.append(outro)

# 计算各场景旁白字数（决定帧数比例）
texts = [INTRO, HOOK, WORKFLOW] + [sc["narration"] for sc in scenes[3:13]] + [OUTRO]
assert len(texts) == len(scenes), (len(texts), len(scenes))

# 音频总帧
dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", os.path.join(D, "generated/narration.wav")]))
total_frames = int(round(dur * FPS))
print("音频时长(秒):", round(dur, 2), "| 总帧:", total_frames)

total_chars = sum(len(t) for t in texts)
for sc, t in zip(scenes, texts):
    sc["durationFrames"] = max(45, int(round(len(t) / total_chars * total_frames)))

actual_total = sum(sc["durationFrames"] for sc in scenes)
print("分配后总帧:", actual_total, "| 场景数:", len(scenes))
print("各场景帧:", [sc["durationFrames"] for sc in scenes])

# 写出 layout-scenes.json
with open(os.path.join(D, "layout-scenes.json"), "w", encoding="utf-8") as f:
    json.dump(scenes, f, ensure_ascii=False, indent=1)
print("layout-scenes.json 已写")

# 写出 video-data.json（Root.tsx 用 layoutScenes 覆盖 scenes；这里提供 title/audio/captions）
video_data = {
    "title": "Codex 做自媒体必装十大 Skill",
    "audio": {
        "voiceover": {"src": "generated/narration.wav", "volume": 1, "startFrame": 45},
    },
    "captions": [],  # 稍后由 whisper 填充
}
with open(os.path.join(D, "video-data.json"), "w", encoding="utf-8") as f:
    json.dump(video_data, f, ensure_ascii=False, indent=1)
print("video-data.json 已写（captions 待填充）")
