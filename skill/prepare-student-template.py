#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare-student-template.py
============================

何公子分发视频模板1（Remotion）给学员前，运行本脚本，自动产出一个
「干净、解耦、不含任何本机隐私」的学员版模板目录。

它会：
  1. 复制模板源码（排除 node_modules / .git / out / generated / public/generated
     / work / check / build 等大体积与私有产物目录）；
  2. 把所有写死何公子本机的点改成学员可替换：
       - Whisper 模型路径 → 读环境变量 WHISPER_MODEL_PATH；
       - 片尾「我是何公子」硬编码 → 改为按 audio-pipeline.json 的 outro_voice.text 定位；
       - check_voice_policy.py 的锁定校验 → 改为通用结构校验（不再认何公子音色）；
       - LockedOutro.tsx 的「我是何公子」与 // HEGONGZI 水印 → 占位名；
       - 全量文本文件中的「何公子 / 8bd592c1 / /Users/hegongzi / HEGONGZI」→ 占位或删除；
  3. 重置学员私有内容文件（script.md / content-outline.json / video-data.json）；
  4. 用一份带正确必填字段的占位 audio-pipeline.json 覆盖；
  5. 重写一篇通用 VOICE_POLICY.md / WORKBUDDY.md；
  6. 生成中性占位头像 public/outro/avatar.png（学员替换成自己的）；
  7. 写入 README-学员版.md。

用法：
  python3 prepare-student-template.py \
      --src "/Users/hegongzi/My project/视频模板1" \
      --dst "/Users/hegongzi/WorkBuddy/workbuddy视频/outputs/video-template-1-student"

不传参数时用上面的默认值。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import zlib
import struct
from pathlib import Path

# ── 路径与默认参数 ─────────────────────────────────────────────
DEFAULT_SRC = "/Users/hegongzi/My project/视频模板1"
DEFAULT_DST = "/Users/hegongzi/WorkBuddy/workbuddy视频/outputs/video-template-1-student"

# 复制时整体排除的目录 / 文件（体积大或含何公子私有产物）
EXCLUDE_DIRS = {
    "node_modules", ".git", "out", "generated", "work", "check",
    "build", ".remotion", "__pycache__", ".DS_Store",
}
EXCLUDE_NAMES = {
    ".DS_Store", "Thumbs.db",
    "layout-scenes-5skills.json", "video-data-5skills.json",  # 何公子历史示例，避免混淆
}
EXCLUDE_SUFFIXES = (
    ".bak", ".bak2026", ".disabled", ".pre-sync2.bak",
)
# 这些目录下若残留的"生成物"需额外剔除
EXTRA_FILE_EXCLUDES = {
    "public/generated",  # 何公子旁白 / 片尾音频，整目录不要
}


def should_exclude(path: Path, dst_rel_root: Path) -> bool:
    parts = path.parts
    # 任何路径片段包含 ".bak"（含 .bak-xxx / .bak_yyy / .bak_before_zzz 等变体）一律排除
    for part in parts:
        low = part.lower()
        if ".bak" in low or low.startswith(".bak"):
            return True
    if set(parts) & EXCLUDE_DIRS:
        return True
    if path.name in EXCLUDE_NAMES:
        return True
    for suf in EXCLUDE_SUFFIXES:
        if path.name.endswith(suf):
            return True
    # public/generated 整目录（按相对路径判断，跨平台）
    try:
        rel = path.relative_to(dst_rel_root)
        if rel.parts and rel.parts[0] == "public" and "generated" in rel.parts:
            return True
    except ValueError:
        pass
    return False


# ── 文本替换 ───────────────────────────────────────────────────
TEXT_EXTS = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".json", ".md", ".mdx", ".txt", ".yml", ".yaml", ".toml",
    ".css", ".scss", ".html", ".csv", ".sh", ".bat", ".env",
}

# 全量文本替换表（清理何公子身份与路径）
GLOBAL_REPLACEMENTS = [
    ("何公子", "【你的名字】"),
    ("8bd592c1-a2d8-48cf-98a0-9984bd0e8b41", "你的Voicebox档案ID"),
    ("HEGONGZI", "CREATOR"),
    ("/Users/hegongzi", ""),  # 必须在 whisper 行已先改成 env 变量后再执行
]

# build_video.py：Whisper 路径 → 环境变量
BUILD_VIDEO_WHISPER_OLD = 'WHISPER_MODEL = Path("/Users/hegongzi/.cache/hyperframes/whisper/models/ggml-small.bin")'
BUILD_VIDEO_WHISPER_NEW = 'WHISPER_MODEL = Path(os.environ.get("WHISPER_MODEL_PATH", "models/ggml-small.bin"))'

