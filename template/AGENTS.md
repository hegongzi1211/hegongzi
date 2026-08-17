# 项目执行入口

在这个模板中工作时，先完整读取 `WORKBUDDY.md`，再读取其中列出的必要文件。

- 固定使用当前目录，不复制模板，不进入任何 backup 目录。
- 不扫描 `node_modules/`、`build/`、`out/` 和历史任务目录。
- 排版预览只渲染单帧，不重新生成 Voicebox 旁白。
- 旁白或字幕变化时才运行 `python3 scripts/build_video.py`。
- 最终确认后只执行一次 Remotion 完整渲染。
- 不添加转场音效或内容提示音。
- 不修改锁定片尾和已经批准的音色。
