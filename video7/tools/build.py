"""Generate index.html for VO edit "travel take 2" (video7). Updated format (see ../video/FORMAT.md):
headline 100px, sub-headline 47px, caption 40px, small labels ~19px, ~70 MB render.

Run from video7/:  python3 tools/build.py
VO (assets/audio/vo.wav) is the original track: 100% volume, starts at 0, no cuts.
B-roll is used only in the heel/foot-pain part (4.1-10.1s).
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 60
FOOTAGE_VOL = 0.30                       # original footage sound at 30%
CLIP_VOL = {"g09": 0.08}                 # smoke spray hiss -> 8%
CLIP_ORIGIN = {"g02": "50% 70%", "g04": "50% 70%", "g06": "50% 70%"}
SFX_VOL = 0.30
VO_FILE = "assets/audio/vo.wav"
VO_LEN = 33.273
H1, H2, CAP = 100, 47, 40                # headline / sub-headline / caption px
S = 0.70 * 2 / 3                         # small labels ({{n}} tokens): ~19px for a 40 token

# ---- Edit decision list (10 clips) ---------------------------------------------------------------
CLIPS = [
    ("g01", "g01_jog.mp4", 0.00, 4.10, "lv_0_20251221233711 54.4-58.5 jogging on the spot, Emerald Green (intro, one shot)"),
    ("g02", "g02_tired.mp4", 4.10, 2.10, "B ROLL video_20251226_091215 0.8-2.9 runner bent over in pain (pain part)"),
    ("g03", "g03_massage.mp4", 6.20, 2.00, "B ROLL video_20260429_114700 0.3-2.3 massaging a sore foot (pain part)"),
    ("g04", "g04_tired2.mp4", 8.20, 1.90, "B ROLL video_20251226_091215 5.5-7.4 runner bent over (pain part)"),
    ("g05", "g05_foamblk.mp4", 10.10, 3.30, "lv_0_20251220180407 56.65-59.95 squeezing midsole foam, Black"),
    ("g06", "g06_step.mp4", 13.40, 3.70, "lv_0_20251209143405 43.2-46.9 stepping, Violet"),
    ("g07", "g07_bounce.mp4", 17.10, 2.90, "lv_0_20251221130556 64.8-67.7 shoe pressed and springing back up, Emerald Green"),
    ("g08", "g08_jump.mp4", 20.00, 3.40, "video_20260429_114829 40.5-43.9 hopping by the grass edge, Emerald Green"),
    ("g09", "g09_smoke.mp4", 23.40, 4.30, "lv_0_20251221130556 77.55-81.85 smoke through mesh, Emerald Green"),
    ("g10", "g10_cta.mp4", 27.70, 5.83, "lv_0_20251221233711 67.43-72.4 at 0.85x, pair on mat (CTA)"),
]
TOTAL = round(CLIPS[-1][2] + CLIPS[-1][3], 3)
CUTS = [c[2] for c in CLIPS[1:]]

# ---- Captions (phrase, hidden, keywords). hidden=True where a graphic already shows that clause ----------
CHUNKS = [
    ("Bila pergi travel,", True, ""), ("purata korang akan", True, ""), ("berjalan 10,000", True, ""), ("langkah setiap hari kan.", True, ""),
    ("So kalau salah", True, ""), ("pakai kasut,", True, ""),
    ("memang cepat", False, ""), ("sakit tumit", False, "SAKIT TUMIT"), ("macam ni.", False, ""),
    ("Nak pergi travel", False, "TRAVEL"), ("pun akan spoil tau,", False, "SPOIL"), ("memang tak ada", False, ""), ("mood nanti.", False, "MOOD"),
    ("Sebab tu", False, ""),
    ("kasut dengan", True, ""), ("foam tebal macam ni,", True, ""), ("sangat bagus untuk", True, ""), ("serap impak hentakan", True, ""),
    ("setiap kali", False, ""), ("korang pijak tau.", False, "PIJAK"),
    ("Tumit korang", False, "TUMIT"), ("memang tak pedih", False, "TAK PEDIH"), ("punya.", False, ""),
    ("Dan dia juga", True, ""), ("disokong dengan", True, ""), ("plate fleksibel macam ni.", True, ""),
    ("So setiap langkah", False, ""), ("korang tu akan", False, ""), ("jadi lebih", False, ""), ("stabil tau.", False, "STABIL"),
    ("Nak berjalan seharian", False, "SEHARIAN"), ("pun memang selesa", False, "SELESA"),
    ("sebab kain dia", True, ""), ("jenis breathable.", True, ""),
    ("Memang tak rasa", False, ""), ("berkuap langsung.", False, "BERKUAP"),
    ("Harga pun tengah", True, ""), ("murah tau sekarang.", True, ""),
    ("Sebelum terlepas", False, "TERLEPAS"), ("harga promo ni,", False, "PROMO"),
    ("korang pilih warna", True, ""), ("dan saiz kat beg", True, ""), ("kuning sekarang.", True, ""),
]

# ---- SFX cues -------------------------------------------------------------------------------------
SFX_LEN = {"whoosh": 0.45, "pop": 0.12, "ding": 1.0, "impact": 0.9, "cha_ching": 1.1, "riser": 1.5, "zap": 0.25}
SFX = [
    (0.02, "impact", 0.9), (0.30, "whoosh", 0.7), (1.80, "pop", 0.7), (2.95, "ding", 0.6),
    (4.05, "zap", 0.6), (4.20, "impact", 0.5), (4.60, "zap", 0.6), (6.15, "whoosh", 0.6), (6.50, "pop", 0.7), (8.15, "whoosh", 0.6),
    (10.05, "whoosh", 0.7), (10.90, "ding", 0.6), (13.35, "zap", 0.6),
    (17.05, "whoosh", 0.7), (17.30, "ding", 0.6), (19.45, "pop", 0.7), (19.95, "whoosh", 0.6),
    (23.35, "zap", 0.6), (23.50, "ding", 0.6),
    (26.20, "riser", 0.6), (27.68, "impact", 0.8), (28.50, "cha_ching", 0.8),
    (31.00, "pop", 0.6), (31.12, "pop", 0.7), (31.22, "pop", 0.7), (31.32, "pop", 0.7), (31.60, "pop", 0.8), (32.30, "zap", 0.5),
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
    for k, v in {"__TOTAL__": str(TOTAL), "__FPS__": str(FPS), "__VIDEOS__": videos, "__FLASHES__": flashes,
                 "__SFX__": sfx, "__CAPTIONS__": cap_html, "__ZOOM_JS__": zoom, "__FLASH_JS__": flash_js,
                 "__CAPTION_JS__": cap_js, "__VO__": VO_FILE, "__VOLEN__": str(VO_LEN), "__BAG__": BAG,
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


BAG = ('<svg class="bagsvg" viewBox="0 0 100 100"><path d="M32 34 V26 a18 18 0 0 1 36 0 V34" fill="none" stroke="#000" stroke-width="9" stroke-linecap="round"/>'
       '<path d="M14 32 H86 L80 92 H20 Z" fill="#ffe100" stroke="#000" stroke-width="6" stroke-linejoin="round"/>'
       '<path d="M38 52 a12 12 0 0 0 24 0" fill="none" stroke="#000" stroke-width="6" stroke-linecap="round"/></svg>')


def block(bid, start, dur, chip, dots, title, sub=""):
    d = "".join(f'<i class="{"on" if k < dots else ""}"></i>' for k in range(3))
    sub_html = f'<div class="display sub" id="{bid}s">{sub}</div>' if sub else ""
    return (f'<div class="clip feat" id="{bid}" data-start="{start}" data-duration="{dur}" data-track-index="12">\n'
            f'        <div class="shade-top"></div>\n        <div class="dots">{d}</div>\n        <div class="box">\n'
            f'          <div class="chip label" id="{bid}chip">{chip}</div>\n'
            f'          <div class="display title"><span id="{bid}t">{title}</span></div>\n          {sub_html}\n        </div>\n      </div>')


BLOCKS = "\n      ".join([
    block("f1", 10.1, 7.0, "Ciri <b>#1</b>", 1, "Foam tebal", sub="+ Serap hentakan"),
    block("f2", 17.1, 6.3, "Ciri <b>#2</b>", 2, "Plate flexible"),
    block("f3", 23.4, 4.3, "Ciri <b>#3</b>", 3, "Kain breathable"),
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
      .shade-top { position: absolute; left: 0; right: 0; top: 0; height: 900px;
                   background: linear-gradient(180deg, rgba(0,0,0,.7) 0%, rgba(0,0,0,.35) 55%, rgba(0,0,0,0) 100%); }
      .shade-bot { position: absolute; left: 0; right: 0; bottom: 0; height: 760px;
                   background: linear-gradient(0deg, rgba(0,0,0,.6) 0%, rgba(0,0,0,0) 100%); }

      /* HOOK */
      #hook .h { position: absolute; top: 330px; left: 120px; right: 120px; text-align: center; font-size: __H1__; }
      #hook .h .y { color: var(--yellow); }
      #hook .card { position: absolute; left: 240px; width: 600px; top: 470px; background: rgba(0,0,0,.75);
                    border: 3px solid var(--neon); border-radius: 18px; padding: 14px 24px; text-align: center; }
      #hook .lbl { color: #fff; font-size: {{40}}; }
      #hook .val { font-family: var(--font-display); color: var(--neon); font-size: __H1__; line-height: 1; margin-top: 4px; }
      #hook .val small { font-size: __H2__; color: #fff; margin-left: 8px; }
      #hook .bar { height: 14px; background: rgba(255,255,255,.18); border-radius: 8px; overflow: hidden; margin-top: 8px; }
      #hook .bar i { display: block; height: 100%; width: 100%; background: linear-gradient(90deg, var(--teal), var(--neon));
                     transform-origin: 0 50%; transform: scaleX(0); }

      /* PAIN */
      #pain .h { position: absolute; top: 330px; left: 120px; right: 120px; text-align: center; font-size: __H1__; }
      #pain .h .r { color: var(--red); }
      #pain .vig { position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(255,0,0,0) 45%, rgba(255,20,40,.55) 100%); opacity: 0; }
      #pain .xmark { position: absolute; left: 330px; top: 1440px; width: 400px; height: 400px; opacity: 0; }
      #pain .xmark svg { width: 100%; height: 100%; filter: drop-shadow(0 0 6px rgba(0,0,0,.7)); }
      #pain .ring { position: absolute; left: 160px; top: 1380px; width: 320px; height: 320px; border-radius: 50%;
                    border: 8px solid var(--red); opacity: 0; box-shadow: 0 0 20px rgba(255,45,61,.7); }

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

      /* HEAT arrows */
      #heat .a { position: absolute; width: 56px; height: 56px; border-left: 11px solid #ff7a1a; border-top: 11px solid #ff7a1a;
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

      /* CAPTIONS: Anton __CAP__, uppercase, black stroke, centre-bottom */
      .cap .capline { position: absolute; left: 120px; width: 840px; top: 1140px; display: flex; justify-content: center;
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

      <!-- HOOK 0-4.1 -->
      <div class="clip" id="hook" data-start="0" data-duration="4.1" data-track-index="11">
        <div class="shade-top"></div>
        <div class="display h"><span id="hh1">Bila pergi</span> <span class="y" id="hh2">travel</span></div>
        <div class="card" id="hcard">
          <div class="lbl label">Purata langkah setiap hari</div>
          <div class="val"><span id="hval">0</span><small>langkah</small></div>
          <div class="bar"><i id="hbar"></i></div>
        </div>
      </div>

      <!-- PAIN 4.1-10.1 (B-roll) -->
      <div class="clip" id="pain" data-start="4.1" data-duration="6" data-track-index="11">
        <div class="vig" id="pvig"></div>
        <div class="shade-top"></div>
        <div class="display h" id="ph"><span class="r">Salah</span> pakai<br />kasut?</div>
        <div class="xmark" id="px"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="44" fill="rgba(255,45,61,.18)" stroke="#ff2d3d" stroke-width="7"/>
          <path d="M30 30 L70 70 M70 30 L30 70" stroke="#ff2d3d" stroke-width="10" stroke-linecap="round"/></svg></div>
        <div class="ring" id="pring"></div>
      </div>

      <!-- FEATURE BLOCKS -->
      __BLOCKS__
      <div class="clip" id="heat" data-start="24.5" data-duration="3.2" data-track-index="13">
        <div class="a" id="ha1" style="left:700px;top:900px"></div>
        <div class="a" id="ha2" style="left:800px;top:960px"></div>
        <div class="a" id="ha3" style="left:900px;top:900px"></div>
      </div>

      <!-- CTA 27.7-end -->
      <div class="clip" id="buy" data-start="27.7" data-duration="5.83" data-track-index="15">
        <div class="shade-top"></div>
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
          <div class="line">kat <em>beg kuning</em> __BAG__ sekarang</div>
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
      tl.fromTo("#hh1", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "power4.in" }, 0.02);
      tl.fromTo("#hh2", { scale: 2.2, rotation: -8, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.28, ease: "power4.in" }, 0.45);
      tl.fromTo("#hcard", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, 1.0);
      const st = { v: 0 };
      tl.fromTo(st, { v: 0 }, { v: 10000, duration: 1.15, ease: "power2.out",
        onUpdate: () => { document.getElementById("hval").textContent = String(Math.round(st.v)).replace(/\B(?=(\d{3})+(?!\d))/g, ","); } }, 1.8);
      tl.fromTo("#hbar", { scaleX: 0 }, { scaleX: 1, duration: 1.15, ease: "power2.out" }, 1.8);
      tl.to("#hcard", { scale: 1.05, duration: 0.15, yoyo: true, repeat: 1, ease: "sine.inOut" }, 2.95);

      // PAIN
      gsap.set(["#pvig", "#px", "#pring"], { opacity: 0 });
      tl.fromTo("#ph", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.28, ease: "power4.in" }, 4.18);
      tl.fromTo("#px", { scale: 0, rotation: -40, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.3, ease: "back.out(2.2)", immediateRender: false }, 4.6);
      tl.to("#px", { opacity: 0, duration: 0.1 }, 6.1);
      [5.97, 8.31, 9.31].forEach((t) => {
        tl.fromTo("#pvig", { opacity: 0 }, { opacity: 1, duration: 0.15, immediateRender: false }, t);
        tl.to("#pvig", { opacity: 0, duration: 0.5 }, t + 0.15);
      });
      tl.fromTo("#pring", { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)", immediateRender: false }, 6.5);
      tl.to("#pring", { scale: 1.1, duration: 0.15, yoyo: true, repeat: 3 }, 6.8);
      tl.to("#pring", { opacity: 0, duration: 0.1 }, 8.1);

      // FEATURE TITLES
      [["f1", 10.1, 10.84], ["f2", 17.1, 17.22], ["f3", 23.4, 23.45]].forEach(([id, t, tt]) => {
        tl.fromTo(`#${id}chip`, { x: -200, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, tt - 0.1);
        tl.fromTo(`#${id}t`, { yPercent: 105 }, { yPercent: 0, duration: 0.35, ease: "power3.out" }, tt);
        tl.fromTo(`#${id} .dots`, { opacity: 0 }, { opacity: 1, duration: 0.25 }, t);
      });
      tl.fromTo("#f1s", { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 12.9);

      // HEAT rising
      ["#ha1", "#ha2", "#ha3"].forEach((s, i) => {
        for (let k = 0; k < 2; k++) {
          const t = 24.6 + i * 0.2 + k * 1.2;
          tl.fromTo(s, { y: 0, opacity: 0 }, { y: -240, opacity: 1, duration: 0.5, ease: "none", immediateRender: k === 0 }, t);
          tl.to(s, { y: -330, opacity: 0, duration: 0.35, ease: "none" }, t + 0.5);
        }
      });

      // CTA
      tl.fromTo("#bh1", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 27.8);
      tl.fromTo("#bstamp", { scale: 3, rotation: 0, opacity: 0 }, { scale: 1, rotation: -4, opacity: 1, duration: 0.3, ease: "power4.in" }, 28.2);
      tl.fromTo("#bcard", { y: 70, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 30.95);
      tl.fromTo("#bsw .tile", { scale: 0, rotation: -8 }, { scale: 1, rotation: 0, duration: 0.3, stagger: 0.1, ease: "back.out(2.6)" }, 31.1);
      [["#sw1", 32.0], ["#sw2", 32.3], ["#sw3", 32.6]].forEach(([s, t]) => {
        tl.to(s, { scale: 1.06, duration: 0.15, ease: "sine.out" }, t);
        tl.to(s, { scale: 1, duration: 0.15, ease: "sine.in" }, t + 0.15);
      });
      tl.fromTo("#bbag", { scale: 0, rotation: -20 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.4)" }, 31.6);
      for (let k = 0; k < 2; k++) {
        tl.to("#bbag", { y: -14, duration: 0.2, ease: "sine.out" }, 32.1 + k * 0.5);
        tl.to("#bbag", { y: 0, duration: 0.2, ease: "sine.in" }, 32.3 + k * 0.5);
      }
      gsap.set("#barr i", { opacity: 0 });
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 31.85);
      tl.to("#barr i", { opacity: 0.2, duration: 0.15, stagger: 0.1 }, 32.3);
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 32.75);

      // CAPTIONS (word timing from the VO; active word yellow, keywords neon green)
      __CAPTION_JS__

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
""".replace("__BLOCKS__", BLOCKS)

if __name__ == "__main__":
    build()
