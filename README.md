# 何公子视频模板1 · 学员版 Skill（开源分发包）

把何公子的竖屏短视频模板（Remotion + 本地 Voicebox 配音 + Whisper 字幕打轴）做成可自己安装的 WorkBuddy Skill，学员在自己的机器上跑通「脚本 → 数据 → 配音 → 字幕 → 渲染」全流程。

> 此仓库含两部分：**Skill 本体**（告诉 WorkBuddy 怎么做） + **干净模板目录**（Remotion 工程本体，已剥离原作者音色/头像/成片）。两者都要装。

## 目录结构

```
hgz-video-template1-student/
├── skill/                       # ← WorkBuddy Skill（复制到 ~/.workbuddy/skills/）
│   ├── SKILL.md                 #   技能本体，含完整流程说明
│   ├── references/
│   │   ├── SETUP.md             #   学员安装步骤（环境/配音/片尾配置）
│   │   └── student-audio-pipeline.example.json  # 配音配置示例
│   └── prepare-student-template.py  # 作者维护工具（学员无需运行，见底部说明）
└── template/                    # ← 干净 Remotion 模板（放到任意目录，设环境变量指向它）
    ├── package.json
    ├── scripts/
    ├── src/
    ├── public/
    ├── audio-pipeline.json
    ├── video-data.json
    ├── content-outline.json
    └── README-学员版.md         # 模板使用说明（学员必读）
```

## 一、安装 Skill

把 `skill/` 文件夹整个复制到 WorkBuddy 的技能目录：

- **用户级（所有项目可用）**：`~/.workbuddy/skills/hgz-sp-moban-remotion-student/`
- **项目级（仅当前项目）**：`<你的项目>/.workbuddy/skills/hgz-sp-moban-remotion-student/`

例如（macOS / Linux）：

```bash
mkdir -p ~/.workbuddy/skills
cp -R skill ~/.workbuddy/skills/hgz-sp-moban-remotion-student
```

Windows（PowerShell）：

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.workbuddy\skills"
Copy-Item -Recurse skill "$env:USERPROFILE\.workbuddy\skills\hgz-sp-moban-remotion-student"
```

复制后**重启 WorkBuddy**（或刷新技能列表），在技能管理面板里能看到 `hgz-sp-moban-remotion-student`。

## 二、放置模板并配置环境变量

1. 把 `template/` 文件夹放到你机器上任意位置，例如 `~/video-template-1-student/`。
2. 设置环境变量，让 Skill 知道模板在哪、Whisper 模型在哪：

```bash
export REMOTION_TEMPLATE_DIR="$HOME/video-template-1-student"
export WHISPER_MODEL_PATH="/path/to/whisper.cpp/models/ggml-large-v3.bin"
```

（Windows 用「系统环境变量」面板添加，或 PowerShell `$env:REMOTION_TEMPLATE_DIR=...`）

## 三、环境依赖（必须先装好）

| 依赖 | 用途 | 说明 |
|---|---|---|
| **Node.js 22+** | 跑 Remotion 渲染 | 模板 `package.json` 锁定 22.x |
| **Python 3.13+** | 跑配音/打轴脚本 | 标准库即可，无需额外 pip 包 |
| **whisper.cpp（`whisper-cli`）** | 字幕时间轴 | 必须编译好，`WHISPER_MODEL_PATH` 指向 large-v3 模型 |
| **本地 Voicebox TTS 服务** | 配音 | 启动在 `127.0.0.1:17493`，用自己的声音克隆音色 |

> ⚠️ Whisper 和 Voicebox 是**硬依赖**，没有它们整条管线跑不通（不是可选项）。具体安装与配置见 `skill/references/SETUP.md`。

## 四、怎么用

在 WorkBuddy 对话里直接说，例如：

> 用视频模板1 做一个关于「用 AI 半小时做完一周的运营复盘」的 60 秒短视频

Skill 会自动：写口播脚本 → 生成配音 → Whisper 打轴 → 规划版式 → 渲染成片。

首跑前请先按 `skill/references/SETUP.md` 完成：
1. `cd $REMOTION_TEMPLATE_DIR && npm install`
2. 在 `audio-pipeline.json` 填入你自己的 Voicebox 档案、`locked: true`、片尾文案
3. 生成你自己的 `public/generated/outro-voice.wav`、替换 `public/outro/avatar.png`、改 `src/template/scenes/LockedOutro.tsx` 里的名字

## 五、更新

作者推了新版后：

```bash
git pull
cp -R skill ~/.workbuddy/skills/hgz-sp-moban-remotion-student   # 覆盖更新 Skill
cp -R template ~/video-template-1-student                       # 覆盖更新模板（注意保留你改过的 audio-pipeline.json / avatar.png / LockedOutro.tsx）
```

## 六、作者维护说明（学员可忽略）

`skill/prepare-student-template.py` 是**何公子（作者）分发前**用的：从他本机生产模板自动剥离隐私、产出上面的 `template/` 干净目录。学员拿到的是已经干净的模板，**不需要也不应该运行这个脚本**。
