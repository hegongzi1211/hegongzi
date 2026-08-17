# 学员安装指南：何公子视频模板1（学员可分发版）

本指南让你在自己的 WorkBuddy + 自己电脑上，复现"脚本→数据→配音→字幕→渲染"的竖屏短视频流程。

---

## 第一步：拿到干净版模板

向何公子获取**干净版模板目录**（已剥离成片与生成音频，仅含源码与文档）。解压/克隆到你本机任意目录，例如：

```bash
~/video-template-1
```

进入目录装依赖（**不要**提交 `node_modules`，它已被排除在分发包外）：

```bash
cd ~/video-template-1
npm install
```

> 如果拿到的是未预处理的"原版"，请让何公子按技能 SKILL.md 附录用 `prepare-student-template.py` 生成干净版（放开音色锁、Whisper 路径参数化、片尾改占位名）。

---

## 第二步：设置环境变量

在终端（或 WorkBuddy 的环境配置）里设好：

```bash
export REMOTION_TEMPLATE_DIR="$HOME/video-template-1"
export WHISPER_MODEL_PATH="$HOME/models/ggml-small.bin"   # 打轴必填，没有会直接失败
```

- `REMOTION_TEMPLATE_DIR`：你的模板目录，**必填**。
- `WHISPER_MODEL_PATH`：Whisper 模型文件绝对路径，**必填**（打轴强依赖，无可用兜底）。从 [whisper.cpp](https://github.com/ggerganov/whisper.cpp) 下载 `whisper-cli` 与一个中文 `ggml-small.bin` 放到本地，指向它。

---

## 第三步：换成你自己的配音与片尾（必做）

1. 打开模板根目录 `audio-pipeline.json`，把 `profile_id` / `profile_name` 改成你 Voicebox 里的档案；`outro_voice.text` 改成你的片尾口播（如 `我是小明，关注我，学习更多 AI 知识。`）。**`locked` 必须保持 `true`**（这是"我已试听通过"的开关，填 false 反而拒绝生成）。
   - 字段说明见 `references/student-audio-pipeline.example.json`。
2. 生成你的片尾人声（一次即可）：
   ```bash
   echo "我是小明，关注我，学习更多 AI 知识。" > outro.txt
   python3 scripts/voicebox_generate.py --text-file outro.txt --output public/generated/outro-voice.wav
   ```
3. 把你的正方形人像覆盖到 `public/outro/avatar.png`（当前是中性占位灰图）。
4. 打开 `src/template/scenes/LockedOutro.tsx`，把 `我是【你的名字】` 与 `// CREATOR` 水印改成你的名字。

> 注意：`script.md` 的「正式口播」末尾必须和 `audio-pipeline.json` 的 `outro_voice.text` **完全一致**，否则构建会报"正式口播必须以 outro_voice.text 结尾"。

---

## 第四步：装技能 + 跑通示例

1. 在 WorkBuddy 装入 `hegongzi` 技能。
2. 对话里说：

   > 用视频模板做个关于「用 AI 写周报」的竖屏短视频。

3. 技能会自动：写 `script.md` → 写 `content-outline.json` → `build_video.py` 选版+配音+打轴+算时长 → `make:render`（含 `check:sync`）→ 渲染。
4. 成片在 `out/student-video.mp4`。用 `ffprobe` 确认 `1080×1440 / 30fps`。

---

## 常见问题

**Q：配音报错 "Voicebox新克隆尚未通过试听"？**
A：`audio-pipeline.json` 的 `locked` 必须为 `true`（表示你已试听通过、可放心使用）。

**Q：打轴步骤报错找不到模型？**
A：确认 `WHISPER_MODEL_PATH` 指向真实存在的 `ggml-small.bin`，且本机已装 `whisper-cli`。

**Q：构建报 "正式口播必须以 outro_voice.text 结尾"？**
A：`script.md` 末尾没和 `audio-pipeline.json` 的 `outro_voice.text` 对齐，改一致即可。

**Q：check:sync 失败？**
A：说明字幕/画面/旁白没同源。不要手改时长，回到 `script.md` 修正口播后重跑 `build_video.py`。

**Q：片尾还是别人名字/头像？**
A：改 `LockedOutro.tsx` 文案 + 换 `public/outro/avatar.png`；音频则重新生成 `public/generated/outro-voice.wav`。

**Q：没有 Voicebox / 想用别的 TTS？**
A：本模板只支持本机 Voicebox（`voicebox_local`），云端/系统 TTS 不被接受。必须先装 Voicebox.app 并克隆自己的声音（恰好 1 条样本）。
