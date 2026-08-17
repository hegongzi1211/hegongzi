"""验证同步：startFrame=0 后，每屏画面时间段内的字幕应 == 该屏应讲内容（1:1，不再整段错位）。"""
import json

layout = json.load(open('layout-scenes.json'))
vd = json.load(open('video-data.json'))
caps = vd.get('captions', [])
caps.sort(key=lambda c: c.get('startMs', 0) or 0)

FPS = 30
starts = [0.0]
for s in layout:
    starts.append(starts[-1] + s.get('durationFrames', 0) / FPS)

sf = vd.get('audio', {}).get('voiceover', {}).get('startFrame', 0)
print('render startFrame =', sf)
print('total dur = %.2fs' % starts[-1])
print('=' * 72)
bad = 0
for i, s in enumerate(layout):
    if s.get('type') in {'intro', 'outro'}:
        continue
    a = max(0.0, starts[i] - sf / FPS)
    b = max(0.0, starts[i + 1] - sf / FPS)
    seg = [c.get('text', '') for c in caps if a <= (c.get('startMs', 0) / 1000) < b]
    narr = (s.get('narration', '') or '').replace('\n', ' ')
    segtxt = ' / '.join(seg)
    import re
    norm = lambda x: re.sub(r'[^A-Za-z0-9\u4e00-\u9fff]', '', x).lower()
    anchor = norm(narr)[:8]
    ok = (anchor in norm(segtxt)) if anchor else True
    if not ok:
        bad += 1
    flag = 'OK ' if ok else '?? '
    print(f'{flag}[{i:2d}] {s.get("type"):11s} [{a:6.2f}-{b:6.2f}s]')
    print('   应讲:', narr[:90])
    print('   实播:', segtxt[:180])
    print()
print('错位场景数(锚点不匹配):', bad, '/', len(layout))
