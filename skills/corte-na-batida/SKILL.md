---
name: corte-na-batida
description: Monta automaticamente o Reel "corte na batida" de academia — vários ângulos de 4 exercícios cortados no beat, telas pretas com silêncio, closes do rosto e um final em que a pessoa chuta/arremessa e uma imagem (Strava, logo, @) sai do pé/mão e cresce na tela. Use quando alguém mandar os vídeos do treino e pedir "faz o corte na batida", "edita igual aquele trend", "faz a edição dos ângulos com a tela preta" ou parecido.
---

# Corte na batida

Edição vertical (1080×1920, 11,1 s) casada com o áudio do trend. A linha do tempo é fixa (ver `LINHA_DO_TEMPO.md`); o seu trabalho é **escolher os melhores momentos de cada clipe** e rodar os scripts.

Tudo roda com **Python 3 + ffmpeg**. Scripts em `scripts/`:

| Script | Para quê |
|---|---|
| `folhas.py` | Folhas de contato com o tempo escrito, para escolher momentos |
| `card_resultado.py` | (Opcional) Cria um card PNG com números, se a pessoa não tiver imagem pronta |
| `gerar_plano.py` | Transforma `clipes.json` no `plano.json` com a linha do tempo |
| `montar.py` | Renderiza o `plano.json` no vídeo final |

## O que a pessoa precisa mandar

1. **4 vídeos de exercício** (10–40 s cada). O ideal: alguém andando em volta, filmando de vários ângulos, a pessoa no mesmo lugar.
2. **1 close do rosto** (5–10 s): olhando para o lado, depois para a câmera.
3. **1 cena final**: vindo na direção da câmera e **chutando** uma bola imaginária, ou **fingindo arremessar** um peso/objeto na câmera.
4. **A imagem do final** em PNG (de preferência com fundo transparente): print/sticker do Strava, logo, @ do Instagram, qualquer coisa.
**Não precisa de música.** O vídeo sai **mudo** e a pessoa coloca o som na hora de postar, no próprio Instagram (passo 8). A música é "Class-Sikh Maut, Vol. II" (Prabh Deep, Seedhe Maut e Sez on the Beat), e o Instagram cuida da licença. Se a pessoa quiser conferir com som, ela pode mandar o Reel do trend salvo no celular, e aí você extrai o áudio dele (passo 1).

Se a pessoa disser que o arquivo é grande demais para enviar (o app do Claude aceita até 30 MB por arquivo), oriente: gravar em 1080p 30 fps e cortar cada vídeo para 10–15 s no app Fotos. Clipes curtos funcionam normalmente, porque a edição usa só ~2 s de cada exercício.

Se faltar algo, diga exatamente o que falta e mostre o `GRAVACAO.md`. Com 2 ou 3 exercícios funciona também (o script repete os que existem), mas avise que fica melhor com 4.

## Passo a passo

### 1. Áudio (opcional, só para conferir)
- Só se a pessoa mandou o Reel do trend: `ffmpeg -i reel.mp4 -vn -c:a pcm_s16le audio_trend.wav` e coloque `"musica": "audio_trend.wav"` no `clipes.json`.
- Confira: deve ter ~11,1 s e **silêncio em ~1,2–2,0 s e ~3,0–3,8 s** (`ffmpeg -i audio_trend.wav -af silencedetect=n=-45dB:d=0.3 -f null -`). Precisa ser o áudio **do Reel do trend** (já cortado com os silêncios), não a música inteira do Spotify.
- Sem áudio, simplesmente não coloque `"musica"`: o vídeo sai mudo.

### 2. Olhe os clipes
Para cada vídeo: `python3 scripts/folhas.py VIDEO pasta_folhas/` e **abra a imagem**. Vídeos de iPhone já saem em pé (o ffmpeg aplica a rotação).

### 3. Escolha os momentos (é aqui que a qualidade nasce)
Anote, em segundos, momentos com **boa execução visível** e **ângulos diferentes** entre si:
- **close**: 8–9 momentos (rosto nítido; alguns de perfil, um olhando para a câmera).
- **exercício 1**: 4 momentos · **exercício 2**: 4–5 · **exercício 3**: 8 · **exercício 4**: 8.
- Evite: gente passando na frente, câmera tremendo/borrada, a pessoa parada arrumando o aparelho, começo e fim do clipe.
- Ordem dos exercícios: o 1º abre o vídeo (logo depois do swipe) — use o mais bonito/fotogênico.

