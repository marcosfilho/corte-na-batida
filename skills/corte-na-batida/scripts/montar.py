#!/usr/bin/env python3
"""Renderiza a edição a partir de um plano JSON (gerado por gerar_plano.py).

Uso: python3 montar.py plano.json saida.mp4

Tipos de segmento (tempos no vídeo final, em segundos):
  [t0, t1, "preto"]                                  tela preta
  [t0, t1, "A", ss]                                  clipe A a partir do segundo ss
  [t0, t1, "A", ss, zoom]                            idem, com zoom (ex.: 1.3)
  [t0, t1, "A", ss, zoom, vel]                       idem, acelerado (ex.: 1.2 = 20% mais rápido)
  [t0, t1, "swipe", ["A", ss], ["B", ss], em, dur]   transição swipe suave de A para B
  [t0, t1, "final", "A", ss_impacto, {opções}]       congela no chute/arremesso e a imagem sai do ponto e cresce

Só precisa de Python 3 e ffmpeg. Se não houver ffmpeg no sistema, tenta o do pacote imageio-ffmpeg.
"""
import json, subprocess, sys, os, tempfile, math, shutil, struct


def achar_ffmpeg():
    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("ffmpeg não encontrado. Instale (brew install ffmpeg / apt install ffmpeg) "
                 "ou: pip install imageio-ffmpeg")


FFMPEG = achar_ffmpeg()


def tamanho_png(caminho):
    with open(caminho, "rb") as f:
        cab = f.read(24)
    if cab[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit(f"A imagem final precisa ser PNG (de preferência com fundo transparente): {caminho}")
    return struct.unpack(">II", cab[16:24])


plan = json.load(open(sys.argv[1])); out = sys.argv[2]
base = os.path.dirname(os.path.abspath(sys.argv[1]))
fps, W, H = plan.get("fps", 30), plan.get("w", 1080), plan.get("h", 1920)
P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
clips = {k: P(v) for k, v in plan["clips"].items()}
F = lambda t: round(t * fps)
tmp = tempfile.mkdtemp(prefix="corte_")
enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), "-an"]


def vf(zoom=1.0, vel=1.0):
    zw, zh = int(W * zoom) // 2 * 2, int(H * zoom) // 2 * 2
    sp = f"setpts=PTS/{vel}," if vel != 1.0 else ""
    return (f"{sp}scale={zw}:{zh}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},fps={fps},setsar=1")


def run(a):
    subprocess.run([FFMPEG, "-v", "error", "-y"] + a, check=True)


def clip(src, ss, n, path, zoom=1.0, vel=1.0):
    run(["-ss", f"{ss:.3f}", "-i", clips[src], "-vf", vf(zoom, vel), "-frames:v", str(n)] + enc + [path])


def preto(n, path):
    run(["-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={fps}", "-frames:v", str(n)] + enc + [path])


def swipe(a, b, em, dur, n, path):
    pa, pb = path + ".a.mp4", path + ".b.mp4"
    clip(a[0], a[1], F(em + dur), pa)
    clip(b[0], b[1], n - F(em), pb)
    run(["-i", pa, "-i", pb, "-filter_complex",
         f"[0:v][1:v]xfade=transition=smoothleft:duration={dur}:offset={em},fps={fps}",
         "-frames:v", str(n)] + enc + [path])


def final(src, ss, opt, n, path):
    """Congela o frame do impacto, treme a tela e faz a imagem sair do ponto e crescer até o centro."""
    fx, fy = opt.get("ponto", [0.8, 0.4])            # onde a imagem nasce (fração da tela: x, y)
    g = opt.get("crescer", 0.35)                      # tempo da imagem crescendo (s)
    w0, w1 = opt.get("largura_inicial", 0.06), opt.get("largura_final", 0.9)
    cy = opt.get("centro_y", 0.5); rot0 = opt.get("giro_graus", -35)
    tremor = opt.get("tremor_px", 22)
    img = P(opt["imagem"]); LW, LH = tamanho_png(img)
    d = path + "_img"; os.makedirs(d, exist_ok=True)
    fundo = os.path.join(d, "fundo.png")
    run(["-ss", f"{ss:.3f}", "-i", clips[src], "-vf", vf(1.0), "-frames:v", "1", fundo])
    ng = max(1, F(g))
    for i in range(ng + 1):                           # um PNG transparente por frame da animação
        p = min(i / ng, 1.0); e = 1 - (1 - p) ** 3     # ease-out
        lw = int(W * (w0 + (w1 - w0) * e)) // 2 * 2
        lh = max(2, int(lw * LH / LW) // 2 * 2)
        cx = W * (fx * (1 - e) + 0.5 * e); cyy = H * (fy * (1 - e) + cy * e)
        ang = rot0 * (1 - e) * math.pi / 180
        caixa = int(math.hypot(lw, lh)) // 2 * 2 + 4
        rot = f",rotate=a={ang:.4f}:c=none:ow={caixa}:oh={caixa}" if abs(ang) > 1e-3 else ""
        run(["-f", "lavfi", "-i", f"color=black@0.0:s={W}x{H},format=rgba", "-i", img,
             "-filter_complex",
             f"[1:v]format=rgba,scale={lw}:{lh}{rot}[l];"
             f"[0:v][l]overlay=x={cx:.1f}-w/2:y={cyy:.1f}-h/2:format=auto",
             "-frames:v", "1", os.path.join(d, f"l{i:03d}.png")])
    m = 1.06
    bg = (f"[0:v]scale={int(W*m)//2*2}:{int(H*m)//2*2},"
          f"crop={W}:{H}:x='(iw-{W})/2+{tremor}*sin(t*70)*exp(-t*5)':"
          f"y='(ih-{H})/2+{tremor}*cos(t*55)*exp(-t*5)'[bg]")
    run(["-loop", "1", "-framerate", str(fps), "-i", fundo,
         "-framerate", str(fps), "-i", os.path.join(d, "l%03d.png"),
         "-filter_complex", f"{bg};[bg][1:v]overlay=eof_action=repeat:format=auto,fps={fps}",
         "-frames:v", str(n)] + enc + [path])


partes = []
for k, s in enumerate(plan["segments"]):
    t0, t1, tipo = s[0], s[1], s[2]
    n = F(t1) - F(t0); p = os.path.join(tmp, f"{k:03d}.mp4")
    if tipo in ("preto", "black"):
        preto(n, p)
    elif tipo == "swipe":
        swipe(s[3], s[4], s[5], s[6], n, p)
    elif tipo in ("final", "kick"):
        final(s[3], s[4], s[5], n, p)
    else:
        clip(tipo, s[3], n, p, s[4] if len(s) > 4 else 1.0, s[5] if len(s) > 5 else 1.0)
    partes.append(p)
    print(f"  {k+1}/{len(plan['segments'])} {tipo} {t0:.2f}-{t1:.2f}s", flush=True)

lst = os.path.join(tmp, "lista.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in partes))
v = os.path.join(tmp, "video.mp4")
run(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", v])
musica = plan.get("music")
if musica:   # com áudio: versão para conferir
    run(["-i", v, "-i", P(musica), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
         "-b:a", "256k", "-t", str(plan["total"]), "-movflags", "+faststart", out])
else:        # sem áudio: a pessoa coloca o áudio do trend no Instagram ("Usar áudio")
    run(["-i", v, "-map", "0:v", "-c:v", "copy", "-t", str(plan["total"]), "-movflags", "+faststart", out])
shutil.rmtree(tmp, ignore_errors=True)
print("pronto:", out)
