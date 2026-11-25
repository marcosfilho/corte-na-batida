#!/usr/bin/env python3
"""Cria um card PNG transparente com números (estilo resumo de treino/corrida) para a imagem final.

Exemplos:
  python3 card_resultado.py card.png --linha "Distância|8,22 km" --linha "Ritmo|6:08 /km" \
      --linha "Tempo|50m 24s" --rota --rodape "STRAVA"
  python3 card_resultado.py card.png --linha "Supino|100 kg" --linha "Séries|5x5" --rodape "@seuarroba"

--rota desenha um traçado vermelho de corrida (decorativo). Sem --rota, o card fica só com texto.
Se você já tem a imagem (print do app, sticker do Strava, logo), não precisa deste script: use o PNG direto.
"""
import argparse, subprocess, os, glob, shutil, sys, math

ap = argparse.ArgumentParser()
ap.add_argument("saida")
ap.add_argument("--linha", action="append", default=[], help='"Rótulo|Valor" (repita até 4 vezes)')
ap.add_argument("--rodape", default="")
ap.add_argument("--rota", action="store_true")
ap.add_argument("--cor", default="0xF5EFE0"); ap.add_argument("--cor-rota", default="0xE5231B")
a = ap.parse_args()

ff = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
if not ff:
    try:
        import imageio_ffmpeg; ff = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("ffmpeg não encontrado")


def fonte(negrito=True):
    cands = (["/System/Library/Fonts/Avenir Next.ttc", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]
             if negrito else
             ["/System/Library/Fonts/Supplemental/Arial Black.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "C:/Windows/Fonts/ariblk.ttf"])
    for f in cands:
        if os.path.exists(f):
            return f
    g = glob.glob("/usr/share/fonts/**/*Bold*.ttf", recursive=True)
    return g[0] if g else None


F1, F2 = fonte(True), fonte(False)
esc = lambda s: s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "").replace("%", "\\%")
W = 800
linhas = [l.split("|", 1) if "|" in l else ["", l] for l in a.linha][:4]
H = 60 + 260 * len(linhas) + (520 if a.rota else 0) + (110 if a.rodape else 0)
som = ":shadowcolor=black@0.55:shadowx=3:shadowy=3"
f = []
y = 40
for rot, val in linhas:
    if rot:
        f.append(f"drawtext=fontfile='{F1}':text='{esc(rot)}':fontcolor={a.cor}:fontsize=44{som}:x=(w-text_w)/2:y={y}")
    f.append(f"drawtext=fontfile='{F1}':text='{esc(val)}':fontcolor={a.cor}:fontsize=118{som}:x=(w-text_w)/2:y={y+62}")
    y += 260
mascara = []
if a.rota:
    pts = [(100,450),(150,500),(195,545),(205,570),(250,552),(320,545),(310,610),(270,640),(225,660),(205,680),(212,640),(205,570)]
    pts = [(x*1.6 + 90, (yy-440)*1.6 + y + 20) for x, yy in pts]
    vistos = set()
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = int(math.hypot(x1-x0, y1-y0) / 5) + 1
        for i in range(n + 1):
            x = int(x0 + (x1-x0)*i/n); yy = int(y0 + (y1-y0)*i/n)
            if (x, yy) not in vistos:
                vistos.add((x, yy)); mascara.append(f"drawbox=x={x-8}:y={yy-8}:w=16:h=16:color=white:t=fill")
if a.rodape:
    f.append(f"drawtext=fontfile='{F2}':text='{esc(a.rodape)}':fontcolor={a.cor}:fontsize=54{som}:x=(w-text_w)/2:y={H-90}")

base = f"color=black@0.0:s={W}x{H},format=rgba"
if mascara:
    g = (f"[0]{','.join(f) or 'null'}[t];[1]{','.join(mascara)},format=gray[m];"
         f"[2][m]alphamerge[r];[t][r]overlay=format=auto")
    ins = ["-f", "lavfi", "-i", base, "-f", "lavfi", "-i", f"color=black:s={W}x{H}",
           "-f", "lavfi", "-i", f"color={a.cor_rota}:s={W}x{H},format=rgba"]
else:
    g = f"[0]{','.join(f) or 'null'}"
    ins = ["-f", "lavfi", "-i", base]
subprocess.run([ff, "-v", "error", "-y"] + ins + ["-filter_complex", g, "-frames:v", "1", a.saida], check=True)
print("pronto:", a.saida)
