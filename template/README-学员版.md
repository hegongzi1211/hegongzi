# 何公子视频模板1 · 学员版

这是剥离了何公子本机音色、路径与成片后的**干净模板**。你自己装好依赖、配好声音即可在本机复现「脚本 → 数据 → 配音 → 字幕 → 渲染」的竖屏短视频流程。

> 本模板**不包含**何公子的任何声音、头像或成片，也不绑定他的任何账号。

## 一、环境要求

- **Node ≥ 18** + npm（渲染用 Remotion）
- **Python 3.11+**（构建脚本用）
- **ffmpeg**（音频/视频处理，需在场）
- **whisper.cpp 的 `whisper-cli`**：打轴强依赖。下载一个中文 `ggml-small.bin`（或更大）模型放到任意目录，记下绝对路径，下面会用到。
- **配音后端二选一**：
  - **本机 Voicebox.app**（默认）：克隆你自己的声音，得到一个 profile（**该 profile 下只能有 1 条样本**）；
  - **火山引擎云端配音**（可选）：无需安装 Voicebox，只要 API Key + 复刻音色 `speaker_id`，见 `skill/references/火山引擎语音克隆接入.md`。

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

> 用火山引擎云端配音的学员：先把 `audio-pipeline.json` 的 `provider` 改为 `volcengine` 并填 `api_key` / `speaker_id`（完整流程见 `skill/references/火山引擎语音克隆接入.md`）。下面的 Voicebox 改 `profile_id` 步骤可跳过，片尾人声改用 `python3 scripts/ve_generate.py --text-file outro.txt --output public/generated/outro-voice.wav` 生成。

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