# build_video.py：extract_formal_body 末尾硬编码片尾标记 → 通用结尾定位
BUILD_VIDEO_FORMAL_OLD = '''    marker = formal.rfind("我是何公子")
    if marker < 0 or normalize_contract_text(formal[marker:]) != normalize_contract_text(outro_text):
        raise ValueError("正式口播必须以锁定片尾口播结尾")
    return formal[:marker].strip()'''

BUILD_VIDEO_FORMAL_NEW = '''    n_formal = normalize_contract_text(formal)
    n_outro = normalize_contract_text(outro_text)
    if not n_outro:
        raise ValueError("outro_text 不能为空")
    if not n_formal.endswith(n_outro):
        raise ValueError("正式口播必须以 audio-pipeline.json 的 outro_voice.text 结尾")
    marker_raw = len(formal)
    need = len(n_outro)
    seen = 0
    for i in range(len(formal) - 1, -1, -1):
        ch = formal[i]
        if ch not in " \\t\\n\\r　，。！？、；：,.!?;:\\u201c\\u201d\\u2018\\u2019\\"'（）()\\\\-—→+":
            seen += 1
        if seen == need:
            marker_raw = i
            break
    return formal[:marker_raw].strip()'''

# voicebox_generate.py：Whisper 路径 → 环境变量（同文本）
VOICEBOX_WHISPER_OLD = 'WHISPER_MODEL = Path("/Users/hegongzi/.cache/hyperframes/whisper/models/ggml-small.bin")'
VOICEBOX_WHISPER_NEW = 'WHISPER_MODEL = Path(os.environ.get("WHISPER_MODEL_PATH", "models/ggml-small.bin"))'

# check_voice_policy.py：把锁定校验器整段换成通用结构校验
CHECK_VOICE_OLD_START = "def _validate_voicebox_config(config: dict) -> None:"
CHECK_VOICE_OLD_END = "def validate_active_files() -> None:"

GENERIC_VALIDATOR = '''def _validate_voicebox_config(config: dict) -> None:
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


'''


# ── 学员占位内容 ───────────────────────────────────────────────
STUDENT_AUDIO_PIPELINE = {
    "scope": "remotion_video_template_1_only",
    "provider": "voicebox_local",
    "service_url": "http://127.0.0.1:17493",
    "profile_id": "替换为你的Voicebox档案ID",
    "profile_name": "替换为你的档案名",
    "engine": "qwen",
    "model_name": "qwen3-tts",
    "model_size": "1.7B",
    "seed": 2026071201,
    "language": "zh",
    "generation_mode": "one_continuous_take",
    "max_chunk_chars": 300,
    "crossfade_ms": 40,
    "normalize": True,
    "locked": True,
    "postprocess_filter": "highpass=f=80,lowpass=f=8000,speechnorm=e=6.5:r=0.0001:l=1",
    "outro_voice": {
        "profile_id": "替换为你的Voicebox档案ID",
        "text": "我是【你的名字】，关注我，学习更多 AI 知识。",
        "asset": "public/generated/outro-voice.wav"
    }
}

VIDEO_DATA_MIN = {"title": "", "scenes": []}

SCRIPT_MD = '''# 视频口播脚本

> 必须根据用户提供的文章、文字和图片重新写成短视频口播。禁止直接朗读原文或把摘要直接交给 TTS。

## Hook

前三秒用痛点、反常识、错误提醒或具体结果留人。

## Retention Promise

明确告诉观众看完能得到什么。

## Pain

一句话说明不知道这件事会损失什么。

## Open Loop

埋下后面必须继续看的悬念。

## Value

按“问题 → 原因 → 做法 → 结果”展开；每个观点都带真实使用场景，每 15—25 秒设置一次转折或提醒。

## Memory Phrase

写一句观众能够记住、截图或转述的话。

## Comment CTA

在固定片尾前加一句评论区互动引导。口令必须跟内容主题一致，不要每条都写“清单”。格式：

想要这期的[资料类型]，评论区打“[口令]”，我把[领取内容]整理给你。

口令规则：工具/Skill/Agent 类用“工具包”，流程类用“SOP”，模板类用“模板包”，提示词类用“提示词”，检查/避坑类用“检查表”，资料类用“资料包”，只有泛教程才用“清单”。不要用泛泛的“扣1”。

## Locked Outro CTA

我是【你的名字】，关注我，学习更多 AI 知识。

> 注意：上面这句必须与 audio-pipeline.json 里的 outro_voice.text 完全一致，
> 否则构建会报错“正式口播必须以 outro_voice.text 结尾”。

## 正式口播

这里放最终连续口播全文。它是旁白、字幕、分镜和画面文案的唯一内容源。顺序必须是：正文价值内容 → Comment CTA → 锁定片尾 CTA。
'''

