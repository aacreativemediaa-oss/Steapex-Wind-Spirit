"""Generate index.html for VO edit #3 (video4, travel take). Same style/format as video2/video3.

Run from video4/:  python3 tools/build.py
VO (assets/audio/vo.wav) is the original track: 100% volume, starts at 0, no cuts.
Captions are timed from transcript.json (word timings of that VO).
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 60
FOOTAGE_VOL = 0.30   # original footage sound at 30%
# per-clip overrides: b03 has people talking (would clash with the VO) -> muted; smoke spray hiss -> 8%
CLIP_VOL = {"b03": 0.0, "b09": 0.08}
CLIP_ORIGIN = {"b01": "50% 70%", "b08": "50% 70%"}   # zoom anchor kept low so shoes stay in frame
SFX_VOL = 0.30
VO_FILE = "assets/audio/vo.wav"
VO_LEN = 35.502

# ---- Edit decision list (10 clips) ---------------------------------------------------------------
CLIPS = [
    ("b01", "b01_tired.mp4", 0.00, 3.70, "B ROLL video_20251226_091215 0.6-4.3 runner bent over, other-brand shoes (intro, one shot, natural speed)"),
    ("b02", "b02_jog.mp4", 3.70, 3.90, "lv_0_20251221233711 54.45-58.35 jogging on the spot, teal"),
    ("b03", "b03_toe.mp4", 7.60, 3.60, "B ROLL video_20250529_093604 0.5-4.1 bruised toenail close-up (muted: speech)"),
    ("b04", "b04_foamblk.mp4", 11.20, 3.50, "lv_0_20251220180407 56.65-60.15 squeezing midsole foam, black"),
    ("b05", "b05_run.mp4", 14.70, 2.60, "video_20260429_114602 4.0-6.6 jogging on track, teal"),
    ("b06", "b06_flex.mp4", 17.30, 2.30, "lv_0_20251221130556 40.5-42.8 sole flex, teal"),
    ("b07", "b07_jump.mp4", 19.60, 3.40, "video_20260429_114829 40.5-43.9 hopping by the grass edge, teal"),
    ("b08", "b08_step.mp4", 23.00, 4.20, "lv_0_20251209143405 43.2-47.4 stepping, white/purple"),
    ("b09", "b09_smoke.mp4", 27.20, 3.35, "lv_0_20251221130556 77.55-80.9 smoke through mesh, teal"),
    ("b10", "b10_cta.mp4", 30.55, 4.97, "lv_0_20251221233711 67.43-72.4 pair on mat (CTA)"),
]
TOTAL = round(CLIPS[-1][2] + CLIPS[-1][3], 3)
CUTS = [c[2] for c in CLIPS[1:]]

# ---- Captions (phrase, hidden, keywords) -----------------------------------------------------------
CHUNKS = [
    ("Nak kasut selesa", True, ""), ("untuk pergi travel,", True, ""),
    ("korang jangan pakai", True, ""), ("kasut yang tapak", True, ""), ("dia keras tau.", True, ""),
    ("Sebab bila", False, ""), ("pergi travel,", False, "TRAVEL"),
    ("purata korang berjalan", True, ""), ("10,000 step sehari kan.", True, ""),
    ("Kalau salah", False, "SALAH"), ("pakai kasut,", False, ""), ("tumit cepat sakit", False, "SAKIT"), ("macam ni tau.", False, ""),
    ("Memang pedih gila.", False, "PEDIH"),
    ("Sebab tu korang", False, ""), ("kena pilih", False, "PILIH"),
    ("kasut yang ada", True, ""), ("foam tebal dan", True, ""), ("serap hentakan macam ni.", True, ""),
    ("Nak berjalan", False, ""), ("lama pun, tak", False, "TAK"), ("pedih tumit korang", False, "PEDIH"), ("nanti tau.", False, ""),
    ("Kasut ni pun", True, ""), ("dia datang dengan", True, ""), ("plate flexible sekali.", True, ""),
    ("So langkah korang", False, ""), ("jadi lebih stabil,", False, "STABIL"),
    ("especially bila", False, ""), ("pijak permukaan", False, ""), ("yang tak rata.", False, "TAK RATA"),
    ("Dan yang paling", False, ""), ("best kan,", False, "BEST"),
    ("korang berjalan", False, ""), ("daripada pagi", False, "PAGI"), ("sampai ke malam", False, "MALAM"),
    ("pun, memang", False, ""), ("selesa sangat", False, "SELESA"),
    ("sebab kain dia", True, ""), ("jenis breathable tau.", True, ""),
    ("Langsung tak", False, ""), ("rasa berkuap.", False, "BERKUAP"),
    ("Harga pun tengah", True, ""), ("murah sekarang.", True, ""),
    ("So sebelum", False, ""), ("korang terlepas,", False, "TERLEPAS"),
    ("korang pilih warna", True, ""), ("dan saiz kat beg", True, ""), ("kuning bawah ni.", True, ""),
]

# ---- SFX cues -------------------------------------------------------------------------------------
SFX_LEN = {"whoosh": 0.45, "pop": 0.12, "ding": 1.0, "impact": 0.9, "cha_ching": 1.1, "riser": 1.5, "zap": 0.25}
SFX = [
    (0.02, "impact", 0.9), (0.30, "whoosh", 0.7), (1.75, "zap", 0.7),
    (3.65, "whoosh", 0.7), (5.00, "pop", 0.6), (7.05, "ding", 0.6),
    (7.55, "whoosh", 0.7), (10.55, "pop", 0.7),
    (11.15, "zap", 0.6), (11.40, "ding", 0.6),
    (14.65, "whoosh", 0.7),
    (17.25, "zap", 0.6), (17.45, "ding", 0.6), (19.55, "whoosh", 0.7),
    (22.95, "whoosh", 0.7), (25.20, "pop", 0.7), (25.80, "pop", 0.7),
    (27.15, "zap", 0.6), (27.55, "ding", 0.6),
    (29.05, "riser", 0.6), (30.52, "impact", 0.8), (31.20, "cha_ching", 0.8),
    (33.30, "pop", 0.6), (33.42, "pop", 0.7), (33.52, "pop", 0.7), (33.62, "pop", 0.7), (33.90, "pop", 0.7), (34.50, "zap", 0.5),
]

S = 0.70  # graphics at 70% of first-pass size; caption fixed at 60px
def px(v): return f"{round(v * S)}px"
def norm(t): return re.sub(r"[^\w-]", "", t.upper())


def caption_chunks():
    words = json.loads((ROOT / "transcript.json").read_text())["words"]
    i, out = 0, []
    for phrase, hidden, kws in CHUNKS:
        target, toks, acc = phrase.split(), [], []
        while len(" ".join(acc).split()) < len(target):
            acc.append(words[i]["text"]); toks.append(words[i]); i += 1
        assert norm(" ".join(acc)) == norm(phrase), (phrase, acc)
        out.append((toks, hidden, set(kws.split())))
    assert i == len(words), "every VO word must be covered by a caption chunk"
    res = []
    for k, (toks, hidden, kws) in enumerate(out):
        a = toks[0]["start"]
        nxt = out[k + 1][0][0]["start"] if k + 1 < len(out) else TOTAL
        nxt_hidden = k + 1 < len(out) and out[k + 1][1]
        b = toks[-1]["end"] + 0.35 if nxt_hidden else min(nxt, toks[-1]["end"] + 0.3)
        res.append((round(a, 3), round(b, 3), toks, hidden, kws))
    return res


def captions():
    html, js = [], []
    for i, (a, b, toks, hidden, kws) in enumerate(caption_chunks()):
        if hidden:
            continue
        spans = []
        for j, w in enumerate(toks):
            parts = w["text"].upper().rstrip(".,?!").split()
            is_kw = any(p in kws for p in parts)
            spans.append(f'<span class="w{" kw" if is_kw else ""}" id="c{i}w{j}">{" ".join(parts)}</span>')
            sel, t0, t1 = f"#c{i}w{j}", w["start"], w["end"]
            if is_kw:
                js.append(f'tl.fromTo("{sel}",{{scale:1}},{{scale:1.14,duration:0.08}},{t0});'
                          f'tl.to("{sel}",{{scale:1,duration:0.1}},{round(max(t1, t0 + 0.1), 3)});')
            else:
                js.append(f'tl.set("{sel}",{{color:"var(--yellow)"}},{t0});tl.set("{sel}",{{color:"#fff"}},{round(max(t1, t0 + 0.08), 3)});')
        html.append(f'<div class="clip cap" id="c{i}" data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="20">'
                    f'<div class="capline">{"".join(spans)}</div></div>')
        js.append(f'tl.fromTo("#c{i} .capline",{{scale:0.82,y:18}},{{scale:1,y:0,duration:0.14,ease:"back.out(3)"}},{a});')
    return "\n      ".join(html), "\n      ".join(js)


def build():
    def video(i, cid, f, s, d):
        vol = CLIP_VOL.get(cid, FOOTAGE_VOL)
        audio = 'muted' if vol == 0 else f'data-volume="{vol}" data-has-audio="true"'
        org = f' style="transform-origin:{CLIP_ORIGIN[cid]}"' if cid in CLIP_ORIGIN else ""
        return (f'<video id="{cid}" class="clip shot"{org} src="assets/clips/{f}" data-start="{s}" data-duration="{d}" '
                f'data-media-start="0" {audio} data-track-index="{i}" playsinline></video>')
    videos = "\n      ".join(video(i, *c[:4]) for i, c in enumerate(CLIPS))
    flashes = "\n      ".join(f'<div class="clip flash" id="fl{i}" data-start="{t}" data-duration="0.3" data-track-index="30"></div>'
                               for i, t in enumerate(CUTS))
    sfx = "\n      ".join(f'<audio id="sfx{i}" src="assets/sfx/{n}.wav" data-start="{t}" data-duration="{SFX_LEN[n]}" '
                           f'data-volume="{round(SFX_VOL * g, 3)}"></audio>' for i, (t, n, g) in enumerate(SFX))
    zoom = "\n      ".join(
        f'tl.fromTo("#{cid}",{{scale:1.0}},{{scale:1.07,duration:0.45,ease:"power2.out"}},{s});'
        f'tl.to("#{cid}",{{scale:1.11,duration:{round(d - 0.45, 3)},ease:"none"}},{round(s + 0.45, 3)});'
        for cid, f, s, d, _ in CLIPS)
    flash_js = "\n      ".join(f'tl.fromTo("#fl{i}",{{opacity:0.9}},{{opacity:0,duration:0.22,ease:"power1.out"}},{t});'
                                for i, t in enumerate(CUTS))
    cap_html, cap_js = captions()
    html = TEMPLATE
    for k, v in {"__TOTAL__": str(TOTAL), "__FPS__": str(FPS), "__VIDEOS__": videos, "__FLASHES__": flashes,
                 "__SFX__": sfx, "__CAPTIONS__": cap_html, "__ZOOM_JS__": zoom, "__FLASH_JS__": flash_js,
                 "__CAPTION_JS__": cap_js, "__VO__": VO_FILE, "__VOLEN__": str(VO_LEN), "__BAG__": BAG}.items():
        html = html.replace(k, v)
    html = re.sub(r"\{\{(\d+(?:\.\d+)?)\}\}", lambda m: px(float(m.group(1))), html)
    (ROOT / "index.html").write_text(html)
    (ROOT / "edit-decision-list.json").write_text(json.dumps({
        "fps": FPS, "duration": TOTAL, "voiceover": {"file": VO_FILE, "start": 0, "volume": 1.0, "length": VO_LEN},
        "footage_volume": FOOTAGE_VOL, "sfx_volume": SFX_VOL,
        "clips": [dict(id=c[0], file=c[1], start=c[2], duration=c[3], volume=CLIP_VOL.get(c[0], FOOTAGE_VOL), source=c[4]) for c in CLIPS],
        "captions": [dict(start=a, end=b, text=" ".join(w["text"] for w in t), hidden=h) for a, b, t, h, k in caption_chunks()],
        "sfx": [dict(time=t, name=n, gain=g) for t, n, g in SFX],
    }, indent=2, ensure_ascii=False))
    print("wrote index.html, duration", TOTAL)


BAG = ('<svg class="bagsvg" viewBox="0 0 100 100"><path d="M32 34 V26 a18 18 0 0 1 36 0 V34" fill="none" stroke="#000" stroke-width="9" stroke-linecap="round"/>'
       '<path d="M14 32 H86 L80 92 H20 Z" fill="#ffe100" stroke="#000" stroke-width="6" stroke-linejoin="round"/>'
       '<path d="M38 52 a12 12 0 0 0 24 0" fill="none" stroke="#000" stroke-width="6" stroke-linecap="round"/></svg>')

TEMPLATE = r"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Anton"; src: url("assets/fonts/Anton-latin.woff2") format("woff2"); font-weight: 400; font-display: block; }
      @font-face { font-family: "Montserrat"; src: url("assets/fonts/Montserrat-latin.woff2") format("woff2"); font-weight: 100 900; font-display: block; }
      :root { --ground: #000; --ink: #fff; --yellow: #ffe100; --neon: #39ff14; --teal: #19d6c6; --red: #ff2d3d;
              --font-display: "Anton", sans-serif; --font-label: "Montserrat", sans-serif; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }
      .clip { position: absolute; inset: 0; width: 1080px; height: 1920px; }
      video.shot { object-fit: cover; transform-origin: 50% 50%; }
      .flash { background: #fff; opacity: 0; }
      .display { font-family: var(--font-display); text-transform: uppercase; line-height: 0.95; color: #fff;
                 -webkit-text-stroke: {{12}} #000; paint-order: stroke fill; }
      .label { font-family: var(--font-label); font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
      .shade-top { position: absolute; left: 0; right: 0; top: 0; height: 900px;
                   background: linear-gradient(180deg, rgba(0,0,0,.72) 0%, rgba(0,0,0,.35) 55%, rgba(0,0,0,0) 100%); }
      .shade-bot { position: absolute; left: 0; right: 0; bottom: 0; height: 760px;
                   background: linear-gradient(0deg, rgba(0,0,0,.6) 0%, rgba(0,0,0,0) 100%); }

      /* HOOK */
      #hook .chip { position: absolute; top: 300px; left: 120px; right: 120px; text-align: center; }
      #hook .chip span { display: inline-block; background: #000; color: var(--yellow); padding: 10px 24px; border-radius: 999px;
                         font-size: {{40}}; border: 3px solid var(--yellow); }
      #hook .h { position: absolute; top: 372px; left: 120px; right: 120px; text-align: center; font-size: {{130}}; }
      #hook .h .y { color: var(--yellow); }
      #hook .h .r { color: var(--red); }
      #hook .xmark { position: absolute; left: 330px; top: 1440px; width: 400px; height: 400px; }
      #hook .xmark svg { width: 100%; height: 100%; filter: drop-shadow(0 0 6px rgba(0,0,0,.7)); }

      /* STEP COUNTER */
      #steps .card { position: absolute; left: 120px; width: 660px; top: 340px; background: rgba(0,0,0,.75);
                     border: 4px solid var(--neon); border-radius: 26px; padding: 20px 32px; }
      #steps .lbl { color: #fff; font-size: {{42}}; }
      #steps .val { font-family: var(--font-display); color: var(--neon); font-size: {{170}}; line-height: 1; margin-top: 6px; }
      #steps .val small { font-size: {{70}}; color: #fff; margin-left: 10px; }
      #steps .bar { height: 22px; background: rgba(255,255,255,.18); border-radius: 12px; overflow: hidden; margin-top: 12px; }
      #steps .bar i { display: block; height: 100%; width: 100%; background: linear-gradient(90deg, var(--teal), var(--neon));
                      transform-origin: 0 50%; transform: scaleX(0); }

      /* PAIN overlay */
      #pain .vig { position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(255,0,0,0) 45%, rgba(255,20,40,.55) 100%); opacity: 0; }
      #pain .ring { position: absolute; left: 720px; top: 470px; width: 260px; height: 260px; border-radius: 50%;
                    border: 10px solid var(--red); opacity: 0; box-shadow: 0 0 20px rgba(255,45,61,.7); }
      #pain .warn { position: absolute; left: 140px; top: 330px; width: 150px; height: 150px; opacity: 0; }

      /* FEATURE TITLE */
      .feat .box { position: absolute; top: 330px; left: 120px; right: 120px; }
      .feat .chip { display: inline-flex; align-items: center; gap: 14px; background: var(--neon); color: #000;
                    padding: 12px 24px; border-radius: 14px; font-size: {{40}}; border: 4px solid #000; }
      .feat .chip b { background: #000; color: var(--neon); border-radius: 8px; padding: 2px 12px; }
      .feat .title { font-size: {{140}}; margin-top: 22px; overflow: hidden; padding-bottom: 8px; }
      .feat .title > span { display: inline-block; }
      .feat .sub { font-size: {{72}}; color: var(--yellow); margin-top: 6px; }
      .feat .dots { position: absolute; top: 300px; left: 120px; display: flex; gap: 12px; }
      .feat .dots i { width: 70px; height: 10px; border-radius: 6px; background: rgba(255,255,255,.35); display: block; }
      .feat .dots i.on { background: var(--neon); }

      /* SUN -> MOON */
      #day .arc { position: absolute; left: 120px; top: 330px; width: 660px; height: 300px; }
      #day .sun, #day .moon { position: absolute; width: 120px; height: 120px; border-radius: 50%; }
      #day .sun { left: 120px; top: 500px; background: radial-gradient(circle, #ffe100 55%, #ff9f1a 100%); box-shadow: 0 0 40px #ffb000; opacity: 0; }
      #day .moon { left: 660px; top: 500px; background: #f2f2ff; box-shadow: inset -28px 0 0 0 #c7c7e6, 0 0 30px #9aa0ff; opacity: 0; }
      #day .track { position: absolute; left: 180px; top: 440px; width: 540px; height: 200px; border: 6px dashed rgba(255,255,255,.75);
                    border-bottom: none; border-radius: 300px 300px 0 0; opacity: 0; }

      /* HEAT arrows */
      #heat .a { position: absolute; width: 70px; height: 70px; border-left: 14px solid #ff7a1a; border-top: 14px solid #ff7a1a;
                 transform: rotate(45deg); filter: drop-shadow(0 0 4px #000); opacity: 0; }

      /* CTA */
      #buy .box { position: absolute; top: 330px; left: 120px; right: 120px; text-align: center; }
      #buy .h1 { font-size: {{120}}; }
      #buy .stamp { display: inline-block; margin-top: 14px; background: var(--yellow); color: #000; -webkit-text-stroke: 0;
                    font-size: {{200}}; line-height: 1.05; padding: 8px 44px 4px; border: 8px solid #000; border-radius: 22px;
                    box-shadow: 10px 10px 0 #000; transform-origin: 50% 50%; }
      #buy .card { position: absolute; left: 120px; width: 660px; top: 640px; background: rgba(0,0,0,.8);
                   border: 5px solid var(--neon); border-radius: 28px; padding: 22px 30px; text-align: center; }
      #buy .pick { font-size: {{96}}; color: var(--neon); }
      #buy .sw { display: flex; justify-content: center; align-items: flex-start; gap: 14px; margin: 14px 0 12px; }
      #buy .sw .tile { width: 188px; display: flex; flex-direction: column; align-items: center; gap: 6px; transform-origin: 50% 60%; }
      #buy .sw img { width: 188px; height: 235px; object-fit: cover; border-radius: 16px; border: 4px solid #fff; display: block; }
      #buy .sw .nm { font-size: {{40}}; color: #fff; text-align: center; line-height: 1.1; letter-spacing: 0.04em; }
      #buy .line { font-family: var(--font-label); font-weight: 800; color: #fff; font-size: {{46}}; line-height: 1.3;
                   display: flex; align-items: center; justify-content: center; gap: 12px; flex-wrap: wrap; }
      #buy .line .bagsvg { width: 54px; height: 54px; }
      #buy .line em { font-style: normal; color: var(--yellow); }
      #buy .bigbag { position: absolute; left: 130px; top: 1150px; width: 150px; height: 150px; }
      #buy .bigbag .bagsvg { width: 150px; height: 150px; filter: drop-shadow(0 6px 10px rgba(0,0,0,.5)); }
      #buy .arrows { position: absolute; left: 165px; top: 1305px; display: flex; flex-direction: column; align-items: center; }
      #buy .arrows i { width: 56px; height: 56px; border-right: 14px solid var(--yellow); border-bottom: 14px solid var(--yellow);
                       transform: rotate(45deg); margin-top: -20px; display: block; filter: drop-shadow(0 0 3px #000); }

      /* CAPTIONS: Anton 60px, uppercase, black stroke, centre-bottom */
      .cap .capline { position: absolute; left: 120px; width: 840px; top: 1140px; display: flex; justify-content: center;
                      flex-wrap: wrap; gap: 0 16px; transform-origin: 50% 50%; }
      .cap .w { font-family: var(--font-display); font-size: 60px; line-height: 1.1; text-transform: uppercase; color: #fff;
                -webkit-text-stroke: 10px #000; paint-order: stroke fill; display: inline-block; letter-spacing: 0.02em;
                text-shadow: 0 4px 10px rgba(0,0,0,.5); }
      .cap .w.kw { color: var(--neon); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="__TOTAL__" data-fps="__FPS__" data-width="1080" data-height="1920">
      <!-- FOOTAGE (10 clips) -->
      __VIDEOS__

      <!-- VOICEOVER: original, 100%, uncut -->
      <audio id="vo" src="__VO__" data-start="0" data-duration="__VOLEN__" data-media-start="0" data-volume="1"></audio>

      <!-- HOOK 0-3.7 -->
      <div class="clip" id="hook" data-start="0" data-duration="3.7" data-track-index="11">
        <div class="shade-top"></div>
        <div class="chip"><span class="label" id="hchip">Nak kasut selesa untuk travel?</span></div>
        <div class="display h" id="hh"><span id="hh1">Jangan pakai</span><br /><span class="y" id="hh2">kasut tapak</span> <span class="r" id="hh3">keras!</span></div>
        <div class="xmark" id="hx"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="44" fill="rgba(255,45,61,.18)" stroke="#ff2d3d" stroke-width="7"/>
          <path d="M30 30 L70 70 M70 30 L30 70" stroke="#ff2d3d" stroke-width="10" stroke-linecap="round"/></svg></div>
      </div>

      <!-- STEP COUNTER 3.7-7.6 -->
      <div class="clip" id="steps" data-start="3.7" data-duration="3.9" data-track-index="12">
        <div class="shade-top"></div>
        <div class="card" id="scard">
          <div class="lbl label">Purata travel / sehari</div>
          <div class="val"><span id="sval">0</span><small>step</small></div>
          <div class="bar"><i id="sbar"></i></div>
        </div>
      </div>

      <!-- PAIN 7.6-11.2 -->
      <div class="clip" id="pain" data-start="7.6" data-duration="3.6" data-track-index="12">
        <div class="vig" id="pvig"></div>
        <div class="ring" id="pring"></div>
        <svg class="warn" id="pwarn" viewBox="0 0 100 100"><path d="M50 6 L96 90 H4 Z" fill="#ff2d3d" stroke="#000" stroke-width="6" stroke-linejoin="round"/>
          <rect x="45" y="34" width="10" height="30" rx="4" fill="#fff"/><circle cx="50" cy="75" r="6" fill="#fff"/></svg>
      </div>

      <!-- FEATURE 1: 11.2-17.3 -->
      <div class="clip feat" id="f1" data-start="11.2" data-duration="6.1" data-track-index="13">
        <div class="shade-top"></div>
        <div class="dots"><i class="on"></i><i></i><i></i></div>
        <div class="box">
          <div class="chip label" id="f1chip">Ciri <b>#1</b></div>
          <div class="display title"><span id="f1t">Foam tebal</span></div>
          <div class="display sub" id="f1s">+ Serap hentakan</div>
        </div>
      </div>

      <!-- FEATURE 2: 17.3-23.0 -->
      <div class="clip feat" id="f2" data-start="17.3" data-duration="5.7" data-track-index="13">
        <div class="shade-top"></div>
        <div class="dots"><i class="on"></i><i class="on"></i><i></i></div>
        <div class="box">
          <div class="chip label" id="f2chip">Ciri <b>#2</b></div>
          <div class="display title"><span id="f2t">Plate flexible</span></div>
        </div>
      </div>

      <!-- DAY ARC 23.0-27.2 -->
      <div class="clip" id="day" data-start="23" data-duration="4.2" data-track-index="13">
        <div class="shade-top"></div>
        <div class="track" id="dtrack"></div>
        <div class="sun" id="dsun"></div>
        <div class="moon" id="dmoon"></div>
      </div>

      <!-- FEATURE 3: 27.2-30.55 -->
      <div class="clip feat" id="f3" data-start="27.2" data-duration="3.35" data-track-index="13">
        <div class="shade-top"></div>
        <div class="dots"><i class="on"></i><i class="on"></i><i class="on"></i></div>
        <div class="box">
          <div class="chip label" id="f3chip">Ciri <b>#3</b></div>
          <div class="display title"><span id="f3t">Kain breathable</span></div>
        </div>
      </div>
      <div class="clip" id="heat" data-start="28.2" data-duration="2.3" data-track-index="14">
        <div class="a" id="ha1" style="left:700px;top:900px"></div>
        <div class="a" id="ha2" style="left:800px;top:960px"></div>
        <div class="a" id="ha3" style="left:900px;top:900px"></div>
      </div>

      <!-- CTA 30.55-end -->
      <div class="clip" id="buy" data-start="30.55" data-duration="4.97" data-track-index="15">
        <div class="shade-top"></div>
        <div class="shade-bot"></div>
        <div class="box">
          <div class="display h1" id="bh1">Harga tengah</div>
          <div class="display stamp" id="bstamp">Murah!</div>
        </div>
        <div class="card" id="bcard">
          <div class="display pick">Pilih warna &amp; saiz</div>
          <div class="sw" id="bsw">
            <div class="tile" id="sw1"><img src="assets/img/shoe_teal.jpg" alt="" /><div class="nm label">Emerald<br />Green</div></div>
            <div class="tile" id="sw2"><img src="assets/img/shoe_white.jpg" alt="" /><div class="nm label">Violet</div></div>
            <div class="tile" id="sw3"><img src="assets/img/shoe_black.jpg" alt="" /><div class="nm label">Black</div></div>
          </div>
          <div class="line">kat <em>beg kuning</em> __BAG__ bawah ni</div>
        </div>
        <div class="bigbag" id="bbag">__BAG__</div>
        <div class="arrows" id="barr"><i></i><i></i><i></i></div>
      </div>

      <!-- CAPTIONS -->
      __CAPTIONS__

      <!-- WHITE FLASH ON EVERY CUT -->
      __FLASHES__

      <!-- SFX (synthesised, low) -->
      __SFX__
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });

      __ZOOM_JS__
      __FLASH_JS__

      // HOOK
      tl.fromTo("#hchip", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3 }, 0.05);
      tl.fromTo("#hh1", { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "power4.in" }, 1.42);
      tl.fromTo("#hh2", { y: 50, opacity: 0 }, { y: 0, opacity: 1, duration: 0.25, ease: "power3.out" }, 2.2);
      tl.fromTo("#hh3", { scale: 2.2, rotation: -12, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.3, ease: "power4.in" }, 2.95);
      tl.fromTo("#hx", { scale: 0, rotation: -40, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.3, ease: "back.out(2.2)" }, 1.72);
      tl.to("#hx", { scale: 1.08, duration: 0.15, yoyo: true, repeat: 3, ease: "sine.inOut" }, 2.95);

      // STEP COUNTER
      tl.fromTo("#scard", { y: -60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "back.out(1.6)" }, 4.0);
      const st = { v: 0 };
      tl.fromTo(st, { v: 0 }, { v: 10000, duration: 2.0, ease: "power2.out",
        onUpdate: () => { document.getElementById("sval").textContent = String(Math.round(st.v)).replace(/\B(?=(\d{3})+(?!\d))/g, ","); } }, 5.0);
      tl.fromTo("#sbar", { scaleX: 0 }, { scaleX: 1, duration: 2.0, ease: "power2.out" }, 5.0);

      // PAIN
      gsap.set(["#pvig", "#pring", "#pwarn"], { opacity: 0 });
      [9.22, 10.59].forEach((t) => {
        tl.fromTo("#pvig", { opacity: 0 }, { opacity: 1, duration: 0.15, immediateRender: false }, t);
        tl.to("#pvig", { opacity: 0, duration: 0.5 }, t + 0.15);
      });
      tl.fromTo("#pring", { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)", immediateRender: false }, 10.55);
      tl.to("#pring", { scale: 1.1, duration: 0.15, yoyo: true, repeat: 1 }, 10.82);
      tl.fromTo("#pwarn", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)", immediateRender: false }, 8.95);

      // FEATURE TITLES
      [["f1", 11.2], ["f2", 17.3], ["f3", 27.2]].forEach(([id, t]) => {
        tl.fromTo(`#${id}chip`, { x: -260, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, t + 0.05);
        tl.fromTo(`#${id}t`, { yPercent: 105 }, { yPercent: 0, duration: 0.35, ease: "power3.out" }, t + 0.15);
        tl.fromTo(`#${id} .dots`, { opacity: 0 }, { opacity: 1, duration: 0.25 }, t);
      });
      tl.fromTo("#f1s", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 13.5);

      // DAY ARC (pagi -> malam)
      tl.fromTo("#dtrack", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 24.6);
      tl.fromTo("#dsun", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)" }, 25.2);
      tl.to("#dsun", { x: 270, y: -150, duration: 0.3, ease: "sine.out" }, 25.45);
      tl.to("#dsun", { x: 540, y: 0, opacity: 0, duration: 0.3, ease: "sine.in" }, 25.75);
      tl.fromTo("#dmoon", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)" }, 25.81);

      // HEAT rising
      ["#ha1", "#ha2", "#ha3"].forEach((s, i) => {
        for (let k = 0; k < 2; k++) {
          const t = 28.3 + i * 0.2 + k * 0.95;
          tl.fromTo(s, { y: 0, opacity: 0 }, { y: -260, opacity: 1, duration: 0.45, ease: "none", immediateRender: k === 0 }, t);
          tl.to(s, { y: -360, opacity: 0, duration: 0.3, ease: "none" }, t + 0.45);
        }
      });

      // CTA
      tl.fromTo("#bh1", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 30.64);
      tl.fromTo("#bstamp", { scale: 3, rotation: 0, opacity: 0 }, { scale: 1, rotation: -4, opacity: 1, duration: 0.3, ease: "power4.in" }, 31.1);
      tl.fromTo("#bcard", { y: 90, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 33.3);
      tl.fromTo("#bsw .tile", { scale: 0, rotation: -8 }, { scale: 1, rotation: 0, duration: 0.3, stagger: 0.1, ease: "back.out(2.6)" }, 33.38);
      [["#sw1", 34.55], ["#sw2", 34.85], ["#sw3", 35.15]].forEach(([s, t]) => {
        tl.to(s, { scale: 1.08, duration: 0.15, ease: "sine.out" }, t);
        tl.to(s, { scale: 1, duration: 0.15, ease: "sine.in" }, t + 0.15);
      });
      tl.fromTo("#bbag", { scale: 0, rotation: -20 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.4)" }, 33.85);
      for (let k = 0; k < 2; k++) {
        tl.to("#bbag", { y: -18, duration: 0.2, ease: "sine.out" }, 34.35 + k * 0.45);
        tl.to("#bbag", { y: 0, duration: 0.2, ease: "sine.in" }, 34.55 + k * 0.45);
      }
      gsap.set("#barr i", { opacity: 0 });
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 34.1);
      tl.to("#barr i", { opacity: 0.2, duration: 0.15, stagger: 0.1 }, 34.55);
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 35.0);

      // CAPTIONS (word timing from the VO; active word yellow, keywords neon green)
      __CAPTION_JS__

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    build()
