"""Generate index.html (the HyperFrames composition) from one edit decision list.

Run:  python3 tools/build.py   (from the video/ folder)
Everything time-related lives in the tables below so cuts, flashes, captions and SFX stay in sync.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 60
FOOTAGE_VOL = 0.30   # original footage sound at 30% (no clip has music, so none is muted)
SFX_VOL = 0.32       # SFX sit low; there is no voiceover in the source footage

# ---- Edit decision list: (id, file, start, duration, source note) -------------------------------
CLIPS = [
    ("c01", "c01_hook.mp4", 0.0, 4.0, "video_20260117_220257 0.5-4.5  treadmill feet (intro, one shot)"),
    ("c02", "c02_foam.mp4", 4.0, 3.0, "lv_0_20251221130556 60.5-63.5 midsole foam close-up"),
    ("c03", "c03_ball.mp4", 7.0, 4.0, "lv_7535...181155 0.3-4.3 ball-drop impact test (right half of split-screen, cropped 9:16)"),
    ("c04", "c04_flex.mp4", 11.0, 3.0, "lv_0_20251221130556 40.5-43.5 sole flex"),
    ("c05", "c05_jump.mp4", 14.0, 3.0, "video_20260429_114829 41-44 jumping on track"),
    ("c06", "c06_scale.mp4", 17.0, 3.0, "video_20251221_162434 0.8-3.8 shoe on scale 240g"),
    ("c07", "c07_smoke.mp4", 20.0, 3.5, "lv_0_20251221130556 77.8-81.3 smoke through mesh"),
    ("c08", "c08_run.mp4", 23.5, 3.5, "video_20260429_114602 5-8.5 jogging on track"),
    ("c09", "c09_bag.mp4", 27.0, 3.3, "lv_0_20251220180407 83-86.3 Steapex shoe bag"),
    ("c10", "c10_pair.mp4", 30.3, 3.0, "lv_0_20251221130556 93-96 hero pair"),
]
TOTAL = round(CLIPS[-1][2] + CLIPS[-1][3], 3)
CUTS = [c[2] for c in CLIPS[1:]]

# ---- Captions: (start, end, words, keywords). No VO exists, so captions follow the script. -------
# Hidden on purpose where a graphic already shows the same clause: hook, feature titles,
# "dan ringan" (240g badge), "walaupun jogging lebih 10KM" (distance tracker), whole CTA.
CAPTIONS = [
    (7.35, 8.55, ["SERAP", "IMPAK", "HENTAK"], {"IMPAK"}),
    (8.60, 9.40, ["DENGAN", "BAIK"], set()),
    (9.50, 10.25, ["WALAUPUN", "BADAN"], set()),
    (10.25, 10.95, ["PLUS", "SIZE"], {"PLUS", "SIZE"}),
    (14.30, 15.40, ["RASA", "BOUNCY"], {"BOUNCY"}),
    (15.50, 16.90, ["BILA", "JOGGING"], set()),
    (23.70, 24.95, ["TAK", "PANAS"], {"TAK", "PANAS"}),
]

# ---- SFX cues: (time, name, relative gain) ------------------------------------------------------
SFX_LEN = {"whoosh": 0.45, "pop": 0.12, "ding": 1.0, "impact": 0.9, "cha_ching": 1.1, "riser": 1.5, "zap": 0.25}
SFX = [
    (0.02, "impact", 1.0), (0.32, "whoosh", 0.8), (0.95, "pop", 0.9),
    (3.80, "whoosh", 0.9), (4.15, "ding", 0.7),
    (6.95, "zap", 0.8), (7.40, "pop", 0.6),
    (10.80, "whoosh", 0.9), (11.15, "ding", 0.7),
    (13.85, "whoosh", 0.8), (14.35, "pop", 0.6),
    (16.95, "zap", 0.8), (18.70, "pop", 1.0),
    (19.80, "whoosh", 0.9), (20.15, "ding", 0.7),
    (23.45, "zap", 0.8), (23.75, "pop", 0.6),
    (25.50, "riser", 0.8), (27.00, "impact", 0.9), (27.35, "cha_ching", 0.9),
    (30.25, "whoosh", 0.8), (30.80, "pop", 0.9),
]

# Natural sizes x 0.70 (the brief asks for 70% of the first pass); caption stays at 60px.
S = 0.70
def px(v): return f"{round(v * S)}px"


def captions_html():
    out = []
    for i, (a, b, words, kws) in enumerate(CAPTIONS):
        spans = "".join(
            f'<span class="w{" kw" if w in kws else ""}" id="cap{i}w{j}">{w}</span>' for j, w in enumerate(words)
        )
        out.append(
            f'<div class="clip cap" id="cap{i}" data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="20">'
            f'<div class="capline">{spans}</div></div>'
        )
    return "\n      ".join(out)


def captions_js():
    js = []
    for i, (a, b, words, kws) in enumerate(CAPTIONS):
        js.append(f'tl.fromTo("#cap{i} .capline",{{scale:0.82,y:18}},{{scale:1,y:0,duration:0.14,ease:"back.out(3)"}},{a});')
        step = (b - a) / len(words)
        for j, w in enumerate(words):
            t = round(a + j * step, 3)
            sel = f"#cap{i}w{j}"
            if w in kws:
                js.append(f'tl.fromTo("{sel}",{{scale:1}},{{scale:1.14,duration:0.08}},{t});')
                js.append(f'tl.to("{sel}",{{scale:1,duration:0.1}},{round(t + step * 0.9, 3)});')
            else:
                js.append(f'tl.set("{sel}",{{color:"var(--yellow)"}},{t});')
                js.append(f'tl.set("{sel}",{{color:"#fff"}},{round(t + step, 3)});')
    return "\n      ".join(js)


def build():
    videos = "\n      ".join(
        f'<video id="{cid}" class="clip shot" src="assets/clips/{f}" data-start="{s}" data-duration="{d}" '
        f'data-media-start="0" data-volume="{FOOTAGE_VOL}" data-has-audio="true" data-track-index="{i}" playsinline></video>'
        for i, (cid, f, s, d, _) in enumerate(CLIPS)
    )
    flashes = "\n      ".join(
        f'<div class="clip flash" id="fl{i}" data-start="{t}" data-duration="0.3" data-track-index="30"></div>'
        for i, t in enumerate(CUTS)
    )
    sfx = "\n      ".join(
        f'<audio id="sfx{i}" src="assets/sfx/{n}.wav" data-start="{t}" data-duration="{SFX_LEN[n]}" '
        f'data-volume="{round(SFX_VOL * g, 3)}"></audio>'
        for i, (t, n, g) in enumerate(SFX)
    )
    zoom_js = "\n      ".join(
        f'tl.fromTo("#{cid}",{{scale:1.0}},{{scale:1.07,duration:0.45,ease:"power2.out"}},{s});'
        f'tl.to("#{cid}",{{scale:1.11,duration:{round(d - 0.45, 3)},ease:"none"}},{round(s + 0.45, 3)});'
        for cid, f, s, d, _ in CLIPS
    )
    flash_js = "\n      ".join(
        f'tl.fromTo("#fl{i}",{{opacity:0.9}},{{opacity:0,duration:0.22,ease:"power1.out"}},{t});'
        for i, t in enumerate(CUTS)
    )

    html = TEMPLATE
    for k, v in {
        "__TOTAL__": str(TOTAL), "__FPS__": str(FPS), "__VIDEOS__": videos, "__FLASHES__": flashes,
        "__SFX__": sfx, "__CAPTIONS__": captions_html(), "__ZOOM_JS__": zoom_js, "__FLASH_JS__": flash_js,
        "__CAPTION_JS__": captions_js(),
    }.items():
        html = html.replace(k, v)
    # size tokens
    import re
    html = re.sub(r"\{\{(\d+(?:\.\d+)?)\}\}", lambda m: px(float(m.group(1))), html)
    (ROOT / "index.html").write_text(html)
    (ROOT / "edit-decision-list.json").write_text(json.dumps({
        "fps": FPS, "duration": TOTAL, "footage_volume": FOOTAGE_VOL, "sfx_volume": SFX_VOL,
        "clips": [dict(id=c[0], file=c[1], start=c[2], duration=c[3], source=c[4]) for c in CLIPS],
        "captions": [dict(start=a, end=b, words=w, keywords=sorted(k)) for a, b, w, k in CAPTIONS],
        "sfx": [dict(time=t, name=n, gain=g) for t, n, g in SFX],
    }, indent=2))
    print("wrote index.html, duration", TOTAL)


TEMPLATE = r"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Anton"; src: url("assets/fonts/Anton-latin.woff2") format("woff2"); font-weight: 400; font-display: block; }
      @font-face { font-family: "Montserrat"; src: url("assets/fonts/Montserrat-latin.woff2") format("woff2"); font-weight: 100 900; font-display: block; }
      :root {
        --ground: #000;
        --ink: #ffffff;
        --yellow: #ffe100;
        --neon: #39ff14;
        --teal: #19d6c6;
        --font-display: "Anton", sans-serif;
        --font-label: "Montserrat", sans-serif;
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }
      .clip { position: absolute; inset: 0; width: 1080px; height: 1920px; }
      video.shot { object-fit: cover; transform-origin: 50% 50%; }
      .flash { background: #fff; opacity: 0; }

      /* shared text treatments */
      .display { font-family: var(--font-display); text-transform: uppercase; line-height: 0.95; color: #fff;
                 -webkit-text-stroke: {{12}} #000; paint-order: stroke fill; }
      .label { font-family: var(--font-label); font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
      .shade-top { position: absolute; left: 0; right: 0; top: 0; height: 900px;
                   background: linear-gradient(180deg, rgba(0,0,0,.72) 0%, rgba(0,0,0,.35) 55%, rgba(0,0,0,0) 100%); }
      .shade-bot { position: absolute; left: 0; right: 0; bottom: 0; height: 760px;
                   background: linear-gradient(0deg, rgba(0,0,0,.6) 0%, rgba(0,0,0,0) 100%); }

      /* HOOK */
      #hook .brand { position: absolute; top: 300px; left: 0; right: 0; text-align: center; }
      #hook .brand span { display: inline-block; background: rgba(0,0,0,.55); color: #fff; padding: 12px 26px; border-radius: 999px;
                          font-size: {{42}}; border: 3px solid var(--teal); }
      #hook .row { position: absolute; top: 440px; left: 0; right: 0; display: flex; justify-content: center; align-items: center; gap: {{36}}; }
      #hook .num { font-size: {{440}}; color: var(--neon); line-height: 0.82; -webkit-text-stroke: {{16}} #000; paint-order: stroke fill;
                   text-shadow: 0 0 40px rgba(57,255,20,.55); position: relative; }
      #hook .ring { position: absolute; left: 50%; top: 50%; width: 420px; height: 420px; margin: -210px 0 0 -210px;
                    border: 10px solid var(--neon); border-radius: 50%; opacity: 0; }
      #hook .stack { display: flex; flex-direction: column; gap: 6px; }
      #hook .l { font-size: {{130}}; overflow: hidden; }
      #hook .l > span { display: inline-block; }
      #hook .padu { color: var(--yellow); font-size: {{190}}; position: relative; }
      #hook .uline { position: absolute; left: 0; right: 0; bottom: -6px; height: 16px; background: var(--neon);
                     transform-origin: 0 50%; transform: scaleX(0); border: 3px solid #000; }

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

      /* BALL TEST TAG */
      #balltag .tag { position: absolute; left: 120px; top: 960px; background: #000; color: var(--yellow);
                      font-size: {{42}}; padding: 12px 22px; border-radius: 12px; border: 3px solid var(--yellow); }
      #balltag .chev { position: absolute; left: 640px; top: 760px; display: flex; flex-direction: column; align-items: center; }
      #balltag .chev i { width: 64px; height: 64px; border-right: 14px solid var(--neon); border-bottom: 14px solid var(--neon);
                         transform: rotate(45deg); margin-top: -22px; display: block; filter: drop-shadow(0 0 3px #000); }

      /* 240g BADGE */
      #weight .badge { position: absolute; left: 120px; top: 880px; width: 300px; height: 300px; border-radius: 50%;
                       background: var(--yellow); border: 8px solid #000; display: flex; flex-direction: column;
                       align-items: center; justify-content: center; box-shadow: 0 16px 40px rgba(0,0,0,.45); }
      #weight .badge .v { font-family: var(--font-display); font-size: {{150}}; color: #000; line-height: 0.9; }
      #weight .badge .v small { font-size: {{80}}; }
      #weight .badge .k { font-size: {{40}}; color: #000; margin-top: 8px; }

      /* DISTANCE TRACKER */
      #track .card { position: absolute; left: 120px; width: 660px; top: 760px; background: rgba(0,0,0,.72);
                     border: 4px solid var(--neon); border-radius: 26px; padding: 26px 34px; }
      #track .top { display: flex; justify-content: space-between; align-items: baseline; }
      #track .lbl { color: #fff; font-size: {{42}}; }
      #track .val { font-family: var(--font-display); color: var(--neon); font-size: {{150}}; line-height: 1; }
      #track .val small { font-size: {{80}}; color: #fff; margin-left: 8px; }
      #track .bar { height: 22px; background: rgba(255,255,255,.18); border-radius: 12px; overflow: hidden; margin-top: 16px; }
      #track .bar i { display: block; height: 100%; width: 100%; background: linear-gradient(90deg, var(--teal), var(--neon));
                      transform-origin: 0 50%; transform: scaleX(0); }
      #track .note { color: var(--yellow); font-size: {{42}}; margin-top: 14px; }

      /* CTA */
      #cta .box { position: absolute; top: 300px; left: 120px; right: 120px; text-align: center; }
      #cta .chip { display: inline-block; background: var(--yellow); color: #000; padding: 12px 28px; border-radius: 999px;
                   font-size: {{44}}; border: 4px solid #000; }
      #cta .h { font-size: {{150}}; margin-top: 20px; }
      #cta .h .y { color: var(--neon); }
      #cta .subp { display: inline-block; margin-top: 22px; background: rgba(0,0,0,.7); color: #fff; font-family: var(--font-label);
                   font-weight: 600; font-size: {{48}}; padding: 14px 28px; border-radius: 18px; }
      #ctabtn .btn { position: absolute; left: 450px; top: 1020px; white-space: nowrap;
                     background: var(--neon); color: #000; border: 6px solid #000; border-radius: 999px; padding: 22px 54px;
                     font-size: {{64}}; -webkit-text-stroke: 0; box-shadow: 0 8px 30px rgba(0,0,0,.5); }
      #ctabtn .brand { position: absolute; left: 120px; width: 660px; top: 1180px; text-align: center; color: #fff; font-size: {{42}};
                       text-shadow: 0 2px 8px #000; }

      #ctabtn .brand span { background: rgba(0,0,0,.75); padding: 8px 20px; border-radius: 999px; }
      /* CAPTIONS: Anton 60px, uppercase, black stroke, centre-bottom */
      .cap .capline { position: absolute; left: 120px; width: 840px; top: 1140px; display: flex; justify-content: center;
                      flex-wrap: wrap; gap: 0 22px; transform-origin: 50% 50%; }
      .cap .w { font-family: var(--font-display); font-size: 60px; line-height: 1.1; text-transform: uppercase; color: #fff;
                -webkit-text-stroke: 10px #000; paint-order: stroke fill; display: inline-block; letter-spacing: 0.02em;
                text-shadow: 0 4px 10px rgba(0,0,0,.5); }
      .cap .w.kw { color: var(--neon); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="__TOTAL__" data-fps="__FPS__" data-width="1080" data-height="1920">
      <!-- FOOTAGE (10 clips, original sound 30%) -->
      __VIDEOS__

      <!-- HOOK 0-4s -->
      <div class="clip" id="hook" data-start="0" data-duration="4" data-track-index="11">
        <div class="shade-top"></div>
        <div class="brand"><span class="label">Steapex &middot; Wind Spirit</span></div>
        <div class="row">
          <div class="display num" id="h3">3<div class="ring" id="hring"></div></div>
          <div class="stack">
            <div class="display l"><span id="hl1">Ciri Kasut</span></div>
            <div class="display l"><span id="hl2">Jogging</span></div>
            <div class="display l padu"><span id="hl3">Padu</span><div class="uline" id="hul" data-layout-allow-overflow></div></div>
          </div>
        </div>
      </div>

      <!-- FEATURE 1: 4-11s -->
      <div class="clip feat" id="f1" data-start="4" data-duration="7" data-track-index="12">
        <div class="shade-top"></div>
        <div class="dots"><i class="on"></i><i></i><i></i></div>
        <div class="box">
          <div class="chip label" id="f1chip">Ciri <b>#1</b></div>
          <div class="display title"><span id="f1t">Foam Tebal</span></div>
          <div class="display sub" id="f1s">+ Shock Absorption</div>
        </div>
      </div>
      <div class="clip" id="balltag" data-start="7" data-duration="4" data-track-index="13">
        <div class="tag label" id="btag">Ujian bola jatuh</div>
        <div class="chev" id="bchev"><i></i><i></i><i></i></div>
      </div>

      <!-- FEATURE 2: 11-20s -->
      <div class="clip feat" id="f2" data-start="11" data-duration="9" data-track-index="12">
        <div class="shade-top"></div>
        <div class="dots"><i class="on"></i><i class="on"></i><i></i></div>
        <div class="box">
          <div class="chip label" id="f2chip">Ciri <b>#2</b></div>
          <div class="display title"><span id="f2t">Tapak Responsive</span></div>
        </div>
      </div>
      <div class="clip" id="weight" data-start="17" data-duration="3" data-track-index="13">
        <div class="badge" id="wbadge"><div class="v">240<small>g</small></div><div class="k label">Ringan</div></div>
      </div>

      <!-- FEATURE 3: 20-27s -->
      <div class="clip feat" id="f3" data-start="20" data-duration="7" data-track-index="12">
        <div class="shade-top"></div>
        <div class="dots"><i class="on"></i><i class="on"></i><i class="on"></i></div>
        <div class="box">
          <div class="chip label" id="f3chip">Ciri <b>#3</b></div>
          <div class="display title"><span id="f3t">Kain Breathable</span></div>
        </div>
      </div>
      <div class="clip" id="track" data-start="23.5" data-duration="3.5" data-track-index="13">
        <div class="card" id="tcard">
          <div class="top"><div class="lbl label">Jogging</div><div class="val"><span id="tval">0.0</span><small>KM+</small></div></div>
          <div class="bar"><i id="tbar"></i></div>
          <div class="note label">Walaupun lebih 10KM</div>
        </div>
      </div>

      <!-- CTA 27-33.3s -->
      <div class="clip" id="cta" data-start="27" data-duration="6.3" data-track-index="14">
        <div class="shade-top"></div>
        <div class="box">
          <div class="chip label" id="cchip">Bonus percuma</div>
          <div class="display h" id="ch"><span id="ch1">Dapat beg kasut</span><br /><span class="y" id="ch2">sekali!</span></div>
          <div class="subp" id="csub">Kasut kotor boleh simpan terus</div>
        </div>
      </div>
      <div class="clip" id="ctabtn" data-start="30.3" data-duration="3" data-track-index="15">
        <div class="shade-bot"></div>
        <div class="btn display" id="cbtn">Beli sekarang &darr;</div>
        <div class="brand label" id="cbrand"><span>Steapex &middot; Wind Spirit</span></div>
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

      // brief zoom-in on every clip
      __ZOOM_JS__

      // white flash at each cut
      __FLASH_JS__

      // HOOK
      tl.fromTo("#h3", { scale: 3.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.28, ease: "power4.in" }, 0.0);
      tl.fromTo("#hring", { scale: 0.6, opacity: 1 }, { scale: 1.9, opacity: 0, duration: 0.6, ease: "power2.out" }, 0.28);
      tl.fromTo("#hl1", { yPercent: 110 }, { yPercent: 0, duration: 0.3, ease: "power3.out" }, 0.32);
      tl.fromTo("#hl2", { yPercent: 110 }, { yPercent: 0, duration: 0.3, ease: "power3.out" }, 0.46);
      tl.fromTo("#hl3", { scale: 0, rotation: -8 }, { scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2.6)" }, 0.95);
      tl.to("#hul", { scaleX: 1, duration: 0.3, ease: "power2.out" }, 1.15);
      tl.fromTo("#hook .brand span", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 0.6);
      tl.to("#h3", { scale: 1.06, duration: 0.15, yoyo: true, repeat: 1 }, 2.2);
      tl.to("#hook .row", { y: -16, duration: 1.6, ease: "sine.inOut" }, 2.0);

      // FEATURE TITLES
      [["f1", 4], ["f2", 11], ["f3", 20]].forEach(([id, t]) => {
        tl.fromTo(`#${id}chip`, { x: -260, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, t + 0.05);
        tl.fromTo(`#${id}t`, { yPercent: 105 }, { yPercent: 0, duration: 0.35, ease: "power3.out" }, t + 0.15);
        tl.fromTo(`#${id} .dots`, { opacity: 0 }, { opacity: 1, duration: 0.25 }, t);
      });
      tl.fromTo("#f1s", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 4.45);

      // BALL TEST
      tl.fromTo("#btag", { x: -300, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.6)" }, 7.1);
      gsap.set("#bchev i", { opacity: 0.15 });
      for (let k = 0; k < 6; k++) {
        tl.to("#bchev i", { opacity: 1, duration: 0.18, stagger: 0.12 }, 7.2 + k * 0.6);
        tl.to("#bchev i", { opacity: 0.15, duration: 0.18, stagger: 0.12 }, 7.5 + k * 0.6);
      }

      // 240g BADGE
      tl.fromTo("#wbadge", { scale: 0, rotation: -25 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.4)" }, 18.7);

      // DISTANCE TRACKER
      tl.fromTo("#tcard", { y: 80, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 23.75);
      const km = { v: 0 };
      tl.fromTo(km, { v: 0 }, { v: 10, duration: 1.8, ease: "power2.out",
        onUpdate: () => { document.getElementById("tval").textContent = km.v.toFixed(1); } }, 24.0);
      tl.fromTo("#tbar", { scaleX: 0 }, { scaleX: 1, duration: 1.8, ease: "power2.out" }, 24.0);

      // CTA
      tl.fromTo("#cchip", { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(2.5)" }, 27.05);
      tl.fromTo("#ch1", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 27.2);
      tl.fromTo("#ch2", { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "power4.in" }, 27.4);
      tl.fromTo("#csub", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 27.8);
      gsap.set("#cbtn", { xPercent: -50 });
      tl.fromTo("#cbtn", { scale: 0 }, { scale: 1, duration: 0.35, ease: "back.out(2.2)" }, 30.75);
      tl.fromTo("#cbrand", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 31.0);
      tl.to("#cbtn", { scale: 1.07, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }, 31.3);

      // CAPTIONS (active word yellow, keywords neon green)
      __CAPTION_JS__

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    build()