VOICE_POLICY_MD = '''# 旁白音色与情感策略（学员版）

## 你自己的声音

本模板只使用你**自己本机**的 Voicebox.app 克隆音色，不绑定任何人的声音。

- 模板固定模型为 Qwen3-TTS（默认 1.7B，机器吃力可改 0.6B，但音色略飘）。
- `audio-pipeline.json` 里填你自己的 `profile_id` / `profile_name`。
- `locked: true` 表示“这是我已试听通过、可放心使用的音色”，**必须保持 true**，否则配音脚本会拒绝生成。
- 正式旁白一次连续生成，再从最终音频生成字幕和场景时间。

## 情感不靠后期加速解决

1. 先把书面摘要改成口语短句，标出停顿、反问、强调和悬念。
2. 每句话只承担一个意思；关键句前后留自然停顿。
3. Hook、提醒、转折、结果和 CTA 使用不同语气，不把全文设置成同一种强度。
4. 一次连续生成完整旁白，再从最终音频生成字幕和场景时间。
5. 禁止通过 `atempo`、后期加速、变调或逐字幕碎片生成来制造节奏。

## Voicebox 使用条件

- 只使用你自己的本机 Voicebox 档案（profile）。
- 必须整段连续生成，并对开头 12 秒和全轨做转写检查。
- 出现无关前缀、参考文字泄漏、拼接感或错字时，立即淘汰重生成。
- 只有同文案盲听通过后，才允许作为正式音色。
'''

WORKBUDDY_MD = '''# WorkBuddy 快速使用入口（学员版）

固定模板路径：你本机解压后的模板目录（在环境变量 `REMOTION_TEMPLATE_DIR` 中设置）。

不要复制模板核心逻辑，也不要改用旁边的 backup 目录。

## 硬性边界

- 只允许使用你本机的模板目录作为入口。
- WorkBuddy 的任务目录只能放输入素材、临时说明和最终产物；不得在任务目录中新建旁路视频生成脚本。
- 不要修改 `scripts/build_video.py` / `voicebox_generate.py` 的核心生成逻辑（Whisper 路径、片尾定位已参数化，无需改）。
- 不自己计算 `durationFrames`、字幕时间或音频起点；这些只能由 `python3 scripts/build_video.py` 根据同一份脚本、Voicebox 旁白和 Whisper 时间轴生成。
- 禁止直接运行 `npx remotion render`；必须通过 `npm run make:render -- --output ...`，让同步硬校验先执行。

## 开始前必读

1. `SCRIPT_TEMPLATE.md`（口播七段结构）
2. `LAYOUT_GUIDE.md`（版式规则）
3. `VOICE_POLICY.md`（你的音色策略）
4. `README-学员版.md`（安装与配音准备）

## 正确执行顺序

1. 根据新内容改写 `script.md`，并参照 `content-outline.example.json` 创建 `content-outline.json`。`hook.narration + sections[].narration` 必须逐字组成 `script.md` 的正式口播正文；固定 CTA 只放在正式口播末尾。`script.md` 正式口播必须以 `audio-pipeline.json` 的 `outro_voice.text` 结尾。
   编号内容必须把每个编号要点拆成独立 section，不能把多个方法压进一页概览。
   每条视频默认在固定片尾前添加一个“评论区互动”section，口令必须随内容变化。
2. 运行 `python3 scripts/build_video.py`：自动选版 + 配音（你的 Voicebox）+ Whisper 打轴 + 算时长。同一口播再次运行会命中 `voice_cache=hit`，不重复调用 Voicebox。
3. 确认排版后只运行一次正式入口，它会先执行同步硬校验，再渲染终稿：

   `npm run make:render -- --output out/student-video.mp4`

不要使用 `npm run make:render` 做排版预览。它是终稿入口。

## 锁定项（可改文案，勿改结构）

- `src/template/scenes/LockedOutro.tsx`：把占位名「我是【你的名字】」和 `// CREATOR` 水印改成你的；头像换成 `public/outro/avatar.png`（你的正方形人像）。
- 正文与片尾使用你自己的本机 Voicebox 档案。
- 不添加转场音效或内容提示音。
- 字幕最多两行。
- 正文旁白结束后保留 15 帧（0.5 秒）画面停顿，片尾不得与正文旁白抢帧。
'''

