"""Generate index.html for "Tips Jogging Untuk Pemula" (video6). No voiceover: captions follow the script.

Run from video6/:  python3 tools/build.py
Format: ../video/FORMAT.md, with this video's update: headline 150px, sub-headline 70px, ~70 MB render.
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 60
FOOTAGE_VOL = 0.30                     # original footage sound at 30% (no source clip contains music or speech)
CLIP_VOL = {"t08": 0.08}               # smoke spray hiss -> 8%
CLIP_ORIGIN = {"t04": "50% 82%"}       # zoom anchored low so the shoes stay in frame
SFX_VOL = 0.32
H1 = 100   # headline px
H2 = 47    # sub-headline px (all text scaled x2/3 with the headline: 150 -> 100)

# ---- Edit decision list (10 clips) ---------------------------------------------------------------
CLIPS = [
    ("t01", "t01_run.mp4", 0.00, 4.20, "video_20260429_114602 4.6-8.8 runner on track, Emerald Green (intro, one shot)"),
    ("t02", "t02_jog.mp4", 4.20, 4.40, "lv_0_20251221233711 54.4-58.8 jogging on the spot, Emerald Green"),
    ("t03", "t03_tread.mp4", 8.60, 3.40, "video_20260117_220257 0.5-3.9 treadmill feet, Emerald Green"),
    ("t04", "t04_knees.mp4", 12.00, 6.50, "video_20260118_102336 2.0-8.5 high-knee warm-up in park, Emerald Green"),
    ("t05", "t05_foam.mp4", 18.50, 3.00, "lv_0_20251220180407 56.65-59.65 squeezing midsole foam, Black"),
    ("t06", "t06_massage.mp4", 21.50, 2.10, "B ROLL video_20260429_114700 0.3-2.4 massaging a sore foot (foot-pain part)"),
    ("t07", "t07_hop.mp4", 23.60, 3.40, "lv_0_20251221233711 41.4-44.8 feet hopping, Emerald Green"),
    ("t08", "t08_smoke.mp4", 27.00, 4.30, "lv_0_20251221130556 77.55-81.85 smoke through mesh, Emerald Green"),
    ("t09", "t09_bounce.mp4", 31.30, 4.00, "lv_0_20251221130556 64.8-68.8 shoe pressed and springing back up, Emerald Green"),
    ("t10", "t10_cta.mp4", 35.30, 4.97, "lv_0_20251221233711 67.43-72.4 pair on mat (CTA)"),
]
TOTAL = round(CLIPS[-1][2] + CLIPS[-1][3], 3)
CUTS = [c[2] for c in CLIPS[1:]]

# ---- Captions (no VO): (start, end, text, keywords). Hook, headlines and CTA are graphics -> no caption.
CAPTIONS = [
    (5.30, 6.40, "Pastikan heart rate", "HEART RATE"), (6.40, 7.30, "maintain dalam", ""), (7.30, 8.30, "Zone 2.", "ZONE 2"),
    (8.70, 9.60, "Pace laju", "PACE"), (9.60, 10.50, "bukan ukuran", ""), (10.50, 11.85, "kesihatan.", "KESIHATAN"),
    (13.00, 14.30, "Jangan terus berlari", "JANGAN"), (14.30, 15.20, "tanpa panaskan", ""), (15.20, 16.00, "badan.", ""),
    (16.20, 17.10, "Dapat kurangkan", ""), (17.10, 18.40, "risiko injury.", "INJURY"),
    (20.00, 21.00, "Dapat kurangkan", ""), (21.60, 22.40, "sakit pada", "SAKIT"), (22.40, 23.50, "tapak kaki.", ""),
    (23.90, 24.80, "Lebih enjoy", "ENJOY"), (24.80, 26.70, "jogging setiap hari.", ""),
    (28.20, 29.40, "Tak rasa berkuap", "BERKUAP"), (29.40, 30.30, "atau panas bila", "PANAS"), (30.30, 31.25, "jogging lama.", ""),
    (32.50, 33.70, "Lebih stabil pada", "STABIL"), (33.70, 35.20, "setiap langkah.", ""),
]

# ---- SFX cues -------------------------------------------------------------------------------------
SFX_LEN = {"whoosh": 0.45, "pop": 0.12, "ding": 1.0, "impact": 0.9, "cha_ching": 1.1, "riser": 1.5, "zap": 0.25}
SFX = [
    (0.02, "impact", 0.9), (0.35, "whoosh", 0.7), (0.80, "pop", 0.8), (2.20, "pop", 0.9), (2.35, "ding", 0.6),
    (4.15, "whoosh", 0.7), (4.35, "ding", 0.6), (5.50, "pop", 0.7), (7.30, "ding", 0.5), (8.55, "zap", 0.6),
    (11.95, "whoosh", 0.7), (12.15, "ding", 0.6), (13.20, "pop", 0.6),
    (18.45, "zap", 0.6), (18.65, "ding", 0.6), (21.45, "whoosh", 0.6), (21.65, "impact", 0.5), (23.55, "whoosh", 0.6),
    (26.95, "zap", 0.6), (27.15, "ding", 0.6), (31.25, "whoosh", 0.7), (31.45, "ding", 0.6),
    (33.80, "riser", 0.6), (35.28, "impact", 0.8), (35.60, "cha_ching", 0.7),
    (36.35, "pop", 0.7), (36.45, "pop", 0.7), (36.55, "pop", 0.7), (36.90, "pop", 0.8), (37.60, "zap", 0.5),
]

S = 0.70 * 2 / 3  # small labels: 70%-of-first-pass scale, then x2/3 with the headline (150 -> 100px)
def px(v): return f"{round(v * S)}px"


def captions():
    html, js = [], []
    for i, (a, b, text, kws) in enumerate(CAPTIONS):
        words = text.split(); kw = set(kws.split()); step = (b - a) / len(words)
        spans = []
        for j, w in enumerate(words):
            up = w.upper().rstrip(".,?!"); is_kw = up in kw
            spans.append(f'<span class="w{" kw" if is_kw else ""}" id="c{i}w{j}">{up}</span>')
            t0 = round(a + j * step, 3); t1 = round(t0 + step, 3); sel = f"#c{i}w{j}"
            if is_kw:
                js.append(f'tl.fromTo("{sel}",{{scale:1}},{{scale:1.14,duration:0.08}},{t0});tl.to("{sel}",{{scale:1,duration:0.1}},{round(t1 - 0.05, 3)});')
            else:
                js.append(f'tl.set("{sel}",{{color:"var(--yellow)"}},{t0});tl.set("{sel}",{{color:"#fff"}},{t1});')
        html.append(f'<div class="clip cap" id="c{i}" data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="20">'
                    f'<div class="capline">{"".join(spans)}</div></div>')
        js.append(f'tl.fromTo("#c{i} .capline",{{scale:0.82,y:18}},{{scale:1,y:0,duration:0.14,ease:"back.out(3)"}},{a});')
    return "\n      ".join(html), "\n      ".join(js)


def build():
    def video(i, cid, f, s, d):
        vol = CLIP_VOL.get(cid, FOOTAGE_VOL)
        org = f' style="transform-origin:{CLIP_ORIGIN[cid]}"' if cid in CLIP_ORIGIN else ""
        return (f'<video id="{cid}" class="clip shot"{org} src="assets/clips/{f}" data-start="{s}" data-duration="{d}" '
                f'data-media-start="0" data-volume="{vol}" data-has-audio="true" data-track-index="{i}" playsinline></video>')
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
    for k, v in {"__TOTAL__": str(TOTAL), "__FPS__": str(FPS), "__VIDEOS__": videos, "__FLASHES__": flashes, "__SFX__": sfx,
                 "__CAPTIONS__": cap_html, "__ZOOM_JS__": zoom, "__FLASH_JS__": flash_js, "__CAPTION_JS__": cap_js,
                 "__BAG__": BAG, "__H1__": f"{H1}px", "__H2__": f"{H2}px"}.items():
        html = html.replace(k, v)
    html = re.sub(r"\{\{(\d+(?:\.\d+)?)\}\}", lambda m: px(float(m.group(1))), html)
    (ROOT / "index.html").write_text(html)
    (ROOT / "edit-decision-list.json").write_text(json.dumps({
        "fps": FPS, "duration": TOTAL, "voiceover": None, "footage_volume": FOOTAGE_VOL, "sfx_volume": SFX_VOL,
        "headline_px": H1, "subheadline_px": H2,
        "clips": [dict(id=c[0], file=c[1], start=c[2], duration=c[3], volume=CLIP_VOL.get(c[0], FOOTAGE_VOL), source=c[4]) for c in CLIPS],
        "captions": [dict(start=a, end=b, text=t, keywords=k) for a, b, t, k in CAPTIONS],
        "sfx": [dict(time=t, name=n, gain=g) for t, n, g in SFX],
    }, indent=2, ensure_ascii=False))
    print("wrote index.html, duration", TOTAL)


BAG = ('<svg class="bagsvg" viewBox="0 0 100 100"><path d="M32 34 V26 a18 18 0 0 1 36 0 V34" fill="none" stroke="#000" stroke-width="9" stroke-linecap="round"/>'
       '<path d="M14 32 H86 L80 92 H20 Z" fill="#ffe100" stroke="#000" stroke-width="6" stroke-linejoin="round"/>'
       '<path d="M38 52 a12 12 0 0 0 24 0" fill="none" stroke="#000" stroke-width="6" stroke-linecap="round"/></svg>')


def block(bid, start, dur, chip, dots, n_dots, title, sub="", pre=""):
    d = "".join(f'<i class="{"on" if k < dots else ""}"></i>' for k in range(n_dots))
    pre_html = f'<div class="display sub pre" id="{bid}p">{pre}</div>' if pre else ""
    sub_html = f'<div class="display sub" id="{bid}s">{sub}</div>' if sub else ""
    return (f'<div class="clip feat" id="{bid}" data-start="{start}" data-duration="{dur}" data-track-index="12">\n'
            f'        <div class="shade-top"></div>\n        <div class="dots">{d}</div>\n        <div class="box">\n'
            f'          <div class="chip label" id="{bid}chip">{chip}</div>\n          {pre_html}\n'
            f'          <div class="display title"><span id="{bid}t">{title}</span></div>\n          {sub_html}\n        </div>\n      </div>')


BLOCKS = "\n      ".join([
    block("k1", 4.2, 7.8, "Tips <b>#1</b>", 1, 3, "Fokus pada<br />heart rate", sub="Bukan pace!"),
    block("k2", 12.0, 6.5, "Tips <b>#2</b>", 2, 3, "Warm up", sub="Sebelum mula"),
    block("k3", 18.5, 8.5, "Tips <b>#3</b>", 3, 3, "Shock<br />absorption", pre="Pakai kasut yang ada"),
    block("u1", 27.0, 4.3, "Kelebihan <b>#1</b>", 1, 2, "Kain<br />breathable"),
    block("u2", 31.3, 4.0, "Kelebihan <b>#2</b>", 2, 2, "Plate<br />flexible"),
])

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
                 -webkit-text-stroke: 6px #000; paint-order: stroke fill; }
      .label { font-family: var(--font-label); font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
      .shade-top { position: absolute; left: 0; right: 0; top: 0; height: 1000px;
                   background: linear-gradient(180deg, rgba(0,0,0,.75) 0%, rgba(0,0,0,.4) 60%, rgba(0,0,0,0) 100%); }
      .shade-bot { position: absolute; left: 0; right: 0; bottom: 0; height: 760px;
                   background: linear-gradient(0deg, rgba(0,0,0,.6) 0%, rgba(0,0,0,0) 100%); }

      /* HOOK */
      #hook .h { position: absolute; top: 330px; left: 120px; right: 120px; text-align: center; font-size: __H1__; }
      #hook .h .y { color: var(--yellow); }
      #hook .save { position: absolute; top: 560px; left: 0; right: 0; text-align: center; }
      #hook .save span { display: inline-flex; align-items: center; gap: 12px; background: var(--neon); color: #000; -webkit-text-stroke: 0;
                         font-size: __H2__; line-height: 1.05; padding: 10px 24px 7px; border: 5px solid #000; border-radius: 16px;
                         box-shadow: 6px 6px 0 #000; text-align: left; }
      #hook .save svg { width: 47px; height: 60px; flex: none; }

      /* TIP / USP BLOCKS: headline __H1__, sub-headline __H2__ */
      .feat .box { position: absolute; top: 330px; left: 120px; right: 120px; }
      .feat .chip { display: inline-flex; align-items: center; gap: 14px; background: var(--neon); color: #000;
                    padding: 8px 16px; border-radius: 10px; font-size: {{40}}; border: 3px solid #000; }
      .feat .chip b { background: #000; color: var(--neon); border-radius: 8px; padding: 2px 12px; }
      .feat .title { font-size: __H1__; margin-top: 12px; overflow: hidden; padding-bottom: 8px; }
      .feat .title > span { display: inline-block; }
      .feat .sub { font-size: __H2__; color: var(--yellow); margin-top: 4px; }
      .feat .sub.pre { color: #fff; margin-top: 12px; }
      .feat .dots { position: absolute; top: 300px; left: 120px; display: flex; gap: 12px; }
      .feat .dots i { width: 70px; height: 10px; border-radius: 6px; background: rgba(255,255,255,.35); display: block; }
      .feat .dots i.on { background: var(--neon); }

      /* HEART RATE widget */
      #hr .card { position: absolute; left: 120px; width: 460px; top: 640px; background: rgba(0,0,0,.78);
                  border: 3px solid var(--red); border-radius: 18px; padding: 14px 20px; }
      #hr .top { display: flex; align-items: center; gap: 15px; }
      #hr .heart { width: 56px; height: 56px; flex: none; }
      #hr .bpm { font-family: var(--font-display); color: #fff; font-size: 64px; line-height: 1; }
      #hr .bpm small { font-family: var(--font-label); font-weight: 800; font-size: 20px; color: #bbb; margin-left: 6px; letter-spacing: .06em; }
      #hr .zones { display: flex; gap: 6px; margin-top: 11px; }
      #hr .zones i { flex: 1; height: 30px; border-radius: 7px; font-style: normal; display: flex; align-items: center; justify-content: center;
                     font-family: var(--font-label); font-weight: 800; font-size: 19px; color: rgba(0,0,0,.75); opacity: .35; }
      #hr .zones i.z2 { outline: 0 solid #fff; }

      /* WARM-UP gauge */
      #warm .g { position: absolute; left: 860px; top: 640px; width: 56px; height: 300px; border: 6px solid #fff; border-radius: 40px;
                 background: rgba(0,0,0,.5); overflow: hidden; box-shadow: 0 0 0 4px #000; }
      #warm .g i { position: absolute; left: 0; right: 0; bottom: 0; height: 100%; display: block; transform-origin: 50% 100%; transform: scaleY(0);
                   background: linear-gradient(0deg, #19d6c6 0%, #ffe100 55%, #ff5a1f 100%); }
      #warm .bulb { position: absolute; left: 846px; top: 925px; width: 84px; height: 84px; border-radius: 50%; background: #ff5a1f;
                    border: 6px solid #fff; box-shadow: 0 0 0 4px #000; }

      /* PAIN overlay */
      #pain .vig { position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(255,0,0,0) 45%, rgba(255,20,40,.55) 100%); opacity: 0; }
      #pain .ring { position: absolute; left: 160px; top: 1380px; width: 320px; height: 320px; border-radius: 50%;
                    border: 10px solid var(--red); opacity: 0; box-shadow: 0 0 20px rgba(255,45,61,.7); }

      /* HEAT arrows */
      #heat .a { position: absolute; width: 70px; height: 70px; border-left: 14px solid #ff7a1a; border-top: 14px solid #ff7a1a;
                 transform: rotate(45deg); filter: drop-shadow(0 0 4px #000); opacity: 0; }

      /* CTA */
      #buy .box { position: absolute; top: 330px; left: 120px; right: 120px; text-align: center; }
      #buy .h1 { font-size: __H1__; }
      #buy .h1 .y { color: var(--yellow); }
      #buy .sub2 { font-size: __H2__; color: var(--yellow); margin-top: 4px; display: inline-flex; align-items: center; gap: 10px; }
      #buy .sub2 .bagsvg { width: 47px; height: 47px; }
      #buy .card { position: absolute; left: 120px; width: 660px; top: 600px; background: rgba(0,0,0,.78);
                   border: 5px solid var(--neon); border-radius: 28px; padding: 20px 24px 16px; }
      #buy .sw { display: flex; justify-content: center; align-items: flex-start; gap: 14px; }
      #buy .sw .tile { width: 192px; display: flex; flex-direction: column; align-items: center; gap: 6px; transform-origin: 50% 60%; }
      #buy .sw img { width: 192px; height: 240px; object-fit: cover; border-radius: 16px; border: 4px solid #fff; display: block; }
      #buy .sw .nm { font-size: {{40}}; color: #fff; text-align: center; line-height: 1.1; letter-spacing: 0.04em; }
      #buy .bigbag { position: absolute; left: 130px; top: 1000px; width: 150px; height: 150px; }
      #buy .bigbag .bagsvg { width: 150px; height: 150px; filter: drop-shadow(0 6px 10px rgba(0,0,0,.5)); }
      #buy .arrows { position: absolute; left: 165px; top: 1155px; display: flex; flex-direction: column; align-items: center; }
      #buy .arrows i { width: 56px; height: 56px; border-right: 14px solid var(--yellow); border-bottom: 14px solid var(--yellow);
                       transform: rotate(45deg); margin-top: -20px; display: block; filter: drop-shadow(0 0 3px #000); }

      /* CAPTIONS: Anton 60px, uppercase, black stroke, centre-bottom */
      .cap .capline { position: absolute; left: 120px; width: 840px; top: 1140px; display: flex; justify-content: center;
                      flex-wrap: wrap; gap: 0 11px; transform-origin: 50% 50%; }
      .cap .w { font-family: var(--font-display); font-size: 40px; line-height: 1.1; text-transform: uppercase; color: #fff;
                -webkit-text-stroke: 7px #000; paint-order: stroke fill; display: inline-block; letter-spacing: 0.02em;
                text-shadow: 0 4px 10px rgba(0,0,0,.5); }
      .cap .w.kw { color: var(--neon); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="__TOTAL__" data-fps="__FPS__" data-width="1080" data-height="1920">
      <!-- FOOTAGE (10 clips, original sound 30%) -->
      __VIDEOS__

      <!-- HOOK 0-4.2 -->
      <div class="clip" id="hook" data-start="0" data-duration="4.2" data-track-index="11">
        <div class="shade-top"></div>
        <div class="display h"><span id="hh1">Tips jogging</span><br /><span id="hh2">untuk </span><span class="y" id="hh3">pemula</span></div>
        <div class="save" id="hsave"><span class="display"><svg viewBox="0 0 70 90"><path d="M6 4 H64 V86 L35 64 L6 86 Z" fill="#000"/></svg>Save video<br />sebelum hilang!</span></div>
      </div>

      <!-- TIPS & USP BLOCKS -->
      __BLOCKS__

      <!-- HEART RATE widget 5.2-12.0 -->
      <div class="clip" id="hr" data-start="5.2" data-duration="6.8" data-track-index="13">
        <div class="card" id="hrcard">
          <div class="top">
            <svg class="heart" id="hrh" viewBox="0 0 100 90"><path d="M50 86 C20 62 4 46 4 26 C4 12 15 2 28 2 C38 2 46 8 50 16 C54 8 62 2 72 2 C85 2 96 12 96 26 C96 46 80 62 50 86 Z" fill="#ff2d3d" stroke="#000" stroke-width="4"/></svg>
            <div class="bpm"><span id="hrv">90</span><small>BPM</small></div>
          </div>
          <div class="zones"><i style="background:#9aa4b1">Z1</i><i class="z2" id="hrz2" style="background:#39ff14">Z2</i><i style="background:#ffe100">Z3</i><i style="background:#ff9f1a">Z4</i><i style="background:#ff2d3d">Z5</i></div>
        </div>
      </div>

      <!-- WARM-UP gauge 12.0-18.5 -->
      <div class="clip" id="warm" data-start="12" data-duration="6.5" data-track-index="13">
        <div class="g" id="wg"><i id="wfill"></i></div>
        <div class="bulb"></div>
      </div>

      <!-- PAIN 21.5-23.6 (B-roll: sore foot) -->
      <div class="clip" id="pain" data-start="21.5" data-duration="2.1" data-track-index="13">
        <div class="vig" id="pvig"></div>
        <div class="ring" id="pring"></div>
      </div>

      <!-- HEAT 28.0-31.3 -->
      <div class="clip" id="heat" data-start="28" data-duration="3.3" data-track-index="13">
        <div class="a" id="ha1" style="left:700px;top:900px"></div>
        <div class="a" id="ha2" style="left:800px;top:960px"></div>
        <div class="a" id="ha3" style="left:900px;top:900px"></div>
      </div>

      <!-- CTA 35.3-end -->
      <div class="clip" id="buy" data-start="35.3" data-duration="4.97" data-track-index="15">
        <div class="shade-top"></div>
        <div class="box">
          <div class="display h1" id="bh1">Pilih <span class="y">warna</span> kasut</div>
          <div class="display sub2" id="bh2">di beg kuning __BAG__</div>
        </div>
        <div class="card" id="bcard">
          <div class="sw" id="bsw">
            <div class="tile" id="sw1"><img src="assets/img/shoe_teal.jpg" alt="" /><div class="nm label">Emerald<br />Green</div></div>
            <div class="tile" id="sw2"><img src="assets/img/shoe_white.jpg" alt="" /><div class="nm label">Violet</div></div>
            <div class="tile" id="sw3"><img src="assets/img/shoe_black.jpg" alt="" /><div class="nm label">Black</div></div>
          </div>
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
      tl.fromTo("#hh1", { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.28, ease: "power4.in" }, 0.02);
      tl.fromTo("#hh2", { x: -120, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 0.4);
      tl.fromTo("#hh3", { scale: 2.2, rotation: -10, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.3, ease: "power4.in" }, 0.75);
      tl.fromTo("#hsave", { y: 80, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(2)" }, 2.2);
      tl.to("#hsave span", { scale: 1.06, duration: 0.18, yoyo: true, repeat: 3, ease: "sine.inOut" }, 2.7);

      // BLOCK TITLES
      [["k1", 4.2], ["k2", 12.0], ["k3", 18.5], ["u1", 27.0], ["u2", 31.3]].forEach(([id, t]) => {
        tl.fromTo(`#${id}chip`, { x: -260, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, t + 0.05);
        tl.fromTo(`#${id}t`, { yPercent: 105 }, { yPercent: 0, duration: 0.38, ease: "power3.out" }, t + 0.15);
        tl.fromTo(`#${id} .dots`, { opacity: 0 }, { opacity: 1, duration: 0.25 }, t);
      });
      tl.fromTo("#k1s", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "back.out(2)" }, 4.7);
      tl.fromTo("#k2s", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "back.out(2)" }, 12.5);
      tl.fromTo("#k3p", { y: -20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 18.6);

      // HEART RATE
      tl.fromTo("#hrcard", { y: 80, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 5.4);
      const hr = { v: 90 };
      tl.fromTo(hr, { v: 90 }, { v: 128, duration: 1.8, ease: "power2.out",
        onUpdate: () => { document.getElementById("hrv").textContent = Math.round(hr.v); } }, 5.6);
      for (let k = 0; k < 10; k++) {
        tl.to("#hrh", { scale: 1.15, duration: 0.12, ease: "power2.out" }, 5.6 + k * 0.6);
        tl.to("#hrh", { scale: 1, duration: 0.2, ease: "power2.in" }, 5.72 + k * 0.6);
      }
      tl.to("#hr .zones i", { opacity: 0.35, duration: 0.01 }, 5.4);
      tl.to("#hrz2", { opacity: 1, scale: 1.12, outlineWidth: 4, duration: 0.3, ease: "back.out(2.5)" }, 7.3);

      // WARM-UP gauge
      tl.fromTo("#wfill", { scaleY: 0 }, { scaleY: 1, duration: 4.5, ease: "power1.inOut" }, 13.0);

      // PAIN
      gsap.set(["#pvig", "#pring"], { opacity: 0 });
      tl.fromTo("#pvig", { opacity: 0 }, { opacity: 1, duration: 0.15, immediateRender: false }, 21.6);
      tl.to("#pvig", { opacity: 0.3, duration: 0.5 }, 21.75);
      tl.to("#pvig", { opacity: 1, duration: 0.15 }, 22.4);
      tl.to("#pvig", { opacity: 0, duration: 0.6 }, 22.55);
      tl.fromTo("#pring", { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)", immediateRender: false }, 21.65);
      tl.to("#pring", { scale: 1.1, duration: 0.18, yoyo: true, repeat: 3 }, 22.0);

      // HEAT rising
      ["#ha1", "#ha2", "#ha3"].forEach((s, i) => {
        for (let k = 0; k < 2; k++) {
          const t = 28.2 + i * 0.2 + k * 1.2;
          tl.fromTo(s, { y: 0, opacity: 0 }, { y: -260, opacity: 1, duration: 0.5, ease: "none", immediateRender: k === 0 }, t);
          tl.to(s, { y: -360, opacity: 0, duration: 0.35, ease: "none" }, t + 0.5);
        }
      });

      // CTA
      tl.fromTo("#bh1", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "power4.in" }, 35.35);
      tl.fromTo("#bh2", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "back.out(2)" }, 35.75);
      tl.fromTo("#bcard", { y: 90, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 36.1);
      tl.fromTo("#bsw .tile", { scale: 0, rotation: -8 }, { scale: 1, rotation: 0, duration: 0.3, stagger: 0.1, ease: "back.out(2.6)" }, 36.25);
      [["#sw1", 37.2], ["#sw2", 37.5], ["#sw3", 37.8]].forEach(([s, t]) => {
        tl.to(s, { scale: 1.06, duration: 0.15, ease: "sine.out" }, t);
        tl.to(s, { scale: 1, duration: 0.15, ease: "sine.in" }, t + 0.15);
      });
      tl.fromTo("#bbag", { scale: 0, rotation: -20 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.4)" }, 36.85);
      for (let k = 0; k < 3; k++) {
        tl.to("#bbag", { y: -18, duration: 0.2, ease: "sine.out" }, 37.4 + k * 0.5);
        tl.to("#bbag", { y: 0, duration: 0.2, ease: "sine.in" }, 37.6 + k * 0.5);
      }
      gsap.set("#barr i", { opacity: 0 });
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 37.1);
      tl.to("#barr i", { opacity: 0.2, duration: 0.15, stagger: 0.1 }, 37.6);
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 38.1);

      // CAPTIONS (active word yellow, keywords neon green)
      __CAPTION_JS__

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
""".replace("__BLOCKS__", BLOCKS)

if __name__ == "__main__":
    build()
