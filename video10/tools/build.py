"""Generate index.html for "New VO" travel edit (video10). Updated format (../video/FORMAT.md):
headline 85px on one line (balanced wrap only if it cannot fit), sub-headline 47px, caption 40px at y=1450,
small labels ~19px, original footage framing (no close-up crops; brief zoom-in on each cut), ~70 MB render.

Run from video10/:  python3 tools/build.py
VO (assets/audio/vo.wav) is the original track: 100% volume, starts at 0, no cuts.
B-roll is used only in the heel-pain part (8.6-13.4s).
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 60
FOOTAGE_VOL = 0.30
CLIP_VOL = {"m08": 0.08, "m09": 0.08}   # smoke spray hiss -> 8%
CLIP_ORIGIN = {"m02": "50% 70%", "m07": "50% 70%"}
SFX_VOL = 0.30
VO_FILE = "assets/audio/vo.wav"
VO_LEN = 44.163
H1, H2, CAP, CAP_Y = 85, 47, 40, 1450
S = 0.70 * 2 / 3                         # small labels ({{n}} tokens): ~19px for a 40 token

# ---- Edit decision list (10 clips) ---------------------------------------------------------------
CLIPS = [
    ("m01", "m01_run.mp4", 0.00, 8.60, "video_20260429_114602 1.2-9.8 runner approaching on track, Emerald Green (intro, one shot, natural speed)"),
    ("m02", "m02_tired.mp4", 8.60, 2.50, "B ROLL video_20251226_091215 0.8-3.3 runner bent over in pain (pain part)"),
    ("m03", "m03_massage.mp4", 11.10, 2.30, "B ROLL video_20260429_114700 0.3-2.6 massaging a sore foot (pain part)"),
    ("m04", "m04_foam.mp4", 13.40, 4.63, "lv_0_20251220180407 56.6-60.3 at 0.8x, squeezing midsole foam, Black"),
    ("m05", "m05_bounce.mp4", 18.03, 3.80, "lv_0_20251221130556 64.8-68.6 shoe pressed and springing back up, Emerald Green"),
    ("m06", "m06_jump.mp4", 21.83, 4.00, "video_20260429_114829 40.5-44.5 hopping by the grass edge, Emerald Green"),
    ("m07", "m07_step.mp4", 25.83, 3.40, "lv_0_20251209143405 43.2-46.6 stepping, Violet"),
    ("m08", "m08_smoke.mp4", 29.23, 5.55, "lv_0_20251221130556 77.55-82.15 at 0.83x, smoke through mesh, Emerald Green"),
    ("m09", "m09_smokecu.mp4", 34.78, 2.70, "lv_0_20251221130556 82.2-84.9 smoke close-up, Emerald Green"),
    ("m10", "m10_cta.mp4", 37.48, 7.65, "lv_0_20251221233711 67.43-72.4 at 0.65x, pair on mat (CTA)"),
]
TOTAL = round(CLIPS[-1][2] + CLIPS[-1][3], 3)
CUTS = [c[2] for c in CLIPS[1:]]

# ---- Captions (phrase, hidden, keywords). hidden=True where a graphic already shows that clause ----------
CHUNKS = [
    ("Kalau tengah cari", True, ""), ("kasut selesa untuk", True, ""), ("pergi travel,", True, ""),
    ("korang kena tengok", True, ""), ("kasut Steapex ni.", True, ""),
    ("Sebab bila", False, ""), ("pergi travel,", False, "TRAVEL"),
    ("purata korang akan", True, ""), ("berjalan setiap hari", True, ""), ("lebih kurang", True, ""), ("10,000 langkah kan.", True, ""),
    ("So kalau salah", True, ""), ("pakai kasut,", True, ""),
    ("memang cepat", False, ""), ("sakit tumit", False, "SAKIT TUMIT"), ("korang tau.", False, ""),
    ("Paling teruk", False, "TERUK"), ("boleh jadi injury", False, "INJURY"), ("macam ni.", False, ""),
    ("Sebab tu kasut", False, ""), ("dengan foam tebal", True, ""), ("memang bagus untuk", True, ""), ("serap hentakan", True, ""),
    ("setiap kali", False, ""), ("korang pijak tu.", False, "PIJAK"),
    ("Dan dia juga", True, ""), ("disokong dengan", True, ""), ("plate fleksibel", True, ""), ("macam ni tau.", True, ""),
    ("So setiap langkah", False, ""), ("korang tu akan", False, ""), ("jadi lebih stabil", False, "STABIL"),
    ("especially bila", False, ""), ("korang pijak", False, ""), ("permukaan yang", False, ""), ("tak rata.", False, "TAK RATA"),
    ("Nak berjalan", False, ""), ("daripada pagi", False, "PAGI"), ("sampai ke malam", False, "MALAM"),
    ("pun memang", False, ""), ("selesa sangat", False, "SELESA"),
    ("sebab material", True, ""), ("kain dia ada", True, ""), ("ventilation tau.", True, ""),
    ("Memang tak rasa", False, ""), ("berkuap langsung.", False, "BERKUAP"),
    ("Korang nampak", False, ""), ("tak wap air tu", False, "WAP AIR"), ("senang nak keluar", False, "KELUAR"), ("macam ni kan.", False, ""),
    ("So haba panas", False, "HABA PANAS"), ("tu memang tak", False, ""), ("berkumpul kat dalam.", False, "BERKUMPUL"),
    ("Sekarang harga", True, ""), ("tengah murah tau.", True, ""),
    ("Rugi korang", False, "RUGI"), ("tak grab.", False, "GRAB"),
    ("Korang boleh", True, ""), ("pilih warna", True, ""), ("dan saiz kat beg", True, ""), ("kuning sekarang", True, ""),
    ("sebelum korang", False, ""), ("terlepas harga", False, "TERLEPAS"), ("promo ni.", False, "PROMO"),
]

# ---- SFX cues -------------------------------------------------------------------------------------
SFX_LEN = {"whoosh": 0.45, "pop": 0.12, "ding": 1.0, "impact": 0.9, "cha_ching": 1.1, "riser": 1.5, "zap": 0.25}
SFX = [
    (0.02, "impact", 0.9), (0.30, "whoosh", 0.7), (2.20, "pop", 0.7), (3.28, "ding", 0.6),
    (4.40, "pop", 0.7), (7.46, "ding", 0.6),
    (8.55, "zap", 0.6), (8.75, "impact", 0.5), (9.10, "zap", 0.6), (10.30, "pop", 0.7), (11.05, "whoosh", 0.6), (12.56, "impact", 0.5),
    (13.35, "whoosh", 0.7), (14.63, "ding", 0.6), (17.98, "zap", 0.6), (19.67, "ding", 0.6), (21.78, "whoosh", 0.7),
    (25.78, "whoosh", 0.6), (27.19, "pop", 0.7), (27.64, "pop", 0.7),
    (29.18, "zap", 0.6), (29.86, "ding", 0.6), (34.73, "whoosh", 0.6),
    (36.10, "riser", 0.6), (37.46, "impact", 0.8), (38.40, "cha_ching", 0.8), (39.14, "pop", 0.7),
    (40.30, "pop", 0.6), (40.42, "pop", 0.7), (40.52, "pop", 0.7), (40.62, "pop", 0.7), (41.0, "pop", 0.8), (44.35, "zap", 0.5),
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
        res.append((round(a, 3), round(min(b, TOTAL), 3), toks, hidden, kws))
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
                 "__H1__": f"{H1}px", "__H2__": f"{H2}px", "__CAP__": f"{CAP}px", "__CAPY__": f"{CAP_Y}px"}.items():
        html = html.replace(k, v)
    html = re.sub(r"\{\{(\d+(?:\.\d+)?)\}\}", lambda m: px(float(m.group(1))), html)
    (ROOT / "index.html").write_text(html)
    (ROOT / "edit-decision-list.json").write_text(json.dumps({
        "fps": FPS, "duration": TOTAL, "voiceover": {"file": VO_FILE, "start": 0, "volume": 1.0, "length": VO_LEN},
        "footage_volume": FOOTAGE_VOL, "sfx_volume": SFX_VOL, "headline_px": H1, "subheadline_px": H2,
        "caption_px": CAP, "caption_y": CAP_Y,
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
    block("f1", 13.4, 4.63, "Ciri <b>#1</b>", 1, "Foam tebal", sub="+ Serap hentakan"),
    block("f2", 18.03, 7.8, "Ciri <b>#2</b>", 2, "Plate flexible"),
    block("f3", 29.23, 8.25, "Ciri <b>#3</b>", 3, "Kain ada ventilation"),
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
                 -webkit-text-stroke: 6px #000; paint-order: stroke fill; text-wrap: balance; }
      .label { font-family: var(--font-label); font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
      .shade-top { position: absolute; left: 0; right: 0; top: 0; height: 900px;
                   background: linear-gradient(180deg, rgba(0,0,0,.7) 0%, rgba(0,0,0,.35) 55%, rgba(0,0,0,0) 100%); }

      /* HOOK + STEP COUNTER */
      #hook .chip { position: absolute; top: 300px; left: 120px; right: 120px; text-align: center; }
      #hook .chip span { display: inline-block; background: #000; color: var(--yellow); padding: 7px 16px; border-radius: 999px;
                         font-size: {{40}}; border: 2px solid var(--yellow); }
      #hook .h { position: absolute; top: 350px; left: 120px; right: 120px; text-align: center; font-size: __H1__; }
      #hook .h .y { color: var(--yellow); }
      #steps .card { position: absolute; left: 240px; width: 600px; top: 470px; background: rgba(0,0,0,.75);
                     border: 3px solid var(--neon); border-radius: 18px; padding: 14px 24px; text-align: center; }
      #steps .lbl { color: #fff; font-size: {{40}}; }
      #steps .val { font-family: var(--font-display); color: var(--neon); font-size: __H1__; line-height: 1; margin-top: 4px; }
      #steps .val small { font-size: __H2__; color: #fff; margin-left: 8px; }
      #steps .bar { height: 14px; background: rgba(255,255,255,.18); border-radius: 8px; overflow: hidden; margin-top: 8px; }
      #steps .bar i { display: block; height: 100%; width: 100%; background: linear-gradient(90deg, var(--teal), var(--neon));
                      transform-origin: 0 50%; transform: scaleX(0); }

      /* PAIN */
      #pain .h { position: absolute; top: 330px; left: 120px; right: 120px; text-align: center; font-size: __H1__; }
      #pain .h .r { color: var(--red); }
      #pain .vig { position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(255,0,0,0) 45%, rgba(255,20,40,.55) 100%); opacity: 0; }
      #pain .xmark { position: absolute; left: 330px; top: 1440px; width: 400px; height: 400px; opacity: 0; }
      #pain .xmark svg { width: 100%; height: 100%; filter: drop-shadow(0 0 6px rgba(0,0,0,.7)); }
      #pain .ring { position: absolute; left: 160px; top: 1380px; width: 320px; height: 320px; border-radius: 50%;
                    border: 8px solid var(--red); opacity: 0; box-shadow: 0 0 20px rgba(255,45,61,.7); }
      #pain .tag { position: absolute; left: 0; right: 0; top: 470px; text-align: center; }
      #pain .tag span { display: inline-block; background: var(--red); color: #fff; -webkit-text-stroke: 0; font-size: __H2__;
                        padding: 6px 20px 2px; border: 4px solid #000; border-radius: 12px; box-shadow: 5px 5px 0 #000; }

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

      /* SUN -> MOON */
      #day .track { position: absolute; left: 260px; top: 420px; width: 560px; height: 200px; border: 5px dashed rgba(255,255,255,.8);
                    border-bottom: none; border-radius: 300px 300px 0 0; opacity: 0; }
      #day .sun, #day .moon { position: absolute; width: 96px; height: 96px; border-radius: 50%; top: 572px; }
      #day .sun { left: 212px; background: radial-gradient(circle, #ffe100 55%, #ff9f1a 100%); box-shadow: 0 0 34px #ffb000; opacity: 0; }
      #day .moon { left: 772px; background: #f2f2ff; box-shadow: inset -22px 0 0 0 #c7c7e6, 0 0 26px #9aa0ff; opacity: 0; }
      #day .lb { position: absolute; top: 690px; font-size: __H2__; }
      #day .lb.p { left: 190px; color: var(--yellow); }
      #day .lb.m { left: 740px; color: #cfd3ff; }

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

      /* CAPTIONS: Anton __CAP__, uppercase, black stroke, centre-bottom at __CAPY__ */
      .cap .capline { position: absolute; left: 120px; width: 840px; top: __CAPY__; display: flex; justify-content: center;
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

      <!-- HOOK 0-8.6 (one shot) -->
      <div class="clip" id="hook" data-start="0" data-duration="8.6" data-track-index="11">
        <div class="shade-top"></div>
        <div class="chip"><span class="label" id="hchip">Cari kasut selesa untuk travel?</span></div>
        <div class="display h" id="hh"><span id="hh1">Tengok kasut</span> <span class="y" id="hh2">Steapex ni</span></div>
      </div>
      <div class="clip" id="steps" data-start="4.0" data-duration="4.6" data-track-index="12">
        <div class="card" id="scard">
          <div class="lbl label">Purata langkah setiap hari</div>
          <div class="val"><span id="sval">0</span><small>langkah</small></div>
          <div class="bar"><i id="sbar"></i></div>
        </div>
      </div>

      <!-- PAIN 8.6-13.4 (B-roll) -->
      <div class="clip" id="pain" data-start="8.6" data-duration="4.8" data-track-index="11">
        <div class="vig" id="pvig"></div>
        <div class="shade-top"></div>
        <div class="display h" id="ph"><span class="r">Salah</span> pakai kasut?</div>
        <div class="tag" id="ptag"><span class="display">Risiko injury!</span></div>
        <div class="xmark" id="px"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="44" fill="rgba(255,45,61,.18)" stroke="#ff2d3d" stroke-width="7"/>
          <path d="M30 30 L70 70 M70 30 L30 70" stroke="#ff2d3d" stroke-width="10" stroke-linecap="round"/></svg></div>
        <div class="ring" id="pring"></div>
      </div>

      <!-- FEATURE BLOCKS -->
      __BLOCKS__

      <!-- PAGI -> MALAM 25.83-29.23 -->
      <div class="clip" id="day" data-start="25.83" data-duration="3.4" data-track-index="12">
        <div class="shade-top"></div>
        <div class="track" id="dtrack"></div>
        <div class="sun" id="dsun"></div>
        <div class="moon" id="dmoon"></div>
        <div class="lb p display" id="dlp">Pagi</div>
        <div class="lb m display" id="dlm">Malam</div>
      </div>

      <div class="clip" id="heat" data-start="33.1" data-duration="4.38" data-track-index="13">
        <div class="a" id="ha1" style="left:700px;top:900px"></div>
        <div class="a" id="ha2" style="left:800px;top:960px"></div>
        <div class="a" id="ha3" style="left:900px;top:900px"></div>
      </div>

      <!-- CTA 37.48-end -->
      <div class="clip" id="buy" data-start="37.48" data-duration="7.65" data-track-index="15">
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
      tl.fromTo("#hchip", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3 }, 0.05);
      tl.fromTo("#hh1", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "power4.in" }, 2.2);
      tl.fromTo("#hh2", { scale: 2.2, rotation: -6, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.28, ease: "power4.in" }, 3.2);
      tl.to("#hh", { opacity: 0, y: -20, duration: 0.2 }, 3.95);

      // STEP COUNTER
      tl.fromTo("#scard", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, 4.1);
      const st = { v: 0 };
      tl.fromTo(st, { v: 0 }, { v: 10000, duration: 2.0, ease: "power2.out",
        onUpdate: () => { document.getElementById("sval").textContent = String(Math.round(st.v)).replace(/\B(?=(\d{3})+(?!\d))/g, ","); } }, 5.46);
      tl.fromTo("#sbar", { scaleX: 0 }, { scaleX: 1, duration: 2.0, ease: "power2.out" }, 5.46);
      tl.to("#scard", { scale: 1.05, duration: 0.15, yoyo: true, repeat: 1, ease: "sine.inOut" }, 7.46);

      // PAIN
      gsap.set(["#pvig", "#px", "#pring", "#ptag"], { opacity: 0 });
      tl.fromTo("#ph", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.28, ease: "power4.in" }, 8.7);
      tl.fromTo("#px", { scale: 0, rotation: -40, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.3, ease: "back.out(2.2)", immediateRender: false }, 9.1);
      tl.to("#px", { opacity: 0, duration: 0.1 }, 11.0);
      [10.3, 12.56].forEach((t) => {
        tl.fromTo("#pvig", { opacity: 0 }, { opacity: 1, duration: 0.15, immediateRender: false }, t);
        tl.to("#pvig", { opacity: 0, duration: 0.5 }, t + 0.15);
      });
      tl.fromTo("#ptag", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.4)", immediateRender: false }, 12.5);
      tl.fromTo("#pring", { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)", immediateRender: false }, 11.3);
      tl.to("#pring", { scale: 1.1, duration: 0.15, yoyo: true, repeat: 5 }, 11.6);

      // FEATURE TITLES
      [["f1", 13.4, 14.63], ["f2", 18.03, 19.67], ["f3", 29.23, 29.86]].forEach(([id, t, tt]) => {
        tl.fromTo(`#${id}chip`, { x: -200, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, tt - 0.1);
        tl.fromTo(`#${id}t`, { yPercent: 105 }, { yPercent: 0, duration: 0.35, ease: "power3.out" }, tt);
        tl.fromTo(`#${id} .dots`, { opacity: 0 }, { opacity: 1, duration: 0.25 }, t);
      });
      tl.fromTo("#f1s", { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, 15.73);

      // PAGI -> MALAM
      tl.fromTo("#dtrack", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 26.2);
      tl.fromTo(["#dsun", "#dlp"], { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)" }, 26.96);
      tl.to("#dsun", { x: 280, y: -150, duration: 0.25, ease: "sine.out" }, 27.25);
      tl.to("#dsun", { x: 560, y: 0, opacity: 0, duration: 0.25, ease: "sine.in" }, 27.5);
      tl.fromTo(["#dmoon", "#dlm"], { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)" }, 27.64);

      // HEAT rising (wap air keluar)
      ["#ha1", "#ha2", "#ha3"].forEach((q, i) => {
        for (let k = 0; k < 3; k++) {
          const t = 33.2 + i * 0.2 + k * 1.3;
          tl.fromTo(q, { y: 0, opacity: 0 }, { y: -240, opacity: 1, duration: 0.5, ease: "none", immediateRender: k === 0 }, t);
          tl.to(q, { y: -330, opacity: 0, duration: 0.35, ease: "none" }, t + 0.5);
        }
      });

      // CTA
      tl.fromTo("#bh1", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 37.7);
      tl.fromTo("#bstamp", { scale: 3, rotation: 0, opacity: 0 }, { scale: 1, rotation: -4, opacity: 1, duration: 0.3, ease: "power4.in" }, 38.1);
      tl.fromTo("#bcard", { y: 70, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 40.3);
      tl.fromTo("#bsw .tile", { scale: 0, rotation: -8 }, { scale: 1, rotation: 0, duration: 0.3, stagger: 0.1, ease: "back.out(2.6)" }, 40.4);
      [["#sw1", 41.03], ["#sw2", 41.33], ["#sw3", 41.63]].forEach(([q, t]) => {
        tl.to(q, { scale: 1.06, duration: 0.15, ease: "sine.out" }, t);
        tl.to(q, { scale: 1, duration: 0.15, ease: "sine.in" }, t + 0.15);
      });
      tl.fromTo("#bbag", { scale: 0, rotation: -20 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.4)" }, 41.81);
      for (let k = 0; k < 3; k++) {
        tl.to("#bbag", { y: -14, duration: 0.2, ease: "sine.out" }, 42.3 + k * 0.5);
        tl.to("#bbag", { y: 0, duration: 0.2, ease: "sine.in" }, 42.5 + k * 0.5);
      }
      for (let k = 0; k < 2; k++) {
        tl.to("#bbag", { y: -14, duration: 0.2, ease: "sine.out" }, 44.0 + k * 0.5);
        tl.to("#bbag", { y: 0, duration: 0.2, ease: "sine.in" }, 44.2 + k * 0.5);
      }
      gsap.set("#barr i", { opacity: 0 });
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 42.05);
      tl.to("#barr i", { opacity: 0.2, duration: 0.15, stagger: 0.1 }, 42.5);
      tl.to("#barr i", { opacity: 1, duration: 0.15, stagger: 0.1 }, 42.95);

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
