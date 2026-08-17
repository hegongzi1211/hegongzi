# 可复用 Remotion 视频模板

参考 `终稿.MP4` 复刻的 1080×1440、30fps 霓虹科技风模板。片尾组件位于
`src/template/scenes/LockedOutro.tsx`，已作为固定片尾保留。

## 一键生产流程

以后先把新内容整理进根目录 `content-outline.json`（格式参考
`content-outline.example.json`），再运行 `npm run apply:layouts`。系统会把内容关系转换成
Remotion 真正读取的 `layout-scenes.json`；`video-data.json` 保存字幕与音轨等解析结果。

## 可复用版式组件库

正文不再统一套用一种卡片页，目前支持：

- `overview:bento`：首次出现的同级概念总览
- `overview:index`：第二次出现的长名称或解释型总览
- `overview:spotlight`：第三次出现的主观点加补充信息
- `compare`：两类方案、前后变化、左右对比
- `process`：步骤、时间轴、验证闭环
- `case`：问题、做法、结果
- `triangle`：三个互相关联的因素
- `workflow`：完整工作流总结
- `skill_detail`：单个工具或技能详情（兼容旧数据）

选择原则是“统一视觉，不统一排版”。画布、配色、字号层级、字幕安全区、
固定音色和片尾保持一致，正文组件根据内容关系变化。同一种版式默认不连续
使用超过两页。

新内容先整理成通用段落数组。只查看选版报告可运行：

```console
npm run plan:layouts -- outline.json --output planned-outline.json
```

选版结果会写明页面任务、版式、视觉轮廓、信息密度和动画方式。超出组件容量的
内容会自动拆页；连续三页相同视觉轮廓会被构建校验拒绝。

把选版结果真正写入视频场景：

```console
npm run apply:layouts
```

```console
npm run make
```

该命令会：

1. 校验 `layout-scenes.json` 的版式字段和连续重复情况。
2. 读取 `audio-pipeline.json`，使用本机Voicebox和Qwen3-TTS 0.6B一次连续生成完整旁白。
   当前锁定正文档案为 `【你的名字】终稿原声-Remotion专用`（`你的Voicebox档案ID`），直接取样自 `终稿-音频.wav`，通过转写自动定位并清除异常前缀。
3. 对最终旁白做清晰度、响度和 48kHz 后处理。
4. 使用本机 Whisper 对最终音频打轴，生成 `generated/captions.json`。
5. 按实际旁白时间重算所有正文场景时长。
   总时长不固定：封面 1.5 秒，正文跟随实际旁白，旁白结束后保留 0.5 秒停顿，再进入 3.5 秒锁定片尾。
6. 英文产品名、版本号和连续英文词组保持为完整字幕单元，不从单词中间拆开。
7. 写回 `layout-scenes.json`、`video-data.json` 和 `generated/layout-audit.json` 选版报告；不添加转场音效。

生成并直接渲染：

```console
npm run make:render
```

本模板的正式旁白只读取 `audio-pipeline.json` 中锁定的本机 Voicebox 档案。

## 锁定片尾

片尾是 `src/template/scenes/LockedOutro.tsx` 内的原生Remotion场景，与正文共用
`CyberStage` 背景和转场，不拼接外部MP4。除非明确要更换片尾，不要改动其内容结构。

## 预览与渲染

```console
npm install
npm run dev
npx remotion render VideoTemplate out/video.mp4
```

## 校验

```console
npm run lint
npx remotion still VideoTemplate --frame=300 --scale=0.25 out/check.png
```

---

<p align="center">
  <a href="https://github.com/remotion-dev/logo">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-dark.apng">
      <img alt="Animated Remotion Logo" src="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-light.gif">
    </picture>
  </a>
</p>

Welcome to your Remotion project!

## Commands

**Install Dependencies**

```console
npm i
```

**Start Preview**

```console
npm run dev
```

**Render video**

```console
npx remotion render
```

**Upgrade Remotion**

```console
npx remotion upgrade
```

## Docs

Get started with Remotion by reading the [fundamentals page](https://www.remotion.dev/docs/the-fundamentals).

## Help

We provide help on our [Discord server](https://discord.gg/6VzzNDwUwV).

## Issues

Found an issue with Remotion? [File an issue here](https://github.com/remotion-dev/remotion/issues/new).

## License

Note that for some entities a company license is needed. [Read the terms here](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md).
