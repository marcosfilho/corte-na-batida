#!/usr/bin/env python3
"""Transforma clipes.json (o que a pessoa gravou + os melhores momentos) no plano.json que o montar.py renderiza.

Uso: python3 gerar_plano.py clipes.json plano.json

A linha do tempo é fixa e casada com o áudio do trend (11,12 s). Ver LINHA_DO_TEMPO.md.

clipes.json:
{
  "musica": "audio_trend.m4a",          (opcional: sem isso o vídeo sai mudo, pronto para "Usar áudio" no Instagram)
  "close":       {"arquivo": "close.mov", "momentos": [12.4, 13.0, 13.6, 14.2, 14.6, 15.0, 15.4, 16.0]},
  "exercicios": [
    {"nome": "puxada", "arquivo": "ex1.mov", "momentos": [7.6, 11.5, 19.0, 29.5]},
    {"nome": "barra",  "arquivo": "ex2.mov", "momentos": [1.0, 4.6, 9.0, 10.2]},
    {"nome": "rosca",  "arquivo": "ex3.mov", "momentos": [1, 4, 7, 10, 13, 16, 19, 22]},
    {"nome": "remada", "arquivo": "ex4.mov", "momentos": [0.5, 2.2, 3.6, 5.0, 6.3, 7.6, 8.8, 5.3]}
  ],
  "final": {"arquivo": "final.mov", "impacto": 6.83, "ponto": [0.83, 0.39], "acelerar": 1.2},
  "imagem_final": {"arquivo": "strava.png", "largura_final": 0.62, "centro_y": 0.44}
}

"momentos" = segundos do clipe com boa execução e, de preferência, ângulos diferentes.
Se faltar momento, o script reaproveita os que existem com um pequeno deslocamento.
"""
import json, sys, os

c = json.load(open(sys.argv[1])); saida = sys.argv[2]
if len(c["exercicios"]) < 2:
    sys.exit("Precisa de pelo menos 2 exercícios (o ideal são 4).")
ex = c["exercicios"]
# com 2 ou 3 exercícios, repete os que existem para preencher as 4 posições
E = [ex[i % len(ex)] for i in range(4)]


class Fila:
    """Entrega os momentos em ordem; quando acabam, recomeça com +0,4 s para não repetir o mesmo frame."""
    def __init__(self, momentos):
        self.m = list(momentos) or [0.5]; self.i = 0
    def prox(self):
        v = self.m[self.i % len(self.m)] + 0.4 * (self.i // len(self.m)); self.i += 1
        return round(v, 3)


clips = {"C": c["close"]["arquivo"], "F": c["final"]["arquivo"]}
filas = {"C": Fila(c["close"]["momentos"])}
chaves, por_arquivo = [], {}
for i, e in enumerate(E):
    if e["arquivo"] in por_arquivo:   # mesmo exercício em duas posições: divide a fila e não repete momento
        k = por_arquivo[e["arquivo"]]
    else:
        k = f"E{i+1}"; clips[k] = e["arquivo"]; filas[k] = Fila(e["momentos"])
        por_arquivo[e["arquivo"]] = k
    chaves.append(k)
E1, E2, E3, E4 = chaves
q = lambda k: filas[k].prox()

seg = []
# 0,00–1,20  entrada: 2 closes rápidos + swipe para o exercício 1
seg += [[0.0, 0.14, "C", q("C"), 1.0], [0.14, 0.28, "C", q("C"), 1.25]]
seg += [[0.28, 1.2, "swipe", ["C", q("C")], [E1, q(E1)], 0.15, 0.3]]
seg += [[1.2, 2.0, "preto"]]                                    # silêncio no áudio
# 2,00–3,00  exercício 1 e 2 alternando, 6 cortes
for (t0, t1), k in zip([(2.0, 2.15), (2.15, 2.3), (2.3, 2.6), (2.6, 2.7), (2.7, 2.85), (2.85, 3.0)],
                       [E1, E2, E1, E2, E1, E2]):
    seg.append([t0, t1, k, q(k)])
seg += [[3.0, 3.8, "preto"]]                                    # silêncio no áudio
# 3,80–5,73  rajada: exercício 3 e 4 alternando, cortes de 4 frames
t, i = 3.8, 0
while t < 5.73 - 0.01:
    t1 = round(min(t + 0.1333, 5.73), 3); k = E3 if i % 2 == 0 else E4
    seg.append([round(t, 3), t1, k, q(k)]); t = t1; i += 1
# 5,73–6,53  três closes
seg += [[5.73, 6.0, "C", q("C"), 1.0], [6.0, 6.27, "C", q("C"), 1.3], [6.27, 6.53, "C", q("C"), 1.0]]
# 6,53–7,50  exercício 4 e 2 com mais tempo de tela
seg += [[6.53, 7.03, E4, q(E4)], [7.03, 7.5, E2, q(E2)]]
# 7,50–8,27  três closes
seg += [[7.5, 7.76, "C", q("C"), 1.0], [7.76, 8.02, "C", q("C"), 1.35], [8.02, 8.27, "C", q("C"), 1.15]]
# 8,27–9,42  cena final acelerada terminando exatamente no impacto (batida forte de 9,42 s)
f = c["final"]; vel = f.get("acelerar", 1.2); imp = f["impacto"]
ini = imp - (9.42 - 8.27) * vel
if ini < 0:
    print(f"aviso: o impacto em {imp}s é cedo demais; a cena final vai começar no 0 e ficar mais curta.")
    ini = 0.0
seg += [[8.27, 9.42, "F", round(ini, 3), 1.0, vel]]
# 9,42–11,12 congela no impacto e a imagem cresce
im = c["imagem_final"]
opt = {"imagem": im["arquivo"], "ponto": f.get("ponto", [0.8, 0.4]),
       "largura_final": im.get("largura_final", 0.9), "centro_y": im.get("centro_y", 0.5),
       "largura_inicial": im.get("largura_inicial", 0.06), "crescer": im.get("crescer", 0.35),
       "giro_graus": im.get("giro_graus", -35), "tremor_px": im.get("tremor_px", 22)}
seg += [[9.42, 11.12, "final", "F", imp, opt]]

plano = {"fps": 30, "w": 1080, "h": 1920, "music": c.get("musica"), "clips": clips,
         "segments": seg, "total": 11.12}
# caminhos relativos ao clipes.json continuam valendo se o plano ficar na mesma pasta
json.dump(plano, open(saida, "w"), indent=1, ensure_ascii=False)
print(f"plano com {len(seg)} segmentos salvo em {saida}")
