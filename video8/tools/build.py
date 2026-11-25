"""Generate index.html for "Tips Jogging Untuk Orang Obese" (video8). No voiceover: captions follow the script.

Run from video8/:  python3 tools/build.py
Format: ../video/FORMAT.md (headline 100px, sub-headline 47px, caption 40px, ~70 MB render).
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 60
FOOTAGE_VOL = 0.30                     # original footage sound at 30% (no source clip contains music or speech)
CLIP_VOL = {"o08": 0.08}               # smoke spray hiss -> 8%
CLIP_ORIGIN = {"o02": "50% 70%", "o04": "50% 55%"}
SFX_VOL = 0.32
H1 = 100   # headline px
H2 = 47    # sub-headline px (all text scaled x2/3 with the headline: 150 -> 100)

# ---- Edit decision list (10 clips) ---------------------------------------------------------------
CLIPS = [
    ("o01", "o01_run.mp4", 0.00, 4.20, "video_20260429_114602 4.6-8.8 runner on track, Emerald Green (intro, one shot)"),
    ("o02", "o02_walk.mp4", 4.20, 4.50, "video_20260117_220711 1.0-5.5 brisk walk on treadmill, Black"),
    ("o03", "o03_tread.mp4", 8.70, 3.80, "video_20260117_220257 0.5-4.3 treadmill feet, Emerald Green"),
    ("o04", "o04_squat.mp4", 12.50, 8.50, "Strength workout.mov 0.4-8.9 goblet squat (cropped above the ankles: other-brand shoes out of frame; inset over blurred fill so the face clears the headline)"),
    ("o05", "o05_foam.mp4", 21.00, 3.00, "lv_0_20251220180407 56.65-59.65 squeezing midsole foam, Black"),
    ("o06", "o06_massage.mp4", 24.00, 2.10, "B ROLL video_20260429_114700 0.3-2.4 massaging a sore foot (foot-pain part)"),
    ("o07", "o07_hop.mp4", 26.10, 3.30, "lv_0_20251221233711 41.4-44.7 feet hopping, Emerald Green"),
    ("o08", "o08_smoke.mp4", 29.40, 4.30, "lv_0_20251221130556 77.55-81.85 smoke through mesh, Emerald Green"),
    ("o09", "o09_bounce.mp4", 33.70, 4.00, "lv_0_20251221130556 64.8-68.8 shoe pressed and springing back up, Emerald Green"),
    ("o10", "o10_cta.mp4", 37.70, 4.97, "lv_0_20251221233711 67.43-72.4 pair on mat (CTA)"),
]
TOTAL = round(CLIPS[-1][2] + CLIPS[-1][3], 3)
CUTS = [c[2] for c in CLIPS[1:]]

# ---- Captions (no VO): (start, end, text, keywords). Hook, headlines and CTA are graphics -> no caption.
CAPTIONS = [
    (8.90, 9.80, "Ikut kadar", ""), (9.80, 10.60, "heart rate,", "HEART RATE"), (10.60, 11.30, "bukan pace.", "PACE"),
    (11.30, 11.90, "Maintain dalam", ""), (11.90, 12.45, "Zone 2 sahaja.", "ZONE 2"),
    (13.60, 14.60, "Untuk kuatkan", "KUATKAN"), (14.60, 15.60, "sendi lutut", "LUTUT"), (15.60, 16.50, "bila tapak kaki", ""),
    (16.50, 17.60, "hentak jalanraya.", "HENTAK"), (17.80, 18.80, "Contoh senaman", ""),
    (22.40, 23.50, "Dapat kurangkan", ""), (24.10, 24.90, "sakit pada", "SAKIT"), (24.90, 26.00, "tapak kaki.", ""),
    (26.40, 27.30, "Lebih enjoy", "ENJOY"), (27.30, 28.30, "brisk walk atau", ""), (28.30, 29.35, "jogging setiap hari.", ""),
    (30.40, 31.50, "Tak rasa berkuap", "BERKUAP"), (31.50, 32.40, "atau panas bila", "PANAS"), (32.40, 33.65, "jogging lama.", ""),
    (34.60, 35.50, "Lebih stabil pada", "STABIL"), (35.50, 36.30, "setiap langkah", ""), (36.30, 36.90, "atau pijak", ""),
    (36.90, 37.65, "permukaan tak rata.", "TAK RATA"),
]

# ---- SFX cues -------------------------------------------------------------------------------------
SFX_LEN = {"whoosh": 0.45, "pop": 0.12, "ding": 1.0, "impact": 0.9, "cha_ching": 1.1, "riser": 1.5, "zap": 0.25}
SFX = [
    (0.02, "impact", 0.9), (0.35, "whoosh", 0.7), (0.80, "pop", 0.8), (2.20, "pop", 0.9), (2.35, "ding", 0.6),
    (4.15, "whoosh", 0.7), (4.35, "ding", 0.6), (5.10, "pop", 0.7), (6.10, "ding", 0.5), (8.65, "zap", 0.6), (9.10, "pop", 0.6), (11.90, "ding", 0.5),
    (12.45, "whoosh", 0.7), (12.65, "ding", 0.6), (16.55, "impact", 0.5), (18.90, "pop", 0.8), (19.60, "pop", 0.8),
    (20.95, "zap", 0.6), (21.15, "ding", 0.6), (23.95, "whoosh", 0.6), (24.15, "impact", 0.5), (26.05, "whoosh", 0.6),
    (29.35, "zap", 0.6), (29.55, "ding", 0.6), (33.65, "whoosh", 0.7), (33.85, "ding", 0.6),
    (36.20, "riser", 0.6), (37.68, "impact", 0.8), (38.10, "cha_ching", 0.8),
    (39.50, "pop", 0.6), (39.62, "pop", 0.7), (39.72, "pop", 0.7), (39.82, "pop", 0.7), (40.30, "pop", 0.8), (41.00, "zap", 0.5),
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
    block("k1", 4.2, 8.3, "Tips <b>#1</b>", 1, 3, "Mula dengan<br />brisk walk", sub="(Jalan laju)"),
    block("k2", 12.5, 8.5, "Tips <b>#2</b>", 2, 3, "Jangan lupa<br />strength workout"),
    block("k3", 21.0, 8.4, "Tips <b>#3</b>", 3, 3, "Shock<br />absorption", pre="Pakai kasut yang ada"),
    block("u1", 29.4, 4.3, "Kelebihan <b>#1</b>", 1, 2, "Kain<br />breathable"),
    block("u2", 33.7, 4.0, "Kelebihan <b>#2</b>", 2, 2, "Plate<br />flexible"),
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

      /* BRISK-WALK timer */
      #walk .card { position: absolute; left: 120px; top: 660px; display: inline-flex; align-items: center; gap: 16px;
                    background: rgba(0,0,0,.78); border: 3px solid var(--neon); border-radius: 18px; padding: 12px 22px; }
      #walk svg { width: 60px; height: 60px; flex: none; }
      #walk .v { font-family: var(--font-display); color: var(--neon); font-size: 64px; line-height: 1; }
      #walk .v small { font-family: var(--font-label); font-weight: 800; font-size: 20px; color: #fff; margin-left: 8px; letter-spacing: .06em; }
      #walk .d { font-family: var(--font-label); font-weight: 800; font-size: 20px; color: #fff; letter-spacing: .06em; margin-top: 4px; }

      /* SQUAT examples */
      #squat .list { position: absolute; top: 620px; left: 120px; display: flex; flex-direction: column; gap: 12px; }
      #squat .it { display: inline-flex; align-items: center; gap: 12px; background: rgba(0,0,0,.78); border: 3px solid var(--neon);
                   border-radius: 14px; padding: 6px 18px 3px 10px; font-size: __H2__; align-self: flex-start; }
      #squat .it i { width: 38px; height: 38px; border-radius: 50%; background: var(--neon); display: inline-flex; align-items: center;
                     justify-content: center; font-style: normal; color: #000; font-family: var(--font-label); font-weight: 900;
                     font-size: 24px; -webkit-text-stroke: 0; margin-bottom: 3px; }

      /* PAIN overlay */
      #pain .vig { position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(255,0,0,0) 45%, rgba(255,20,40,.55) 100%); opacity: 0; }
      #pain .ring { position: absolute; left: 160px; top: 1380px; width: 320px; height: 320px; border-radius: 50%;
                    border: 10px solid var(--red); opacity: 0; box-shadow: 0 0 20px rgba(255,45,61,.7); }

      /* HEAT arrows */
      #heat .a { position: absolute; width: 70px; height: 70px; border-left: 14px solid #ff7a1a; border-top: 14px solid #ff7a1a;
                 transform: rotate(45deg); filter: drop-shadow(0 0 4px #000); opacity: 0; }

      /* CTA */
      #buy .box { position: absolute; top: 330px; left: 120px; right: 120px; text-align: center; }
      #buy .h1 { font-size: 56px; }
      #buy .stamp { display: inline-block; margin-top: 10px; background: var(--yellow); color: #000; -webkit-text-stroke: 0;
                    font-size: __H1__; line-height: 1.05; padding: 6px 30px 2px; border: 6px solid #000; border-radius: 16px;
                    box-shadow: 7px 7px 0 #000; transform-origin: 50% 50%; }
      #buy .card { position: absolute; left: 120px; width: 660px; top: 580px; background: rgba(0,0,0,.8);
                   border: 4px solid var(--neon); border-radius: 22px; padding: 16px 20px 14px; text-align: center; }
      #buy .pick { font-size: __H2__; color: var(--neon); }
      #buy .sw { display: flex; justify-content: center; align-items: flex-start; gap: 14px; margin: 10px 0 8px; }
      #buy .sw .tile { width: 192px; display: flex; flex-direction: column; align-items: center; gap: 5px; transform-origin: 50% 60%; }
      #buy .sw img { width: 192px; height: 240px; object-fit: cover; border-radius: 14px; border: 3px solid #fff; display: block; }
      #buy .sw .nm { font-size: {{40}}; color: #fff; text-align: center; line-height: 1.1; letter-spacing: 0.04em; }
      #buy .line { font-family: var(--font-label); font-weight: 800; color: #fff; font-size: {{46}}; line-height: 1.3;
                   display: flex; align-items: center; justify-content: center; gap: 8px; }
      #buy .line .bagsvg { width: 32px; height: 32px; }
      #buy .line em { font-style: normal; color: var(--yellow); }
      #buy .bigbag { position: absolute; left: 130px; top: 1010px; width: 110px; height: 110px; }
      #buy .bigbag .bagsvg { width: 110px; height: 110px; filter: drop-shadow(0 6px 10px rgba(0,0,0,.5)); }
      #buy .arrows { position: absolute; left: 160px; top: 1130px; display: flex; flex-direction: column; align-items: center; }
      #buy .arrows i { width: 40px; height: 40px; border-right: 10px solid var(--yellow); border-bottom: 10px solid var(--yellow);
                       transform: rotate(45deg); margin-top: -14px; display: block; filter: drop-shadow(0 0 3px #000); }

      /* CAPTIONS: Anton 40px, uppercase, black stroke, centre-bottom */
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
        <div class="display h"><span id="hh1">Tips jogging</span><br /><span id="hh2">untuk orang </span><span class="y" id="hh3">obese</span></div>
        <div class="save" id="hsave"><span class="display"><svg viewBox="0 0 70 90"><path d="M6 4 H64 V86 L35 64 L6 86 Z" fill="#000"/></svg>Save video<br />sebelum hilang!</span></div>
      </div>

      <!-- TIPS & USP BLOCKS -->
      __BLOCKS__

      <!-- BRISK-WALK timer 4.9-8.7 -->
      <div class="clip" id="walk" data-start="4.9" data-duration="3.8" data-track-index="13">
        <div class="card" id="wcard">
          <svg viewBox="0 0 100 100"><circle cx="50" cy="56" r="38" fill="#fff" stroke="#000" stroke-width="6"/>
            <path d="M50 56 V32 M50 56 L66 66" stroke="#000" stroke-width="8" stroke-linecap="round"/><rect x="40" y="4" width="20" height="10" rx="3" fill="#000"/></svg>
          <div><div class="v">20–30<small>MINIT</small></div><div class="d">SETIAP HARI</div></div>
        </div>
      </div>

      <!-- HEART RATE widget 8.7-12.5 -->
      <div class="clip" id="hr" data-start="8.7" data-duration="3.8" data-track-index="13">
        <div class="card" id="hrcard">
          <div class="top">
            <svg class="heart" id="hrh" viewBox="0 0 100 90"><path d="M50 86 C20 62 4 46 4 26 C4 12 15 2 28 2 C38 2 46 8 50 16 C54 8 62 2 72 2 C85 2 96 12 96 26 C96 46 80 62 50 86 Z" fill="#ff2d3d" stroke="#000" stroke-width="4"/></svg>
            <div class="bpm"><span id="hrv">90</span><small>BPM</small></div>
          </div>
          <div class="zones"><i style="background:#9aa4b1">Z1</i><i class="z2" id="hrz2" style="background:#39ff14">Z2</i><i style="background:#ffe100">Z3</i><i style="background:#ff9f1a">Z4</i><i style="background:#ff2d3d">Z5</i></div>
        </div>
      </div>

      <!-- SQUAT examples 18.8-21.0 -->
      <div class="clip" id="squat" data-start="18.8" data-duration="2.2" data-track-index="13">
        <div class="list">
          <div class="it display" id="q1"><i>&check;</i>Squat</div>
          <div class="it display" id="q2"><i>&check;</i>Partial squat</div>
        </div>
      </div>

      <!-- PAIN 24.0-26.1 (B-roll: sore foot) -->
      <div class="clip" id="pain" data-start="24" data-duration="2.1" data-track-index="13">
        <div class="vig" id="pvig"></div>
        <div class="ring" id="pring"></div>
      </div>

      <!-- HEAT 30.4-33.7 -->
      <div class="clip" id="heat" data-start="30.4" data-duration="3.3" data-track-index="13">
        <div class="a" id="ha1" style="left:700px;top:900px"></div>
        <div class="a" id="ha2" style="left:800px;top:960px"></div>
        <div class="a" id="ha3" style="left:900px;top:900px"></div>
      </div>

      <!-- CTA 37.7-end -->
      <div class="clip" id="buy" data-start="37.7" data-duration="4.97" data-track-index="15">
        <div class="shade-top"></div>
        <div class="box">
          <div class="display h1" id="bh1">Harga tengah</div>
          <div class="display stamp" id="bstamp">Murah!</div>
        </div>
        <div class="card" id="bcard">
          <div class="display pick">Pilih warna kasut</div>
          <div class="sw" id="bsw">
            <div class="tile" id="sw1"><img src="assets/img/shoe_teal.jpg" alt="" /><div class="nm label">Emerald<br />Green</div></div>
            <div class="tile" id="sw2"><img src="assets/img/shoe_white.jpg" alt="" /><div class="nm label">Violet</div></div>
            <div class="tile" id="sw3"><img src="assets/img/shoe_black.jpg" alt="" /><div class="nm label">Black</div></div>
          </div>
          <div class="line">di <em>beg kuning</em> __BAG__</div>
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
      [["k1", 4.2], ["k2", 12.5], ["k3", 21.0], ["u1", 29.4], ["u2", 33.7]].forEach(([id, t]) => {
        tl.fromTo(`#${id}chip`, { x: -260, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, t + 0.05);
        tl.fromTo(`#${id}t`, { yPercent: 105 }, { yPercent: 0, duration: 0.38, ease: "power3.out" }, t + 0.15);
        tl.fromTo(`#${id} .dots`, { opacity: 0 }, { opacity: 1, duration: 0.25 }, t);
      });
      tl.fromTo("#k1s", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "back.out(2)" }, 4.7);
            tl.fromTo("#k3p", { y: -20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 21.1);

      // BRISK-WALK timer
      tl.fromTo("#wcard", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.8)" }, 5.0);
      tl.to("#wcard", { scale: 1.06, duration: 0.15, yoyo: true, repeat: 1, ease: "sine.inOut" }, 6.1);

      // HEART RATE
      tl.fromTo("#hrcard", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 8.8);
      const hr = { v: 90 };
      tl.fromTo(hr, { v: 90 }, { v: 122, duration: 1.6, ease: "power2.out",
        onUpdate: () => { document.getElementById("hrv").textContent = Math.round(hr.v); } }, 9.0);
      for (let k = 0; k < 6; k++) {
        tl.to("#hrh", { scale: 1.15, duration: 0.12, ease: "power2.out" }, 9.0 + k * 0.58);
        tl.to("#hrh", { scale: 1, duration: 0.2, ease: "power2.in" }, 9.12 + k * 0.58);
      }
      tl.to("#hr .zones i", { opacity: 0.35, duration: 0.01 }, 8.8);
      tl.to("#hrz2", { opacity: 1, scale: 1.12, outlineWidth: 4, duration: 0.3, ease: "back.out(2.5)" }, 11.9);

      // SQUAT examples
      [["#q1", 18.9], ["#q2", 19.6]].forEach(([q, t]) => {
        tl.fromTo(q, { x: -60, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, t);
      });

      // PAIN
      gsap.set(["#pvig", "#pring"], { opacity: 0 });
      tl.fromTo("#pvig", { opacity: 0 }, { opacity: 1, duration: 0.15, immediateRender: false }, 24.1);
      tl.to("#pvig", { opacity: 0.3, duration: 0.5 }, 24.25);
      tl.to("#pvig", { opacity: 1, duration: 0.15 }, 24.9);
      tl.to("#pvig", { opacity: 0, duration: 0.6 }, 25.05);
      tl.fromTo("#pring", { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)", immediateRender: false }, 24.15);
      tl.to("#pring", { scale: 1.1, duration: 0.18, yoyo: true, repeat: 3 }, 24.5);

      // HEAT rising
      ["#ha1", "#ha2", "#ha3"].forEach((s, i) => {
        for (let k = 0; k < 2; k++) {
          const t = 30.5 + i * 0.2 + k * 1.2;
          tl.fromTo(s, { y: 0, opacity: 0 }, { y: -260, opacity: 1, duration: 0.5, ease: "none", immediateRender: k === 0 }, t);
          tl.to(s, { y: -360, opacity: 0, duration: 0.35, ease: "none" }, t + 0.5);
        }
      });

      // CTA
      tl.fromTo("#bh1", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 37.75);
      tl.fromTo("#bstamp", { scale: 3, rotation: 0, opacity: 0 }, { scale: 1, rotation: -4, opacity: 1, duration: 0.3, ease: "power4.in" }, 38.1);
      tl.fromTo("#bcard", { y: 70, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 39.35);
      tl.fromTo("#bsw .tile", { scale: 0, rotation: -8 }, { scale: 1, rotation: 0, duration: 0.3, stagger: 0.1, ease: "back.out(2.6)" }, 39.5);
      [["#sw1", 40.4], ["#sw2", 40.7], ["#sw3", 41.0]].forEach(([q, t]) => {
        tl.to(q, { scale: 1.06, duration: 0.15, ease: "sine.out" }, t);
        tl.to(q, { scale: 1, duration: 0.15, ease: "sine.in" }, t + 0.15);
      });
      tl.fromTo("#bbag", { scale: 0, rotation: -20 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.4)" }, 40.0);
      for (let k = 0; k < 3; k++) {
        tl.to("#bbag", { y: -14, duration: 0.2, ease: "sine.out" }, 40.5 + k * 0.5);
        tl.to("#bbag", { y: 0, duration: 0.2, ease: "sine.in" }, 40.7 + k * 0.5);
      }
      gsap.set("#barr i", { opacity: 0 });
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 40.25);
      tl.to("#barr i", { opacity: 0.2, duration: 0.15, stagger: 0.1 }, 40.7);
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 41.15);

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
