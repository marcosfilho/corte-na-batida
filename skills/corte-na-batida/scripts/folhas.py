#!/usr/bin/env python3
"""Gera folhas de contato (miniaturas com o tempo escrito) para escolher os melhores momentos.

Visão geral (1 quadro por segundo):
    python3 folhas.py video.mov pasta_saida/
Zoom num trecho (para achar o frame exato do chute/arremesso), 10 quadros por segundo:
    python3 folhas.py video.mov pasta_saida/ --de 6.0 --ate 7.5 --fps 10
"""
import argparse, os, subprocess, sys, shutil, glob

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("saida")
ap.add_argument("--de", type=float, default=0.0); ap.add_argument("--ate", type=float, default=None)
ap.add_argument("--fps", type=float, default=1.0)
a = ap.parse_args()

ff = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
if not ff:
    try:
        import imageio_ffmpeg; ff = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("ffmpeg não encontrado")


def achar_fonte():
    for f in ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(f):
            return f
    achadas = glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
    return achadas[0] if achadas else None


os.makedirs(a.saida, exist_ok=True)
nome = os.path.splitext(os.path.basename(a.video))[0]
sufixo = f"_{a.de:g}-{a.ate:g}s" if a.ate else ""
out = os.path.join(a.saida, f"folha_{nome}{sufixo}.jpg")
fonte = achar_fonte()
rotulo = (f",drawtext=fontfile='{fonte}':text='%{{pts\\:flt\\:{a.de}}}':x=4:y=4:fontsize=22:"
          f"fontcolor=yellow:box=1:boxcolor=black@0.7") if fonte else ""
cols = 10 if a.fps <= 2 else 8
args = [ff, "-v", "error", "-y", "-ss", str(a.de)]
if a.ate:
    args += ["-t", str(a.ate - a.de)]
    linhas = max(1, -(-int(round((a.ate - a.de) * a.fps)) // cols))
else:
    linhas = 8
args += ["-i", a.video, "-vf", f"fps={a.fps},scale=200:-2{rotulo},tile={cols}x{linhas}", "-frames:v", "1", out]
subprocess.run(args, check=True)
print(out)
