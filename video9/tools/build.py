"""Generate index.html for "New VO" (video9). Updated format (../video/FORMAT.md):
headline 100px on ONE line (wraps only if it cannot fit), sub-headline 47px, caption 40px, small labels ~19px,
original footage framing kept (no close-up crops; brief zoom-in on each cut stays), ~70 MB render.

Run from video9/:  python3 tools/build.py
VO (assets/audio/vo.wav) is the original track: 100% volume, starts at 0, no cuts.
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 60
FOOTAGE_VOL = 0.30                     # original footage sound at 30%
CLIP_VOL = {"n08": 0.08}               # smoke spray hiss -> 8%
CLIP_ORIGIN = {"n07": "50% 70%"}
SFX_VOL = 0.30
VO_FILE = "assets/audio/vo.wav"
VO_LEN = 35.455
H1, H2, CAP = 85, 47, 40
S = 0.70 * 2 / 3                       # small labels ({{n}} tokens): ~19px for a 40 token

# ---- Edit decision list (10 clips) ---------------------------------------------------------------
CLIPS = [
    ("n01", "n01_ball.mp4", 0.00, 5.40, "lv_7535...181155 0-5.4 ball-drop split-screen, full frame over blurred fill (intro, one shot)"),
    ("n02", "n02_run.mp4", 5.40, 2.70, "video_20260429_114602 4.0-6.7 jogging on track, Emerald Green"),
    ("n03", "n03_hop.mp4", 8.10, 3.30, "lv_0_20251221233711 41.4-44.7 feet hopping, Emerald Green"),
    ("n04", "n04_jog.mp4", 11.40, 3.60, "lv_0_20251221233711 54.45-58.05 jogging on the spot, Emerald Green"),
    ("n05", "n05_tread.mp4", 15.00, 2.50, "video_20260117_220257 0.5-3.0 treadmill feet, Emerald Green"),
    ("n06", "n06_foam.mp4", 17.50, 3.70, "lv_0_20251220180407 56.6-60.3 squeezing midsole foam, Black"),
    ("n07", "n07_step.mp4", 21.20, 3.60, "lv_0_20251209143405 43.2-46.8 stepping, Violet"),
    ("n08", "n08_smoke.mp4", 24.80, 4.60, "lv_0_20251221130556 77.55-82.15 smoke through mesh, Emerald Green"),
    ("n09", "n09_black.mp4", 29.40, 2.80, "lv_0_20251220180407 94.05-96.85 Black shoe held (CTA)"),
    ("n10", "n10_cta.mp4", 32.20, 3.80, "lv_0_20251221233711 67.43-71.23 pair on mat (CTA)"),
]
TOTAL = round(CLIPS[-1][2] + CLIPS[-1][3], 3)
CUTS = [c[2] for c in CLIPS[1:]]

# ---- Captions (phrase, hidden, keywords). hidden=True where a graphic already shows that clause ----------
CHUNKS = [
    ("Kalau nak cari", True, ""), ("kasut sukan,", True, ""), ("korang cari yang", True, ""), ("macam belah kanan ni.", True, ""),
    ("Lantunan dia", True, ""), ("lebih tinggi tau.", True, ""),
    ("Itu maksudnya", False, ""), ("bila korang", False, ""), ("berjoging ataupun", False, "BERJOGING"), ("berlari kan,", False, "BERLARI"),
    ("rasa lebih bouncy", False, "BOUNCY"), ("macam ada spring", False, "SPRING"), ("kat tapak kaki tu.", False, ""),
    ("Memang syok gila", False, "SYOK"), ("pakai untuk", True, ""), ("bersukan ataupun", True, ""), ("casual tau.", True, ""),
    ("Nak pakai untuk", True, ""), ("travel pun", True, ""), ("memang best sangat.", False, "BEST"),
    ("Dan yang paling", False, ""), ("penting,", False, "PENTING"), ("untuk korang yang", False, ""), ("badan plus size tu,", False, "PLUS SIZE"),
    ("foam dekat tapak", True, ""), ("ni dia agak", True, ""), ("tebal dan serap", True, ""), ("hentakan tau.", True, ""),
    ("So korang nak", False, ""), ("berjalan lama pun,", False, "LAMA"), ("tak pedih tumit", False, "TAK PEDIH"), ("dah lepas ni.", False, ""),
    ("Dengan kain yang", True, ""), ("breathable macam ni,", True, ""),
    ("memang selesa sangat", False, "SELESA"), ("korang nak pakai", False, ""), ("untuk aktiviti", False, ""), ("seharian.", False, "SEHARIAN"),
    ("Sekarang harga", True, ""), ("tengah murah tau,", True, ""), ("tapi untuk tempoh", True, ""), ("terhad je.", True, ""),
    ("Sebelum korang", False, ""), ("terlepas,", False, "TERLEPAS"),
    ("better korang grab", True, ""), ("sekarang dekat link", True, ""), ("bawah ni.", True, ""),
]

# ---- SFX cues -------------------------------------------------------------------------------------
SFX_LEN = {"whoosh": 0.45, "pop": 0.12, "ding": 1.0, "impact": 0.9, "cha_ching": 1.1, "riser": 1.5, "zap": 0.25}
SFX = [
    (0.02, "impact", 0.9), (0.30, "whoosh", 0.7), (1.45, "pop", 0.8), (2.30, "pop", 0.6), (3.64, "ding", 0.6), (4.60, "zap", 0.7),
    (5.35, "whoosh", 0.7), (5.60, "ding", 0.6), (8.05, "whoosh", 0.7), (9.75, "pop", 0.7),
    (11.35, "zap", 0.6), (12.72, "pop", 0.7), (13.50, "pop", 0.7), (14.85, "pop", 0.7),
    (14.95, "whoosh", 0.6), (17.45, "zap", 0.6), (19.26, "ding", 0.6), (21.15, "whoosh", 0.7),
    (24.75, "zap", 0.6), (25.10, "ding", 0.6),
    (28.00, "riser", 0.6), (29.38, "impact", 0.8), (30.56, "cha_ching", 0.8), (31.43, "pop", 0.7),
    (32.95, "pop", 0.6), (33.05, "pop", 0.7), (33.15, "pop", 0.7), (33.25, "pop", 0.7), (33.55, "pop", 0.8), (35.20, "zap", 0.5),
]

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
        js.append(f'tl.fromTo("#c{i} .capline",{{scale:0.82,y:12}},{{scale:1,y:0,duration:0.14,ease:"back.out(3)"}},{a});')
    return "\n      ".join(html), "\n      ".join(js)


def build():
    def video(i, cid, f, s, d):
        vol = CLIP_VOL.get(cid, FOOTAGE_VOL)
        audio = f'data-volume="{vol}" data-has-audio="true"'
        if cid == "n01":  # square split-screen shown in full over a pre-blurred fill (no crop)
            return (f'<video id="n01bg" class="clip shot" src="assets/clips/n01_bg.mp4" data-start="{s}" data-duration="{d}" '
                    f'data-media-start="0" muted playsinline data-track-index="0"></video>\n      '
                    f'<video id="n01" class="clip sq" src="assets/clips/{f}" data-start="{s}" data-duration="{d}" '
                    f'data-media-start="0" {audio} data-track-index="1" playsinline></video>')
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
                 "__CAPTION_JS__": cap_js, "__VO__": VO_FILE, "__VOLEN__": str(VO_LEN),
                 "__H1__": f"{H1}px", "__H2__": f"{H2}px", "__CAP__": f"{CAP}px"}.items():
        html = html.replace(k, v)
    html = re.sub(r"\{\{(\d+(?:\.\d+)?)\}\}", lambda m: px(float(m.group(1))), html)
    (ROOT / "index.html").write_text(html)
    (ROOT / "edit-decision-list.json").write_text(json.dumps({
        "fps": FPS, "duration": TOTAL, "voiceover": {"file": VO_FILE, "start": 0, "volume": 1.0, "length": VO_LEN},
        "footage_volume": FOOTAGE_VOL, "sfx_volume": SFX_VOL, "headline_px": H1, "subheadline_px": H2, "caption_px": CAP,
        "clips": [dict(id=c[0], file=c[1], start=c[2], duration=c[3], volume=CLIP_VOL.get(c[0], FOOTAGE_VOL), source=c[4]) for c in CLIPS],
        "captions": [dict(start=a, end=b, text=" ".join(w["text"] for w in t), hidden=h) for a, b, t, h, k in caption_chunks()],
        "sfx": [dict(time=t, name=n, gain=g) for t, n, g in SFX],
    }, indent=2, ensure_ascii=False))
    print("wrote index.html, duration", TOTAL)


def block(bid, start, dur, chip, dots, title, sub=""):
    d = "".join(f'<i class="{"on" if k < dots else ""}"></i>' for k in range(3))
    sub_html = f'<div class="display sub" id="{bid}s">{sub}</div>' if sub else ""
    return (f'<div class="clip feat" id="{bid}" data-start="{start}" data-duration="{dur}" data-track-index="12">\n'
            f'        <div class="shade-top"></div>\n        <div class="dots">{d}</div>\n        <div class="box">\n'
            f'          <div class="chip label" id="{bid}chip">{chip}</div>\n'
            f'          <div class="display title"><span id="{bid}t">{title}</span></div>\n          {sub_html}\n        </div>\n      </div>')


BLOCKS = "\n      ".join([
    block("f1", 5.4, 6.0, "Ciri <b>#1</b>", 1, "Lantunan tinggi"),
    block("f2", 19.2, 5.6, "Ciri <b>#2</b>", 2, "Foam tebal", sub="+ Serap hentakan"),
    block("f3", 24.8, 4.6, "Ciri <b>#3</b>", 3, "Kain breathable"),
])

LINKSVG = ('<svg class="lnk" viewBox="0 0 100 100"><g fill="none" stroke="#000" stroke-width="12" stroke-linecap="round">'
           '<path d="M42 58 L58 42"/><path d="M47 30 L56 21 a17 17 0 0 1 24 24 L71 54"/><path d="M53 70 L44 79 a17 17 0 0 1 -24 -24 L29 46"/></g></svg>')

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
      video.sq { top: 580px; height: 1080px; object-fit: cover; transform-origin: 50% 50%; }
      .flash { background: #fff; opacity: 0; }
      .display { font-family: var(--font-display); text-transform: uppercase; line-height: 0.95; color: #fff;
                 -webkit-text-stroke: 6px #000; paint-order: stroke fill; text-wrap: balance; }
      .label { font-family: var(--font-label); font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
      .shade-top { position: absolute; left: 0; right: 0; top: 0; height: 900px;
                   background: linear-gradient(180deg, rgba(0,0,0,.7) 0%, rgba(0,0,0,.35) 55%, rgba(0,0,0,0) 100%); }

      /* HOOK (headline on one line; wraps only if it cannot fit) */
      #hook .chip { position: absolute; top: 300px; left: 120px; right: 120px; text-align: center; }
      #hook .chip span { display: inline-block; background: #000; color: var(--yellow); padding: 7px 16px; border-radius: 999px;
                         font-size: {{40}}; border: 2px solid var(--yellow); }
      #hook .h { position: absolute; top: 350px; left: 120px; right: 120px; text-align: center; font-size: __H1__; }
      #hook .h .y { color: var(--yellow); }
      #hook .tag { position: absolute; top: 620px; padding: 6px 12px; border-radius: 9px; font-size: {{42}}; border: 2px solid #000; }
      #hook .tag.l { left: 140px; background: #d9d9d9; color: #000; }
      #hook .tag.r { left: 660px; background: var(--neon); color: #000; }
      #hook .mk { position: absolute; height: 0; transform-origin: 0 50%; }
      #hook .mk.l { left: 40px; width: 460px; top: 1273px; border-top: 5px dashed rgba(255,255,255,.9); }
      #hook .mk.r { left: 580px; width: 460px; top: 1191px; border-top: 6px solid var(--neon); }
      #hook .ring { position: absolute; left: 706px; top: 1141px; width: 100px; height: 100px; border-radius: 50%;
                    border: 6px solid var(--neon); opacity: 0; }
      #hook .up { position: absolute; left: 500px; top: 1000px; width: 300px; text-align: left; font-size: __H2__; line-height: 1; }
      #hook .up .g { color: var(--neon); }

      /* FEATURE BLOCKS */
      .feat .box { position: absolute; top: 330px; left: 120px; right: 120px; }
      .feat .chip { display: inline-flex; align-items: center; gap: 10px; background: var(--neon); color: #000;
                    padding: 8px 16px; border-radius: 10px; font-size: {{40}}; border: 3px solid #000; }
      .feat .chip b { background: #000; color: var(--neon); border-radius: 6px; padding: 1px 8px; }
      .feat .title { font-size: __H1__; margin-top: 12px; overflow: hidden; padding-bottom: 6px; }
      .feat .title > span { display: inline-block; }
      .feat .sub { font-size: __H2__; color: var(--yellow); margin-top: 4px; }
      .feat .dots { position: absolute; top: 300px; left: 120px; display: flex; gap: 10px; }
      .feat .dots i { width: 56px; height: 8px; border-radius: 5px; background: rgba(255,255,255,.35); display: block; }
      .feat .dots i.on { background: var(--neon); }

      /* SPRING */
      #spring svg { position: absolute; left: 790px; top: 820px; width: 110px; height: 180px; transform-origin: 50% 100%; }

      /* ACTIVITY chips */
      #acts .list { position: absolute; top: 330px; left: 120px; display: flex; flex-direction: column; gap: 12px; }
      #acts .it { display: inline-flex; align-items: center; gap: 12px; background: rgba(0,0,0,.75); border: 3px solid var(--neon);
                  border-radius: 14px; padding: 6px 18px 3px 10px; font-size: __H2__; align-self: flex-start; }
      #acts .it i { width: 38px; height: 38px; border-radius: 50%; background: var(--neon); display: inline-flex; align-items: center;
                    justify-content: center; font-style: normal; color: #000; font-family: var(--font-label); font-weight: 900;
                    font-size: 24px; -webkit-text-stroke: 0; margin-bottom: 3px; }

      /* PLUS-SIZE chip */
      #plus .chip { position: absolute; top: 330px; left: 150px; display: inline-flex; align-items: center; gap: 10px;
                    background: var(--yellow); color: #000; -webkit-text-stroke: 0; font-size: __H2__; padding: 8px 18px 4px;
                    border: 4px solid #000; border-radius: 14px; box-shadow: 5px 5px 0 #000; }

      /* HEAT arrows */
      #heat .a { position: absolute; width: 56px; height: 56px; border-left: 11px solid #ff7a1a; border-top: 11px solid #ff7a1a;
                 transform: rotate(45deg); filter: drop-shadow(0 0 4px #000); opacity: 0; }

      /* CTA */
      #buy .box { position: absolute; top: 330px; left: 120px; right: 120px; text-align: center; }
      #buy .h1 { font-size: 56px; }
      #buy .stamp { display: inline-block; margin-top: 10px; background: var(--yellow); color: #000; -webkit-text-stroke: 0;
                    font-size: __H1__; line-height: 1.05; padding: 6px 30px 2px; border: 6px solid #000; border-radius: 16px;
                    box-shadow: 7px 7px 0 #000; transform-origin: 50% 50%; }
      #buy .timer { position: absolute; left: 0; right: 0; top: 590px; text-align: center; }
      #buy .timer span { display: inline-flex; align-items: center; gap: 10px; background: var(--red); color: #fff; font-size: {{48}};
                         padding: 8px 20px; border-radius: 999px; border: 3px solid #000; }
      #buy .timer svg { width: 30px; height: 30px; }
      #buy .card { position: absolute; left: 120px; width: 660px; top: 580px; background: rgba(0,0,0,.8);
                   border: 4px solid var(--neon); border-radius: 22px; padding: 16px 20px 14px; text-align: center; }
      #buy .pick { font-size: __H2__; color: var(--neon); }
      #buy .sw { display: flex; justify-content: center; align-items: flex-start; gap: 14px; margin: 10px 0 8px; }
      #buy .sw .tile { width: 192px; display: flex; flex-direction: column; align-items: center; gap: 5px; transform-origin: 50% 60%; }
      #buy .sw img { width: 192px; height: 240px; object-fit: cover; border-radius: 14px; border: 3px solid #fff; display: block; }
      #buy .sw .nm { font-size: {{40}}; color: #fff; text-align: center; line-height: 1.1; letter-spacing: 0.04em; }
      #buy .line { font-family: var(--font-label); font-weight: 800; color: #fff; font-size: {{46}}; line-height: 1.3;
                   display: flex; align-items: center; justify-content: center; gap: 8px; }
      #buy .line em { font-style: normal; color: var(--yellow); }
      #buy .btn { position: absolute; left: 0; right: 0; top: 1020px; text-align: center; }
      #buy .btn span { display: inline-flex; align-items: center; gap: 12px; background: var(--yellow); color: #000; -webkit-text-stroke: 0;
                       font-size: __H2__; padding: 10px 26px 6px; border: 4px solid #000; border-radius: 999px; box-shadow: 5px 5px 0 #000; }
      #buy .btn .lnk { width: 44px; height: 44px; }
      #buy .arrows { position: absolute; left: 0; right: 0; top: 1110px; display: flex; flex-direction: column; align-items: center; }
      #buy .arrows i { width: 40px; height: 40px; border-right: 10px solid var(--yellow); border-bottom: 10px solid var(--yellow);
                       transform: rotate(45deg); margin-top: -14px; display: block; filter: drop-shadow(0 0 3px #000); }

      /* CAPTIONS: Anton __CAP__, uppercase, black stroke, centre-bottom */
      .cap .capline { position: absolute; left: 120px; width: 840px; top: 1185px; display: flex; justify-content: center;
                      flex-wrap: wrap; gap: 0 11px; transform-origin: 50% 50%; }
      .cap .w { font-family: var(--font-display); font-size: __CAP__; line-height: 1.1; text-transform: uppercase; color: #fff;
                -webkit-text-stroke: 7px #000; paint-order: stroke fill; display: inline-block; letter-spacing: 0.02em;
                text-shadow: 0 3px 8px rgba(0,0,0,.5); }
      .cap .w.kw { color: var(--neon); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="__TOTAL__" data-fps="__FPS__" data-width="1080" data-height="1920">
      <!-- FOOTAGE (10 clips) -->
      __VIDEOS__

      <!-- VOICEOVER: original, 100%, uncut -->
      <audio id="vo" src="__VO__" data-start="0" data-duration="__VOLEN__" data-media-start="0" data-volume="1"></audio>

      <!-- HOOK 0-5.4 -->
      <div class="clip" id="hook" data-start="0" data-duration="5.4" data-track-index="11">
        <div class="shade-top"></div>
        <div class="chip"><span class="label" id="hchip">Nak cari kasut sukan?</span></div>
        <div class="display h" id="hh"><span id="hh1">Cari yang</span> <span class="y" id="hh2">belah kanan</span></div>
        <div class="mk l" id="mkl"></div>
        <div class="mk r" id="mkr"></div>
        <div class="ring" id="hring"></div>
        <div class="tag l label" id="tagl">Kasut lain</div>
        <div class="tag r label" id="tagr">Steapex</div>
        <div class="up display" id="hup"><span class="g">Lantun</span><br />lebih tinggi &uarr;</div>
      </div>

      <!-- FEATURE BLOCKS -->
      __BLOCKS__
      <div class="clip" id="spring" data-start="9.6" data-duration="1.8" data-track-index="13">
        <svg id="spr" viewBox="0 0 60 100"><polyline points="30,0 30,8 6,16 54,26 6,36 54,46 6,56 54,66 6,76 54,86 30,92 30,100"
          fill="none" stroke="#39ff14" stroke-width="7" stroke-linejoin="round" stroke-linecap="round" style="filter:drop-shadow(0 0 3px #000)"/></svg>
      </div>

      <!-- ACTIVITIES 11.4-16.5 -->
      <div class="clip" id="acts" data-start="11.4" data-duration="5.1" data-track-index="12">
        <div class="shade-top"></div>
        <div class="list">
          <div class="it display" id="a1"><i>&check;</i>Bersukan</div>
          <div class="it display" id="a2"><i>&check;</i>Casual</div>
          <div class="it display" id="a3"><i>&check;</i>Travel</div>
        </div>
      </div>

      <!-- PLUS SIZE 17.5-19.2 -->
      <div class="clip" id="plus" data-start="17.5" data-duration="1.7" data-track-index="12">
        <div class="shade-top"></div>
        <div class="chip display" id="pchip">Paling penting!</div>
      </div>

      <div class="clip" id="heat" data-start="25.6" data-duration="3.8" data-track-index="13">
        <div class="a" id="ha1" style="left:700px;top:900px"></div>
        <div class="a" id="ha2" style="left:800px;top:960px"></div>
        <div class="a" id="ha3" style="left:900px;top:900px"></div>
      </div>

      <!-- CTA 29.4-end -->
      <div class="clip" id="buy" data-start="29.4" data-duration="6.6" data-track-index="15">
        <div class="shade-top"></div>
        <div class="box">
          <div class="display h1" id="bh1">Harga tengah</div>
          <div class="display stamp" id="bstamp">Murah!</div>
        </div>
        <div class="timer" id="btimer"><span class="label"><svg viewBox="0 0 100 100"><circle cx="50" cy="54" r="38" fill="#fff" stroke="#000" stroke-width="6"/>
          <path d="M50 54 V30 M50 54 L66 64" stroke="#000" stroke-width="8" stroke-linecap="round"/><rect x="40" y="4" width="20" height="10" rx="3" fill="#000"/></svg>Tempoh terhad</span></div>
        <div class="card" id="bcard">
          <div class="display pick">Grab sekarang!</div>
          <div class="sw" id="bsw">
            <div class="tile" id="sw1"><img src="assets/img/shoe_teal.jpg" alt="" /><div class="nm label">Emerald<br />Green</div></div>
            <div class="tile" id="sw2"><img src="assets/img/shoe_white.jpg" alt="" /><div class="nm label">Violet</div></div>
            <div class="tile" id="sw3"><img src="assets/img/shoe_black.jpg" alt="" /><div class="nm label">Black</div></div>
          </div>
        </div>
        <div class="btn" id="bbtn"><span class="display">__LINK__ Link bawah ni</span></div>
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
      tl.fromTo("#hh1", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "power4.in" }, 1.25);
      tl.fromTo("#hh2", { scale: 2.2, rotation: -6, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.28, ease: "power4.in" }, 2.0);
      tl.fromTo("#mkl", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: "power2.out" }, 1.43);
      tl.fromTo("#mkr", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: "power2.out" }, 1.47);
      gsap.set("#hring", { opacity: 0 });
      tl.fromTo("#hring", { scale: 0.5, opacity: 1 }, { scale: 1.6, opacity: 0, duration: 0.5, immediateRender: false }, 1.47);
      tl.fromTo("#tagl", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.25, ease: "back.out(2)" }, 2.29);
      tl.fromTo("#tagr", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.25, ease: "back.out(2)" }, 2.34);
      tl.fromTo("#hup", { x: 50, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(2)" }, 3.64);
      tl.fromTo("#hring", { scale: 0.5, opacity: 1 }, { scale: 1.6, opacity: 0, duration: 0.5, immediateRender: false }, 4.21);

      // FEATURE TITLES
      [["f1", 5.4, 5.5], ["f2", 19.2, 19.26], ["f3", 24.8, 25.28]].forEach(([id, t, tt]) => {
        tl.fromTo(`#${id}chip`, { x: -200, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, tt - 0.1);
        tl.fromTo(`#${id}t`, { yPercent: 105 }, { yPercent: 0, duration: 0.35, ease: "power3.out" }, tt);
        tl.fromTo(`#${id} .dots`, { opacity: 0 }, { opacity: 1, duration: 0.25 }, t);
      });
      tl.fromTo("#f2s", { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 20.82);

      // SPRING
      tl.fromTo("#spr", { scale: 0 }, { scale: 1, duration: 0.25, ease: "back.out(2)" }, 9.62);
      for (let k = 0; k < 3; k++) {
        tl.to("#spr", { scaleY: 0.55, duration: 0.16, ease: "power2.in" }, 9.9 + k * 0.42);
        tl.to("#spr", { scaleY: 1.1, duration: 0.18, ease: "back.out(3)" }, 10.06 + k * 0.42);
      }

      // ACTIVITY chips
      [["#a1", 12.72], ["#a2", 13.5], ["#a3", 14.85]].forEach(([q, t]) => {
        tl.fromTo(q, { x: -60, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, t);
      });

      // PLUS SIZE
      tl.fromTo("#pchip", { scale: 0, rotation: -8 }, { scale: 1, rotation: -2, duration: 0.3, ease: "back.out(2.4)" }, 17.6);

      // HEAT rising
      ["#ha1", "#ha2", "#ha3"].forEach((q, i) => {
        for (let k = 0; k < 2; k++) {
          const t = 25.7 + i * 0.2 + k * 1.3;
          tl.fromTo(q, { y: 0, opacity: 0 }, { y: -240, opacity: 1, duration: 0.5, ease: "none", immediateRender: k === 0 }, t);
          tl.to(q, { y: -330, opacity: 0, duration: 0.35, ease: "none" }, t + 0.5);
        }
      });

      // CTA
      tl.fromTo("#bh1", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 29.6);
      tl.fromTo("#bstamp", { scale: 3, rotation: 0, opacity: 0 }, { scale: 1, rotation: -4, opacity: 1, duration: 0.3, ease: "power4.in" }, 30.27);
      tl.fromTo("#btimer", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.4)" }, 31.1);
      tl.to("#btimer", { scale: 1.06, duration: 0.18, yoyo: true, repeat: 3, ease: "sine.inOut" }, 31.5);
      tl.to("#btimer", { opacity: 0, y: -20, duration: 0.2 }, 32.75);
      tl.fromTo("#bcard", { y: 70, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 32.95);
      tl.fromTo("#bsw .tile", { scale: 0, rotation: -8 }, { scale: 1, rotation: 0, duration: 0.3, stagger: 0.1, ease: "back.out(2.6)" }, 33.05);
      tl.fromTo("#bbtn", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.4)" }, 33.55);
      tl.to("#bbtn span", { scale: 1.06, duration: 0.15, yoyo: true, repeat: 1, ease: "sine.inOut" }, 34.81);
      gsap.set("#barr i", { opacity: 0 });
      tl.to("#barr i", { opacity: 1, duration: 0.12, stagger: 0.08 }, 34.6);
      tl.to("#barr i", { opacity: 0.25, duration: 0.12, stagger: 0.08 }, 34.95);
      tl.to("#barr i", { opacity: 1, duration: 0.12, stagger: 0.08 }, 35.25);

      // CAPTIONS (word timing from the VO; active word yellow, keywords neon green)
      __CAPTION_JS__

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
""".replace("__BLOCKS__", BLOCKS).replace("__LINK__", LINKSVG)

if __name__ == "__main__":
    build()
