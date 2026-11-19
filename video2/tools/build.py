"""Generate index.html for the voiceover edit (video2). Same locked format as ../video/FORMAT.md.

Run from video2/:  python3 tools/build.py
The voiceover (assets/audio/vo.wav) is the original track, untouched: 100% volume, starts at 0, no cuts.
Captions are timed from transcript.json (word timings of that same VO).
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 60
FOOTAGE_VOL = 0.30   # original footage sound at 30% (no source clip contains music)
SFX_VOL = 0.30       # SFX kept well under the VO
VO_FILE = "assets/audio/vo.wav"
VO_LEN = 38.613

# ---- Edit decision list (10 clips) ---------------------------------------------------------------
CLIPS = [
    ("v01", "v01_ball.mp4", 0.00, 4.75, "lv_7535...181155 0-4.75 ball-drop split-screen (intro, one shot, natural speed)"),
    ("v02", "v02_flex.mp4", 4.75, 3.25, "lv_0_20251221130556 40.5-43.75 sole flex"),
    ("v03", "v03_hop.mp4", 8.00, 4.95, "lv_0_20251221233711 41.4-46.35 feet hopping"),
    ("v04", "v04_tread.mp4", 12.95, 2.15, "video_20260117_220257 0.5-2.65 treadmill feet"),
    ("v05", "v05_foam.mp4", 15.10, 2.35, "lv_0_20251221130556 35.62-37.97 squeezing midsole foam"),
    ("v06", "v06_run.mp4", 17.45, 2.65, "video_20260429_114602 4.0-6.65 jogging on track"),
    ("v07", "v07_smoke.mp4", 20.10, 4.30, "lv_0_20251221130556 77.55-81.85 smoke through mesh"),
    ("v08", "v08_smokecu.mp4", 24.40, 2.70, "lv_0_20251221130556 82.2-84.9 smoke close-up"),
    ("v09", "v09_knees.mp4", 27.10, 6.55, "video_20260118_102336 2.0-8.55 high knees in park (4K crop)"),
    ("v10", "v10_cta.mp4", 33.65, 4.97, "lv_0_20251221233711 67.43-72.4 pair on mat (CTA)"),
]
TOTAL = round(CLIPS[-1][2] + CLIPS[-1][3], 3)
CUTS = [c[2] for c in CLIPS[1:]]

# ---- Captions: 2-3 word chunks over the VO transcript ---------------------------------------------
# (phrase, hidden, keywords). hidden=True where a graphic already shows that clause.
CHUNKS = [
    ("Nampak tak beza", True, ""), ("antara dua kasut ni.", True, ""),
    ("Kasut belah kanan ni,", True, ""), ("bola tu melantun", True, ""), ("lagi tinggi kan.", True, ""),
    ("Maksudnya, kasut ni", True, ""), ("lebih responsif tau.", True, ""),
    ("Lebih padu.", False, "PADU"),
    ("Sebab tu bila", False, ""), ("korang jogging,", False, ""), ("rasa lebih bouncy.", False, "BOUNCY"),
    ("Macam ada spring", False, "SPRING"), ("kat tapak kaki tu.", False, ""),
    ("Memang best", False, "BEST"), ("gila weh.", False, ""),
    ("Yang badan besar", False, "BADAN BESAR"), ("tu korang jangan", False, "JANGAN"), ("risau.", False, "RISAU"),
    ("Foam dia tebal", True, ""), ("dan boleh serap", True, ""), ("hentakan dengan bagus.", True, ""),
    ("Korang jogging", False, ""), ("lebih 10KM pun,", False, "10KM"), ("tumit tak", False, "TAK"), ("pedih tau.", False, "PEDIH"),
    ("Dan yang paling", False, ""), ("syok kan,", False, "SYOK"),
    ("kain dia", True, ""), ("sangat breathable.", True, ""),
    ("Haba dari dalam", False, "HABA"), ("kasut tu mudah", False, ""), ("nak keluar", False, "KELUAR"), ("macam ni.", False, ""),
    ("Korang pakai lama", False, ""), ("pun tak rasa", False, "TAK RASA"), ("panas kan.", False, "PANAS"),
    ("So nak start", True, ""), ("bersenam,", True, ""), ("brisk walk santai,", True, ""), ("ataupun jogging", True, ""), ("petang-petang tu,", True, ""),
    ("kasut Steapex", False, "STEAPEX"), ("Wind Spirit ni", False, "WIND SPIRIT"), ("memang sesuai", False, "SESUAI"), ("sangat untuk korang.", False, ""),
    ("Harga pun", True, ""), ("tengah murah", True, ""), ("sekarang ni.", True, ""),
    ("Sebelum korang", False, ""), ("terlepas promo ni,", False, "TERLEPAS PROMO"),
    ("better korang", True, ""), ("check out sekarang", True, ""), ("dekat beg kuning.", True, ""),
]

# ---- SFX cues -------------------------------------------------------------------------------------
SFX_LEN = {"whoosh": 0.45, "pop": 0.12, "ding": 1.0, "impact": 0.9, "cha_ching": 1.1, "riser": 1.5, "zap": 0.25}
SFX = [
    (0.02, "impact", 0.9), (0.30, "whoosh", 0.7), (1.45, "pop", 0.8), (2.05, "pop", 0.6), (3.62, "ding", 0.6),
    (4.70, "zap", 0.7), (4.90, "pop", 0.6),
    (7.95, "whoosh", 0.7), (10.85, "pop", 0.7),
    (12.90, "whoosh", 0.7),
    (15.05, "zap", 0.6), (15.20, "ding", 0.6), (17.40, "whoosh", 0.7), (17.75, "pop", 0.6),
    (20.05, "zap", 0.7), (21.30, "ding", 0.6), (24.35, "whoosh", 0.6),
    (27.05, "whoosh", 0.7), (27.88, "pop", 0.7), (28.35, "pop", 0.7), (29.50, "pop", 0.7),
    (32.15, "riser", 0.6), (33.62, "impact", 0.8), (34.42, "cha_ching", 0.8),
    (36.62, "pop", 0.7), (37.10, "pop", 0.8), (37.80, "zap", 0.5),
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
    # chunk display window: first word start -> next chunk start (capped at last word end + 0.3)
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
        if cid == "v01":  # square split-screen: blurred fill behind, sharp square on top
            return (f'<video id="v01bg" class="clip shot" src="assets/clips/v01_bg.mp4" data-start="{s}" data-duration="{d}" '
                    f'data-media-start="0" muted playsinline data-track-index="0"></video>\n      '
                    f'<video id="v01" class="clip sq" src="assets/clips/{f}" data-start="{s}" data-duration="{d}" '
                    f'data-media-start="0" data-volume="{FOOTAGE_VOL}" data-has-audio="true" data-track-index="1" playsinline></video>')
        return (f'<video id="{cid}" class="clip shot" src="assets/clips/{f}" data-start="{s}" data-duration="{d}" '
                f'data-media-start="0" data-volume="{FOOTAGE_VOL}" data-has-audio="true" data-track-index="{i}" playsinline></video>')
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
        "clips": [dict(id=c[0], file=c[1], start=c[2], duration=c[3], source=c[4]) for c in CLIPS],
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
      :root { --ground: #000; --ink: #fff; --yellow: #ffe100; --neon: #39ff14; --teal: #19d6c6;
              --font-display: "Anton", sans-serif; --font-label: "Montserrat", sans-serif; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }
      .clip { position: absolute; inset: 0; width: 1080px; height: 1920px; }
      video.shot { object-fit: cover; transform-origin: 50% 50%; }
      video.sq { top: 520px; height: 1080px; object-fit: cover; transform-origin: 50% 50%; }
      .flash { background: #fff; opacity: 0; }
      .display { font-family: var(--font-display); text-transform: uppercase; line-height: 0.95; color: #fff;
                 -webkit-text-stroke: {{12}} #000; paint-order: stroke fill; }
      .label { font-family: var(--font-label); font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
      .shade-top { position: absolute; left: 0; right: 0; top: 0; height: 900px;
                   background: linear-gradient(180deg, rgba(0,0,0,.72) 0%, rgba(0,0,0,.35) 55%, rgba(0,0,0,0) 100%); }
      .shade-bot { position: absolute; left: 0; right: 0; bottom: 0; height: 760px;
                   background: linear-gradient(0deg, rgba(0,0,0,.6) 0%, rgba(0,0,0,0) 100%); }

      /* HOOK */
      #hook .chip { position: absolute; top: 300px; left: 0; right: 0; text-align: center; }
      #hook .chip span { display: inline-block; background: #000; color: var(--yellow); padding: 10px 24px; border-radius: 999px;
                         font-size: {{42}}; border: 3px solid var(--yellow); }
      #hook .h { position: absolute; top: 368px; left: 120px; right: 120px; text-align: center; font-size: {{140}}; }
      #hook .h .y { color: var(--yellow); display: inline-block; }
      #hook .tag { position: absolute; top: 560px; padding: 8px 18px; border-radius: 12px; font-size: {{42}}; border: 3px solid #000; }
      #hook .tag.l { left: 140px; background: #d9d9d9; color: #000; }
      #hook .tag.r { left: 660px; background: var(--neon); color: #000; }
      #hook .mk { position: absolute; height: 0; border-top: 6px dashed #fff; transform-origin: 0 50%; }
      #hook .mk.l { left: 40px; width: 460px; top: 1213px; border-top-color: rgba(255,255,255,.9); }
      #hook .mk.r { left: 580px; width: 460px; top: 1131px; border-top: 8px solid var(--neon); }
      #hook .ring { position: absolute; left: 696px; top: 1071px; width: 120px; height: 120px; border-radius: 50%;
                    border: 8px solid var(--neon); opacity: 0; }
      #hook .up { position: absolute; left: 470px; top: 900px; width: 310px; text-align: left; }
      #hook .up .t { font-size: {{72}}; color: var(--neon); line-height: 1; }
      #hook .up .t2 { font-size: {{72}}; color: #fff; line-height: 1; }

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

      /* SPRING overlay */
      #spring svg { position: absolute; left: 780px; top: 860px; width: 150px; height: 240px; transform-origin: 50% 100%; }

      /* DISTANCE TRACKER */
      #track .card { position: absolute; left: 120px; width: 660px; top: 760px; background: rgba(0,0,0,.72);
                     border: 4px solid var(--neon); border-radius: 26px; padding: 22px 34px; }
      #track .top { display: flex; justify-content: space-between; align-items: baseline; }
      #track .lbl { color: #fff; font-size: {{42}}; }
      #track .val { font-family: var(--font-display); color: var(--neon); font-size: {{150}}; line-height: 1; }
      #track .val small { font-size: {{80}}; color: #fff; margin-left: 8px; }
      #track .bar { height: 22px; background: rgba(255,255,255,.18); border-radius: 12px; overflow: hidden; margin-top: 14px; }
      #track .bar i { display: block; height: 100%; width: 100%; background: linear-gradient(90deg, var(--teal), var(--neon));
                      transform-origin: 0 50%; transform: scaleX(0); }

      /* HEAT arrows */
      #heat .a { position: absolute; width: 70px; height: 70px; border-left: 14px solid #ff7a1a; border-top: 14px solid #ff7a1a;
                 transform: rotate(45deg); filter: drop-shadow(0 0 4px #000); opacity: 0; }

      /* ACTIVITY chips */
      #acts .list { position: absolute; top: 330px; left: 190px; display: flex; flex-direction: column; gap: 18px; }
      #acts .it { display: inline-flex; align-items: center; gap: 18px; background: rgba(0,0,0,.75); border: 4px solid var(--neon);
                  border-radius: 18px; padding: 10px 26px 6px 14px; font-size: {{96}}; align-self: flex-start; }
      #acts .it i { width: 58px; height: 58px; border-radius: 50%; background: var(--neon); display: inline-flex; align-items: center;
                    justify-content: center; font-style: normal; color: #000; font-family: var(--font-label); font-weight: 900;
                    font-size: 38px; -webkit-text-stroke: 0; margin-bottom: 4px; }

      /* CTA */
      #buy .box { position: absolute; top: 330px; left: 120px; right: 120px; text-align: center; }
      #buy .h1 { font-size: {{120}}; }
      #buy .stamp { display: inline-block; margin-top: 14px; background: var(--yellow); color: #000; -webkit-text-stroke: 0;
                    font-size: {{200}}; line-height: 1.05; padding: 8px 44px 4px; border: 8px solid #000; border-radius: 22px;
                    box-shadow: 10px 10px 0 #000; transform-origin: 50% 50%; }
      #buy .card { position: absolute; left: 120px; width: 660px; top: 800px; background: rgba(0,0,0,.8);
                   border: 5px solid var(--neon); border-radius: 28px; padding: 24px 30px; text-align: center; }
      #buy .pick { font-size: {{100}}; color: var(--neon); }
      #buy .line { font-family: var(--font-label); font-weight: 800; color: #fff; font-size: {{48}}; line-height: 1.3; margin-top: 10px;
                   display: flex; align-items: center; justify-content: center; gap: 12px; flex-wrap: wrap; }
      #buy .line .bagsvg { width: 56px; height: 56px; }
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
      <!-- FOOTAGE (10 clips, original sound 30%) -->
      __VIDEOS__

      <!-- VOICEOVER: original, 100%, uncut -->
      <audio id="vo" src="__VO__" data-start="0" data-duration="__VOLEN__" data-media-start="0" data-volume="1"></audio>

      <!-- HOOK 0-4.75 : ball drop comparison -->
      <div class="clip" id="hook" data-start="0" data-duration="4.75" data-track-index="11">
        <div class="shade-top"></div>
        <div class="chip"><span class="label">Ujian bola jatuh</span></div>
        <div class="display h" id="hh"><span id="hh1">Nampak tak</span> <span class="y" id="hh2">beza?</span></div>
        <div class="mk l" id="mkl"></div>
        <div class="mk r" id="mkr"></div>
        <div class="ring" id="hring"></div>
        <div class="tag l label" id="tagl">Kasut lain</div>
        <div class="tag r label" id="tagr">Steapex</div>
        <div class="up" id="hup"><div class="display t">Lantun</div><div class="display t2">lebih tinggi &uarr;</div></div>
      </div>

      <!-- FEATURE 1: 4.75-12.95 -->
      <div class="clip feat" id="f1" data-start="4.75" data-duration="8.2" data-track-index="12">
        <div class="shade-top"></div>
        <div class="dots"><i class="on"></i><i></i><i></i></div>
        <div class="box">
          <div class="chip label" id="f1chip">Ciri <b>#1</b></div>
          <div class="display title"><span id="f1t">Tapak responsif</span></div>
        </div>
      </div>
      <div class="clip" id="spring" data-start="10.4" data-duration="2.55" data-track-index="13">
        <svg id="spr" viewBox="0 0 60 100"><polyline points="30,0 30,8 6,16 54,26 6,36 54,46 6,56 54,66 6,76 54,86 30,92 30,100"
          fill="none" stroke="#39ff14" stroke-width="7" stroke-linejoin="round" stroke-linecap="round" style="filter:drop-shadow(0 0 3px #000)"/></svg>
      </div>

      <!-- FEATURE 2: 15.1-20.1 -->
      <div class="clip feat" id="f2" data-start="15.1" data-duration="5" data-track-index="12">
        <div class="shade-top"></div>
        <div class="dots"><i class="on"></i><i class="on"></i><i></i></div>
        <div class="box">
          <div class="chip label" id="f2chip">Ciri <b>#2</b></div>
          <div class="display title"><span id="f2t">Foam tebal</span></div>
          <div class="display sub" id="f2s">+ Serap hentakan</div>
        </div>
      </div>
      <div class="clip" id="track" data-start="17.45" data-duration="2.65" data-track-index="13">
        <div class="card" id="tcard">
          <div class="top"><div class="lbl label">Jarak</div><div class="val"><span id="tval">0.0</span><small>KM</small></div></div>
          <div class="bar"><i id="tbar"></i></div>
        </div>
      </div>

      <!-- FEATURE 3: 21.2-27.1 -->
      <div class="clip feat" id="f3" data-start="21.2" data-duration="5.9" data-track-index="12">
        <div class="shade-top"></div>
        <div class="dots"><i class="on"></i><i class="on"></i><i class="on"></i></div>
        <div class="box">
          <div class="chip label" id="f3chip">Ciri <b>#3</b></div>
          <div class="display title"><span id="f3t">Kain breathable</span></div>
        </div>
      </div>
      <div class="clip" id="heat" data-start="22.7" data-duration="2.5" data-track-index="13">
        <div class="a" id="ha1" style="left:700px;top:900px"></div>
        <div class="a" id="ha2" style="left:800px;top:960px"></div>
        <div class="a" id="ha3" style="left:900px;top:900px"></div>
      </div>

      <!-- LIFESTYLE 27.1-33.65 -->
      <div class="clip" id="acts" data-start="27.1" data-duration="6.55" data-track-index="12">
        <div class="shade-top"></div>
        <div class="list">
          <div class="it display" id="a1"><i>&check;</i>Bersenam</div>
          <div class="it display" id="a2"><i>&check;</i>Brisk walk</div>
          <div class="it display" id="a3"><i>&check;</i>Jogging petang</div>
        </div>
      </div>

      <!-- CTA 33.65-end -->
      <div class="clip" id="buy" data-start="33.65" data-duration="4.97" data-track-index="15">
        <div class="shade-top"></div>
        <div class="shade-bot"></div>
        <div class="box">
          <div class="display h1" id="bh1">Harga tengah</div>
          <div class="display stamp" id="bstamp">Murah!</div>
        </div>
        <div class="card" id="bcard">
          <div class="display pick">Check out sekarang</div>
          <div class="line">dekat <em>beg kuning</em> __BAG__</div>
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
      tl.fromTo("#hh1", { scale: 2.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "power4.in" }, 0.0);
      tl.fromTo("#hh2", { scale: 0, rotation: -10 }, { scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2.6)" }, 0.45);
      tl.fromTo("#hook .chip span", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3 }, 0.25);
      tl.fromTo("#mkl", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: "power2.out" }, 1.43);
      tl.fromTo("#mkr", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: "power2.out" }, 1.47);
      gsap.set("#hring", { opacity: 0 });
      tl.fromTo("#hring", { scale: 0.5, opacity: 1 }, { scale: 1.6, opacity: 0, duration: 0.5, immediateRender: false }, 1.47);
      tl.fromTo("#tagl", { y: -40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.25, ease: "back.out(2)" }, 2.0);
      tl.fromTo("#tagr", { y: -40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.25, ease: "back.out(2)" }, 2.05);
      tl.fromTo("#hup", { x: 60, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(2)" }, 3.6);
      tl.fromTo("#hring", { scale: 0.5, opacity: 1 }, { scale: 1.6, opacity: 0, duration: 0.5, immediateRender: false }, 3.9);

      // FEATURE TITLES
      [["f1", 4.75], ["f2", 15.1], ["f3", 21.2]].forEach(([id, t]) => {
        tl.fromTo(`#${id}chip`, { x: -260, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, t + 0.05);
        tl.fromTo(`#${id}t`, { yPercent: 105 }, { yPercent: 0, duration: 0.35, ease: "power3.out" }, t + 0.15);
        tl.fromTo(`#${id} .dots`, { opacity: 0 }, { opacity: 1, duration: 0.25 }, t);
      });
      tl.fromTo("#f2s", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 16.3);

      // SPRING
      tl.fromTo("#spr", { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(2)" }, 10.45);
      for (let k = 0; k < 4; k++) {
        tl.to("#spr", { scaleY: 0.55, duration: 0.18, ease: "power2.in" }, 10.8 + k * 0.5);
        tl.to("#spr", { scaleY: 1.1, duration: 0.2, ease: "back.out(3)" }, 10.98 + k * 0.5);
      }

      // DISTANCE TRACKER
      tl.fromTo("#tcard", { y: 80, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 17.6);
      const km = { v: 0 };
      tl.fromTo(km, { v: 0 }, { v: 10, duration: 1.4, ease: "power2.out",
        onUpdate: () => { document.getElementById("tval").textContent = km.v.toFixed(1); } }, 17.8);
      tl.fromTo("#tbar", { scaleX: 0 }, { scaleX: 1, duration: 1.4, ease: "power2.out" }, 17.8);

      // HEAT rising
      ["#ha1", "#ha2", "#ha3"].forEach((s, i) => {
        for (let k = 0; k < 2; k++) {
          const t = 22.8 + i * 0.25 + k * 1.1;
          tl.fromTo(s, { y: 0, opacity: 0 }, { y: -260, opacity: 1, duration: 0.5, ease: "none", immediateRender: k === 0 }, t);
          tl.to(s, { y: -360, opacity: 0, duration: 0.35, ease: "none" }, t + 0.5);
        }
      });

      // ACTIVITY chips
      [["#a1", 27.86], ["#a2", 28.33], ["#a3", 29.48]].forEach(([s, t]) => {
        tl.fromTo(s, { x: -60, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, t);
      });

      // CTA
      tl.fromTo("#bh1", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 33.75);
      tl.fromTo("#bstamp", { scale: 3, rotation: 0, opacity: 0 }, { scale: 1, rotation: -4, opacity: 1, duration: 0.3, ease: "power4.in" }, 34.12);
      tl.fromTo("#bcard", { y: 90, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 36.5);
      tl.fromTo("#bbag", { scale: 0, rotation: -20 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.4)" }, 37.05);
      for (let k = 0; k < 2; k++) {
        tl.to("#bbag", { y: -18, duration: 0.2, ease: "sine.out" }, 37.5 + k * 0.45);
        tl.to("#bbag", { y: 0, duration: 0.2, ease: "sine.in" }, 37.7 + k * 0.45);
      }
      gsap.set("#barr i", { opacity: 0 });
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 37.3);
      tl.to("#barr i", { opacity: 0.2, duration: 0.15, stagger: 0.1 }, 37.75);
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 38.2);

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
