from pathlib import Path


source = (Path(__file__).resolve().parent / "build_video.py").read_text(encoding="utf-8")
render_call = source[source.index('if args.render:'):]
assert '"--concurrency=10"' in render_call, "Final render must use the verified fast concurrency"
assert '"--overwrite"' in render_call, "Final render must not stop for an existing output"

print("render_command_policy=passed")
