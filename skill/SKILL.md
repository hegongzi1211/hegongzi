---
name: hegongzi-video-student
description: 学员版 / 可分发版。基于何公子 Remotion 视频模板1（1080×1440 / 30fps / 数据驱动 + 多版式自适应）的**已解耦**版本，让学员在自己的 WorkBuddy + 自己机器上复现"脚本→数据→配音→字幕→渲染"全流程。模板路径、Whisper 模型、配音音色、片尾人名/头像全部解耦为环境变量或可替换配置，**不绑定何公子任何本机资源**。当用户说"用视频模板做个关于 XXX 的片子""复刻何公子的视频流程""把这段内容做成竖屏短视频"且使用者不是何公子本人时使用。
metadata:
  short-description: 何公子视频模板1·学员可分发版（已解耦）
  distributable: true
  locked-voice: false
agent_created: true
---

# hegongzi-video-student（学员可分发版）

这是何公子 Remotion 视频模板1 的**学员版**。目标：让学员在自己的 WorkBuddy + 自己电脑上，用同一套数据驱动流程跑出竖屏短视频。

**与锁定生产版（hgz-sp-moban-remotion）的核心区别：**
- 生产版写死何公子机器路径与"何公子终稿原声"音色，且禁止改模板。
- 本版**全部解耦**：模板目录用 `REMOTION_TEMPLATE_DIR`、Whisper 模型用 `WHISPER_MODEL_PATH`、配音用学员自己的 Voicebox 档案、片尾人名/头像可改。不绑定何公子任何本机资源。

> ⚠️ 何公子的锁定音色（`8bd592c1…` / `何公子终稿原声-Remotion专用`）**不随本技能分发**，也无授权给第三方使用。学员必须用自己的配音（本机 Voicebox 克隆音色）。

---

## 一、重要事实（避免学员踩坑）

