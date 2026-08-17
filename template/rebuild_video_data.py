import json, os

BASE = '/WorkBuddy/2026-07-09-11-00-55/hgz-sp-moban-remotion'
OCR = '/WorkBuddy/workbuddy视频制作/ocr_raw'

SKILLS = ['Agent-Reach','Horizon','MediaCrawler','huashu-design','Auto-Redbook-Skills',
          'Generative-Media-Skills','nuwa-skill','guizang-social-card-skill','social-auto-upload','MediaCrawler']
BLOCKS = ['我觉得最有用的点', '像什么', '主要用途', '推荐搭配', '注意事项', '我的结论']
COLORS = {'我觉得最有用的点':'#39FF14','像什么':'#00FFFF','主要用途':'#FF1493',
          '推荐搭配':'#FFA500','注意事项':'#FF69B4','我的结论':'#FFFF00'}
SKILL_COLORS = ['#FFA500','#00FFFF','#39FF14','#FF1493','#FFFF00','#8B5CF6','#FF69B4','#00FF7F','#FF4500','#1E90FF']

def parse_skill(idx):
    txt = open(f'{OCR}/IMG_{79+idx:04d}.txt', encoding='utf-8').read()
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    desc = lines[2] if len(lines) > 2 else ''
    positions = [(b, txt.find(b)) for b in BLOCKS if txt.find(b) >= 0]
    positions.sort(key=lambda x: x[1])
    details = []
    for i, (b, pos) in enumerate(positions):
        start = pos + len(b)
        end = positions[i+1][1] if i+1 < len(positions) else len(txt)
        val = txt[start:end].strip().strip('。').strip()
        details.append({'text': b, 'color': COLORS[b], 'label': '说明', 'value': val})
    return desc, details

caps = json.load(open(f'{BASE}/generated/captions.json'))

# ---- 比例切分：用 ocr_raw 真实文本长度分配 855s(25650帧) ----
hook_text = ("Codex 做自媒体，必装十大 Skill。真正拉开差距的不是装多少工具，"
             "而是把它们串成一条生产线。接下来用十个 Skill，跑通选题、创作、发布和复盘。")
workflow_text = ("完整流程只有六步：找选题、听用户、写初稿、做视觉、多媒体延展、发布后收反馈。"
                 "工具负责把重复环节跑顺；选题判断和账号视角，还是你自己做主。")
skill_texts = []
for i in range(10):
    _, details = parse_skill(i)
    skill_texts.append(' '.join(d['value'] for d in details))

audio_sections = [hook_text, workflow_text] + skill_texts
lengths = [len(t) for t in audio_sections]
total_len = sum(lengths)
TOTAL_AUDIO_FRAMES = 25650  # 855s * 30fps
frames = [round(l / total_len * TOTAL_AUDIO_FRAMES) for l in lengths]
print('各 audio section 帧数:', frames, 'sum=', sum(frames))

# ---- 构造 scenes ----
vd = json.load(open(f'{BASE}/video-data.json'))
intro_tpl = vd['scenes'][0]
hook_tpl = vd['scenes'][1]
wf_tpl = next(s for s in vd['scenes'] if s['type'] == 'workflow')
outro_tpl = vd['scenes'][-1]

scenes = []
intro = dict(intro_tpl); intro['durationFrames'] = 45; scenes.append(intro)

hook = dict(hook_tpl)
hook['durationFrames'] = frames[0]
hook['narration'] = hook_text
hook['title'] = '不是多装工具，而是串成生产线'
hook['subtitle'] = '十个 Skill，跑通选题到复盘'
scenes.append(hook)

wf = dict(wf_tpl)
wf['durationFrames'] = frames[1]
wf['narration'] = workflow_text
scenes.append(wf)

for i in range(10):
    desc, details = parse_skill(i)
    sd = {
        'type': 'skill_detail',
        'durationFrames': frames[2+i],
        'showSubtitle': True,
        'narration': skill_texts[i],
        'supportText': details[-1]['value'] if details else '',
        'skillNum': f'{i+1:02d}',
        'skillName': SKILLS[i],
        'desc': desc,
        'mainColor': SKILL_COLORS[i],
        'details': details
    }
    scenes.append(sd)

outro = dict(outro_tpl); outro['durationFrames'] = 105; scenes.append(outro)

sum_audio = sum(s['durationFrames'] for s in scenes[1:-1])
audio = {
    'voiceover': {'src': 'generated/narration.wav', 'volume': 1, 'startFrame': 45},
    'outro': {'src': 'generated/outro-voice.wav', 'volume': 1, 'startFrame': 45 + sum_audio}
}
total = 45 + sum_audio + 105
new_vd = {
    'title': vd.get('title', 'Codex 十大 Skill'),
    'scenes': scenes,
    'audio': audio,
    'captions': caps,
    'metadata': {'durationInFrames': total}
}
json.dump(new_vd, open(f'{BASE}/video-data.json', 'w'), ensure_ascii=False, indent=2)
print('总帧', total, 'sum_audio', sum_audio)
print('各 scene 帧数:', [s['durationFrames'] for s in scenes])
print('10 Skill 帧数:', [s['durationFrames'] for s in scenes[3:13]])