README_STUDENT = '''# 何公子视频模板1 · 学员版

这是剥离了何公子本机音色、路径与成片后的**干净模板**。你自己装好依赖、配好声音即可在本机复现「脚本 → 数据 → 配音 → 字幕 → 渲染」的竖屏短视频流程。

> 本模板**不包含**何公子的任何声音、头像或成片，也不绑定他的任何账号。

## 一、环境要求

- **Node ≥ 18** + npm（渲染用 Remotion）
- **Python 3.11+**（构建脚本用）
- **ffmpeg**（音频/视频处理，需在场）
- **whisper.cpp 的 `whisper-cli`**：打轴强依赖。下载一个中文 `ggml-small.bin`（或更大）模型放到任意目录，记下绝对路径，下面会用到。
- **Voicebox.app**（本机 TTS）：克隆你自己的声音，得到一个 profile（**该 profile 下只能有 1 条样本**）。

## 二、安装步骤

```bash
cd <你的模板目录>
npm install
```

设置环境变量（写到 shell 配置或 WorkBuddy 环境里）：

```bash
export REMOTION_TEMPLATE_DIR="<你的模板目录>"   # 必填
export WHISPER_MODEL_PATH="<你的 ggml-small.bin 绝对路径>"  # 打轴必填
```

## 三、换成你自己的声音

1. 打开 `audio-pipeline.json`，把 `profile_id` / `profile_name` 改成你 Voicebox 里的档案；
   `outro_voice.text` 改成你的片尾口播（如 `我是小明，关注我，学习更多 AI 知识。`）。
   `script.md` 的正式口播末尾必须和这句**完全一致**。
2. 生成你的片尾人声（一次即可）：
   ```bash
   echo "我是小明，关注我，学习更多 AI 知识。" > outro.txt
   python3 scripts/voicebox_generate.py --text-file outro.txt --output public/generated/outro-voice.wav
   ```
3. 把你的正方形人像覆盖到 `public/outro/avatar.png`（当前是占位灰图）。
4. 打开 `src/template/scenes/LockedOutro.tsx`，把 `我是【你的名字】` 与 `// CREATOR` 改成你的名字。

## 四、跑通一个视频

```bash
cd "$REMOTION_TEMPLATE_DIR"
# 1. 写口播（参考 SCRIPT_TEMPLATE.md 七段结构）
# 2. 写内容大纲（参考 content-outline.example.json）
# 3. 一键：选版 + 配音 + 打轴 + 算时长（不渲染）
python3 scripts/build_video.py
# 4. 终稿：同步校验 + 渲染
npm run make:render -- --output out/student-video.mp4
```

成片：用 `ffprobe` 确认 `1080×1440 / 30fps`。

## 五、常见问题

- **配音报错 "Voicebox新克隆尚未通过试听"**：`audio-pipeline.json` 的 `locked` 必须为 `true`（表示你已试听通过）。
- **打轴报错找不到模型**：确认 `WHISPER_MODEL_PATH` 指向真实存在的 `ggml-small.bin`。
- **构建报 "正式口播必须以 outro_voice.text 结尾"**：`script.md` 末尾没和 `audio-pipeline.json` 的 `outro_voice.text` 对齐，改一致即可。
- **check:sync 失败**：字幕/画面/旁白没同源。不要手改时长，回到 `script.md` 修正口播后重跑 `build_video.py`。
- **片尾卡片还是别人名字/头像**：改 `LockedOutro.tsx` 文案 + 换 `public/outro/avatar.png`。
'''


# ── 占位头像（纯 Python 生成中性灰图，无需 PIL） ──────────────
def write_placeholder_png(path: Path, size: int = 480) -> None:
    color = (27, 43, 58)  # 深蓝灰
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # PNG filter type 0
        for x in range(size):
            # 画一个浅色圆环作为“头像”提示
            dx, dy = x - size / 2, y - size / 2
            d = (dx * dx + dy * dy) ** 0.5
            if 150 < d < 170:
                raw += bytes((90, 200, 220))
            else:
                raw += bytes(color)
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