### 4. Ache o frame do impacto na cena final
- `python3 scripts/folhas.py FINAL pasta_folhas/ --de X --ate Y --fps 10` em volta do chute/arremesso.
- **impacto** = o segundo em que o pé (ou a mão) está no ponto máximo, logo antes de voltar.
- **ponto** = onde fica o pé/mão nesse frame, como fração da tela `[x, y]` (0,0 = canto superior esquerdo). Ex.: pé à direita, um pouco acima do meio → `[0.83, 0.39]`.
- O impacto precisa ter **pelo menos ~1,4 s de vídeo antes** (a corrida/aproximação).

### 5. Imagem final
- Se a pessoa mandou PNG, use direto. Confira se tem transparência; se for um print com fundo, avise que fica melhor recortado (ou com fundo transparente).
- Se ela só passou números: `python3 scripts/card_resultado.py card.png --linha "Distância|8,22 km" --linha "Ritmo|6:08 /km" --linha "Tempo|50m 24s" --rota --rodape "STRAVA"`.
- Logo horizontal (larga): `largura_final` 0.85–0.92. Card vertical (alto, tipo Strava): `largura_final` ~0.6 e `centro_y` ~0.44.

### 6. Gere e renderize
Escreva `clipes.json` (modelo em `exemplos/clipes_exemplo.json`):
```json
{
  "close": {"arquivo": "close.mov", "momentos": [14.2, 13.0, 15.4, 13.6, 14.6, 12.6, 16.0, 14.0, 15.0]},
  "exercicios": [
    {"nome": "puxada", "arquivo": "ex1.mov", "momentos": [7.6, 11.5, 19.0, 29.5]},
    {"nome": "barra",  "arquivo": "ex2.mov", "momentos": [1.0, 4.6, 9.0, 10.2]},
    {"nome": "rosca",  "arquivo": "ex3.mov", "momentos": [1, 4, 7, 10, 13, 16, 19, 22]},
    {"nome": "remada", "arquivo": "ex4.mov", "momentos": [0.5, 2.2, 3.6, 5.0, 6.3, 7.6, 8.8, 5.3]}
  ],
  "final": {"arquivo": "final.mov", "impacto": 6.83, "ponto": [0.83, 0.39], "acelerar": 1.2},
  "imagem_final": {"arquivo": "logo.png", "largura_final": 0.9, "centro_y": 0.5}
}
```
```bash
python3 scripts/gerar_plano.py clipes.json plano.json
python3 scripts/montar.py plano.json resultado.mp4
```
Caminhos relativos são relativos à pasta do JSON. Renderizar leva ~15–60 s.

### 7. Confira antes de entregar
Extraia frames com busca **precisa** (`-ss` depois do `-i`) em 0,1 · 0,6 · 2,2 · 4,0 · 5,0 · 6,8 · 8,8 · 10,9 s e olhe:
- todo plano mostra o exercício (nada de gente na frente, nada borrado);
- a corrida chega e o impacto cai em ~9,4 s;
- a imagem final está inteira na tela, legível e não cortada.
Depois entregue o arquivo e pergunte o que ajustar.

### 8. Diga como postar com a música
Sempre termine com estas instruções:
1. No Instagram, abra o Reel original do trend: https://www.instagram.com/reel/DfpNJX4hEu_/
2. Toque no **nome do áudio**, embaixo do Reel, e depois em **"Usar áudio"**.
3. Escolha o vídeo que eu te mandei. Ele começa junto com o áudio, então **não mexa no início**. As telas pretas caem nos silêncios da música.
4. Poste. A música é licenciada pelo próprio Instagram.

- **Facebook:** ao postar no Instagram, ative "Compartilhar no Facebook".
- **TikTok:** abra um vídeo desse trend no TikTok e toque no som dele, depois em "Usar este som". Se não achar, use "Class-Sikh Maut Vol. II" da biblioteca do TikTok e ajuste o começo cortando o som até a batida encaixar; nesse caso as telas pretas vão tocar com música.
- Não recomende postar com a música já colada no vídeo, porque a plataforma pode silenciar.

## Ajustes comuns (o que a pessoa costuma pedir)
- **"Muito movimento / não dá para ver o exercício"** → no `plano.json`, junte cortes vizinhos (menos planos, cada um mais longo) ou use menos momentos repetidos. Não troque de exercício a cada corte.
- **"A corrida está lenta"** → `"acelerar": 1.3` (ou 1.4).
- **"Começo parado"** → use closes mais variados nos 2 primeiros momentos do close.
- **Imagem pequena/grande ou mal posicionada** → `largura_final`, `centro_y`, `ponto`.
- **Quer outra imagem no final** → troque `imagem_final.arquivo` e rode de novo (só o final muda).

## Regras
- Não invente momentos sem olhar as folhas.
- Não suba nem distribua o áudio da música. Por padrão o vídeo sai mudo, e o som entra pelo "Usar áudio" do Instagram.