1. **配音后端二选一：本机 Voicebox 或 火山引擎云端。** 模板按 `audio-pipeline.json` 的 `provider` 切换：默认 `voicebox_local`（本机 [Voicebox.app](https://voicebox.app)，需克隆自己的声音、profile 下只能有 1 条样本）；另提供 `volcengine`（火山引擎「声音复刻 + 大模型语音合成」云端后端，无需本机 GPU）作为可替换方案，完整接入见 `references/火山引擎语音克隆接入.md`。除这两种外（edge-tts、系统 TTS 等）仍不被接受。
2. **Whisper 是硬依赖，不是可选项。** 字幕对齐和场景时间轴强依赖 `whisper.cpp` 的 `whisper-cli` 及其 token 级时间戳。学员必须下载一个中文 `ggml-small.bin`（或更大）模型，并用 `WHISPER_MODEL_PATH` 指向它。没有 Whisper 无法生成字幕/时间轴。
3. **`locked` 必须为 `true`。** 这是"我已试听通过、可放心使用的音色"开关，不是"锁定何公子"。填成 `false` 反而会被 `voicebox_generate.py` 拒绝生成。
4. **片尾人名已解耦。** 不再硬编码"我是何公子"：`script.md` 的正式口播必须以 `audio-pipeline.json` 的 `outro_voice.text` 结尾；屏幕上的 `LockedOutro.tsx` 显示占位「我是【你的名字】」，学员改成自己的即可。
5. **何公子不随包分发任何声音/头像/成片**，也不绑定其账号。

---

## 二、环境解耦（两个变量，一次设好）

| 变量 | 作用 | 必填 |
|---|---|---|
| `REMOTION_TEMPLATE_DIR` | 指向学员本机的模板目录 | ✅ 必填 |
| `WHISPER_MODEL_PATH` | Whisper 模型文件绝对路径（打轴用） | ✅ 必填（否则打轴失败） |

学员在 WorkBuddy 里装好本技能后，技能自动读取这些变量；没设则在首次运行时提示补全。

---

## 三、学员需要先有什么

1. **干净版模板**：何公子分发的"学员版模板目录"（已剥离成片/生成音频/本机音色，仅含源码与文档）。放到本机任意目录，设好 `REMOTION_TEMPLATE_DIR`。
2. **Node ≥ 18** + **npm**（渲染用 Remotion）。
3. **Python 3.11+**（构建脚本用）。
4. **ffmpeg**（音频/视频处理，需在 PATH）。
5. **whisper.cpp `whisper-cli`** + 一个中文 `ggml-small.bin` 模型（打轴用）。
6. **Voicebox.app** + 自己的克隆音色 profile（恰好 1 条样本）。

---

## 四、自己的配音与片尾配置（必做）

1. 打开模板根目录 `audio-pipeline.json`，把 `profile_id` / `profile_name` 改成你 Voicebox 里的档案；`outro_voice.text` 改成你的片尾口播（如 `我是小明，关注我，学习更多 AI 知识。`）。**`locked` 保持 `true`**。
2. 生成你的片尾人声（一次即可，存到 `public/generated/outro-voice.wav`）：
   ```bash
   echo "我是小明，关注我，学习更多 AI 知识。" > outro.txt
   python3 scripts/voicebox_generate.py --text-file outro.txt --output public/generated/outro-voice.wav
   ```
3. 把你的正方形人像覆盖到 `public/outro/avatar.png`（当前是中性占位灰图）。
4. 打开 `src/template/scenes/LockedOutro.tsx`，把 `我是【你的名字】` 与 `// CREATOR` 水印改成你的名字。

> 参考配置见本技能 `references/student-audio-pipeline.example.json`（字段已按模板必填项补全：`provider / service_url / profile_id / profile_name / engine / model_name / model_size / seed / language / generation_mode / max_chunk_chars / crossfade_ms / normalize / locked / postprocess_filter / outro_voice`）。

---

## 五、对话即用流程（学员日常只做这一步）

学员在 WorkBuddy 说：

> 用视频模板做个关于「XXX」的竖屏短视频。

技能按以下顺序自动执行（全程在 `$REMOTION_TEMPLATE_DIR` 内）：

```bash
cd "$REMOTION_TEMPLATE_DIR"

# 1. 写口播脚本（SCRIPT_TEMPLATE 七段：Hook/Promise/Pain/OpenLoop/Value/Memory/CTA）
#    script.md 的「正式口播」必须以 audio-pipeline.json 的 outro_voice.text 结尾
# 2. 写内容大纲 → content-outline.json（参考 content-outline.example.json）

# 3. 一键生产：自动选版 + 配音（学员自己的 Voicebox）+ Whisper 打轴 + 算时长（不渲染）
python3 scripts/build_video.py

# 4. 终稿：同步校验（字幕/画面/旁白/片尾是否同源）+ 渲染成片
npm run make:render -- --output out/student-video.mp4
```

规则（与生产版一致，但音色/路径已解耦）：
- `build_video.py` 仅在口播或字幕变动时重跑；同内容重做会命中 `voice_cache=hit`，不重复调用 Voicebox。
- `make:render` 内部会先跑 `check:sync`，失败**停止渲染**，先修数据再渲。
- 不要手动改 `durationFrames` / 字幕时间 / 场景帧数，交给 `build_video.py` 生成。

---

## 六、无 Whisper / 无 Voicebox 时的兜底

- **无 Whisper**：模板无法生成字幕与场景时间轴，**没有可用兜底**（与配音后端无关）。学员必须安装 `whisper-cli` 并设 `WHISPER_MODEL_PATH`（见第三节第 5 条）。
- **无本地 Voicebox**：可改用**火山引擎云端配音**（`provider: volcengine`），无需安装 Voicebox.app，详见 `references/火山引擎语音克隆接入.md`。除火山引擎外的其它云端/系统 TTS 仍不被接受。

---

## 六之一、火山引擎云端配音（可选后端）

不想在本机跑 Voicebox 的学员，可用火山引擎「声音复刻 + 大模型语音合成」做云端配音。核心三步：

1. **克隆音色**：`python3 scripts/ve_voice_clone.py train --sample 你的人声.wav --speaker-id icl_xxx`（后付费用 `--custom-speaker-id`），再用 `query` 轮询到 `status=2/4`。
2. **切配置**：把 `audio-pipeline.json` 的 `provider` 改为 `volcengine`，填 `api_key` 与训练得到的 `speaker_id`。
3. **照常生产**：`build_video.py` 检测到 `volcengine` 会自动改调 `ve_generate.py` 合成旁白，下游 Whisper 打轴与渲染完全不变。

完整字段说明、成本与合规提醒见 `references/火山引擎语音克隆接入.md`。

## 七、固定规范（任何人都不要动结构）

- 画布 `1080×1440`、30fps、竖屏、深色科技背景。
- 自适应版式：`intro / hook / triangle / process / skill_detail / compare / workflow / overview / case / comment_cta / outro`。同版式不连续超过两页，一条视频至少三种正文版式。
- 字幕：单层硬压、最多两行、底部安全区、不与标题/卡片/片尾 CTA 重叠。
- 锁片尾组件不要改其结构（只改文案/头像为你自己的）。

---

## 八、交付检查清单

渲染完成后确认：
- `out/student-video.mp4` 存在，规格 `1080×1440` / 30fps / H.264；
- `check:sync` 通过；
- 字幕与旁白一致、字号统一；
- 片尾念的是**学员自己的**名字/口号（不是何公子），头像也是自己的。

交付时报告：成片路径、配音是否命中缓存、同步校验结果、未决风险。

---

## 附：模板预处理（何公子分发前做一次）

学员拿到的"干净版模板"由何公子用本技能自带的脚本自动产出：

```bash
python3 prepare-student-template.py \
    --src "/Users/hegongzi/My project/视频模板1" \
    --dst "<你要发出的干净模板目录>"
```

该脚本会：① 复制源码并排除 `node_modules / .git / out / generated / public/generated / work / check / build` 等大体积与私有产物；② 把 Whisper 路径改为读 `WHISPER_MODEL_PATH`、把片尾"我是何公子"硬编码改为按 `outro_voice.text` 定位、把 `check_voice_policy.py` 的锁定校验换成通用结构校验、把 `LockedOutro.tsx` 的人名/水印改成占位；③ 全量清理 `何公子 / 8bd592c1 / /Users/hegongzi / HEGONGZI`；④ 重置 `audio-pipeline.json`（带正确必填字段的占位）、`script.md`、`content-outline.json`、`video-data.json`；⑤ 生成中性占位头像；⑥ 写入 `README-学员版.md`。

发出时**不要打包 `node_modules`**（学员自己 `npm install`），也不要包含任何成片/音频。