# ── 工具函数 ───────────────────────────────────────────────────
def copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in sorted(src.iterdir()):
        if should_exclude(item, dst):
            continue
        target = dst / item.name
        if item.is_dir():
            copy_tree(item, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def replace_in_file(path: Path, old: str, new: str, count: int = 1) -> bool:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        return False
    text = text.replace(old, new, count)
    path.write_text(text, encoding="utf-8")
    return True


def replace_block(path: Path, start_marker: str, end_marker: str, new_block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    s = text.find(start_marker)
    e = text.find(end_marker, s + len(start_marker)) if s >= 0 else -1
    if s < 0 or e < 0:
        return False
    text = text[:s] + new_block + text[e:]
    path.write_text(text, encoding="utf-8")
    return True


def global_replace_text(path: Path) -> None:
    if path.suffix.lower() not in TEXT_EXTS:
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return
    changed = False
    for old, new in GLOBAL_REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
            changed = True
    if changed:
        path.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--dst", default=DEFAULT_DST)
    args = ap.parse_args()

    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()
    if not src.is_dir():
        raise SystemExit(f"源模板目录不存在：{src}")
    if dst.exists():
        raise SystemExit(
            f"目标目录已存在：{dst}\n请先删除或换一个 --dst，避免覆盖已有内容。"
        )

    print(f"源: {src}")
    print(f"目标: {dst}")
    print("→ 复制源码（排除私有/大体积目录）...")
    copy_tree(src, dst)

    print("→ 改写核心脚本（解耦本机路径与锁定）...")
    bv = dst / "scripts" / "build_video.py"
    if (old := 'import sys\n') in bv.read_text(encoding="utf-8"):
        replace_in_file(bv, 'import sys\n', 'import sys\nimport os\n')
    replace_in_file(bv, BUILD_VIDEO_WHISPER_OLD, BUILD_VIDEO_WHISPER_NEW)
    if not replace_in_file(bv, BUILD_VIDEO_FORMAL_OLD, BUILD_VIDEO_FORMAL_NEW):
        print("  ! 警告：build_video.py 的 extract_formal_body 未匹配，请人工核对片尾定位逻辑")

    vb = dst / "scripts" / "voicebox_generate.py"
    replace_in_file(vb, VOICEBOX_WHISPER_OLD, VOICEBOX_WHISPER_NEW)

    cv = dst / "scripts" / "check_voice_policy.py"
    if not replace_block(cv, CHECK_VOICE_OLD_START, CHECK_VOICE_OLD_END, GENERIC_VALIDATOR):
        print("  ! 警告：check_voice_policy.py 校验器未匹配，请人工核对")

    print("→ 全量清理何公子身份/路径字符串...")
    for p in sorted(dst.rglob("*")):
        if p.is_file():
            global_replace_text(p)

    print("→ 重置学员私有内容文件...")
    (dst / "audio-pipeline.json").write_text(
        json.dumps(STUDENT_AUDIO_PIPELINE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # content-outline.json 用中性示例覆盖
    ex = dst / "content-outline.example.json"
    if ex.exists():
        shutil.copy2(ex, dst / "content-outline.json")
    (dst / "video-data.json").write_text(
        json.dumps(VIDEO_DATA_MIN, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (dst / "script.md").write_text(SCRIPT_MD, encoding="utf-8")
    # layout-scenes.json 由构建从 content-outline 重新生成，删掉避免旧内容冲突
    ls = dst / "layout-scenes.json"
    if ls.exists():
        ls.unlink()

    print("→ 重写一篇通用 VOICE_POLICY.md / WORKBUDDY.md / README-学员版.md...")
    (dst / "VOICE_POLICY.md").write_text(VOICE_POLICY_MD, encoding="utf-8")
    (dst / "WORKBUDDY.md").write_text(WORKBUDDY_MD, encoding="utf-8")
    (dst / "README-学员版.md").write_text(README_STUDENT, encoding="utf-8")

    print("→ 生成中性占位头像...")
    avatar = dst / "public" / "outro" / "avatar.png"
    avatar.parent.mkdir(parents=True, exist_ok=True)
    write_placeholder_png(avatar)

    # 最终扫描：确认无残留敏感字符串
    leaks = []
    for p in sorted(dst.rglob("*")):
        if p.is_file() and p.suffix.lower() in TEXT_EXTS:
            try:
                t = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for token in ("何公子", "8bd592c1", "/Users/hegongzi", "HEGONGZI"):
                if token in t:
                    leaks.append(f"{p.relative_to(dst)} : {token}")
    if leaks:
        print("\n! 发现未清理的敏感字符串，请检查：")
        for l in leaks:
            print("   ", l)
    else:
        print("\n✓ 敏感字符串扫描通过（无何公子标识/本机路径残留）")

    n_files = sum(1 for _ in dst.rglob("*") if _.is_file())
    print(f"\n✓ 学员版模板已生成：{dst}")
    print(f"  文件数：{n_files}")
    print(f"  下一步：把该目录（不含 node_modules，学员自己 npm install）打包发给学员。")


if __name__ == "__main__":
    main()
