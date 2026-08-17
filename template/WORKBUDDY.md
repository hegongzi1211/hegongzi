# WorkBuddy 快速使用入口（学员版）

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
