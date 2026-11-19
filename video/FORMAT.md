# Format Video (dikunci) — rujukan untuk video seterusnya

Format ini diluluskan pada video "3 Ciri Kasut Jogging Padu". Gunakan semula untuk video produk lain.
Semua masa, teks dan SFX dijana dari satu fail: `tools/build.py` → `index.html`.

## Asas
- 1080×1920 menegak, 60fps, dibina dengan Hyperframes (`hyperframes render --fps 60 --quality delivery`).
- Tiada muzik latar.
- Voiceover asal (jika ada): volume 100%, tiada potongan, caption ikut masa VO. Jika tiada VO → caption ikut skrip.
- Bunyi asal footage 30% (`data-volume="0.3"`). Footage yang ada muzik → dimatikan.

## Struktur (±34s, maksimum 10 klip)
| Blok | Masa | Isi |
|---|---|---|
| Hook | 0–4s | Satu shot sahaja, laju asal. Nombor besar hijau neon + tajuk Anton, "PADU"-style kata kuning bergaris |
| Ciri #1–#3 | ~4–27s | Chip "CIRI #n" + tajuk + bar progres 3 titik. Setiap ciri guna footage sebenar sebagai bukti (picit foam, ujian bola jatuh, lentur tapak, penimbang, ujian asap, lari) |
| USP | ~3s | Chip "BONUS" + tajuk 2 baris (baris kedua hijau neon) + pil sub-teks Montserrat |
| CTA | ~4s, hujung | "HARGA TENGAH" + stamp kuning "MURAH!" + kad "PILIH WARNA" (swatch warna) + "dekat beg kuning 🛍 bawah sekarang" + ikon beg kuning melantun & anak panah ke bawah |

- Setiap klip: zoom masuk ringkas (1.00→1.07 dalam 0.45s, kemudian perlahan ke 1.11) + kilatan putih pada setiap potongan.
- Klip selain intro boleh diperlahankan (cth. 0.8x) jika shot terlalu pendek untuk teks dibaca.

## Teks
- Anton = tajuk & caption; Montserrat = label. Saiz grafik = 70% saiz asal (token `{{n}}` dalam build.py darab 0.70).
- Caption: Anton 60px, huruf besar, stroke hitam, 2–3 perkataan setiap kali, tengah bawah (y≈1140, dalam safe-zone TikTok/Reels/Shorts).
  Perkataan aktif kuning (#ffe100), kata kunci hijau neon (#39ff14).
- Tak bertindih: jika grafik dah tunjuk ayat/klausa sama, caption klausa itu disembunyikan.
- Semua teks dalam safe-zone gabungan: y 290–1248, x 120–960 (bawah y 840: x 120–780).

## Sound effect
- Disintesis sendiri (`tools/make_sfx.py`): whoosh, pop, ding, impact, cha-ching, riser, zap.
- Volume rendah (`SFX_VOL = 0.32`, puncak ≈ −11 hingga −17 dBFS), di bawah VO.
- Corak: impact pada hook, whoosh/zap pada potongan, ding pada tajuk ciri, pop pada caption/lencana,
  riser → impact sebelum USP, cha-ching pada "MURAH!".

## Semakan sebelum hantar
1. `hyperframes check` lulus (tiada amaran safe-zone/overlap/overflow).
2. Snapshot setiap babak + frame akhir setiap blok grafik (terutama CTA) — semak pada fail render sebenar.
3. VO selari dengan asal (jika ada); bunyi footage disahkan −10.5 dB (= 30%) dengan `volumedetect`.
