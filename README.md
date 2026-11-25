# Corte na batida 🎬

Skill para **Claude** e **ChatGPT** que monta sozinha o Reel de academia "corte na batida". Você grava, joga os vídeos no chat e recebe o vídeo pronto, sem abrir o CapCut.

- Vários ângulos de 4 exercícios, cortados **no beat**
- **Telas pretas** com o áudio cortando junto
- Closes do seu rosto
- Final: você **chuta** (ou finge arremessar um peso) na câmera, a imagem **congela**, a tela treme e a sua imagem (Strava, logo, @) **sai do pé e cresce na tela**

Vertical 1080×1920, ~11 s, pronto para Reels e TikTok.

---

## 📱 Jeito mais fácil: template no Edits

Tudo no celular, sem instalar nada: grave os vídeos, tire um print do Strava e use o template no **Edits**, o app de edição do Instagram. A música e os cortes já vêm prontos.

👉 Passo a passo: [`TEMPLATE_EDITS.md`](TEMPLATE_EDITS.md)

---

## 🤖 Versão completa com IA (Claude ou ChatGPT)

Com a skill, a IA escolhe os melhores ângulos sozinha, faz a rajada de cortes e a imagem final **sai do pé e cresce na tela**.

## 1. Grave (5 minutos)

Peça para um amigo te filmar, com o celular em pé:

1. **4 exercícios**, 15–30 s cada. Você fica no lugar e o amigo **anda em volta** filmando de vários ângulos.
2. **1 close do seu rosto**, de 5–10 s.
3. **1 cena final**: você vem correndo na direção da câmera e **chuta uma bola imaginária**, ou **finge arremessar um peso** na câmera.

Separe também:

4. **A imagem do final** em PNG: print do Strava, a sua logo, o seu @…

**Não precisa baixar música.** O vídeo sai mudo, e você coloca o som na hora de postar (passo 4).

> **📱 Vai mandar pelo celular?** O Claude aceita até 30 MB por arquivo. Grave em **1080p 30fps** e corte cada vídeo para **10–15 s** no app Fotos antes de mandar. Assim cada um fica com 10–15 MB.

Guia completo: [`GRAVACAO.md`](skills/corte-na-batida/GRAVACAO.md)

## 2. Instale a skill

### Claude Code (computador)
```bash
git clone https://github.com/marcosfilho/corte-na-batida.git
cp -r corte-na-batida/skills/corte-na-batida ~/.claude/skills/
```
Precisa de **ffmpeg** (`brew install ffmpeg` no Mac, `sudo apt install ffmpeg` no Linux) e Python 3.

### Claude.ai / app do Claude
Compacte a pasta `skills/corte-na-batida` num `.zip` e envie em **Configurações → Capacidades → Skills**.

### ChatGPT
Siga [`chatgpt/COMO_USAR.md`](chatgpt/COMO_USAR.md): você cria um GPT, cola as instruções e sobe os scripts.

## 3. Use

Mande os vídeos e a imagem no chat e escreva:

> **Faz o corte na batida com esses vídeos. No final, usa essa imagem.**

O assistente olha os vídeos, escolhe os melhores momentos de cada ângulo, acha o frame do chute e te devolve o vídeo. Se quiser mudar algo, é só pedir: "menos cortes", "acelera a corrida", "imagem maior".

## 4. Poste com a música

1. No Instagram, abra o [Reel original do trend](https://www.instagram.com/reel/DfpNJX4hEu_/).
2. Toque no **nome do áudio** e depois em **"Usar áudio"**.
3. Escolha o seu vídeo. Ele já começa no tempo certo, então não mexa no início.
4. Poste. 🎵

A música é **"Class-Sikh Maut, Vol. II"**, de Prabh Deep, Seedhe Maut e Sez on the Beat. Usando o áudio pelo Instagram, a licença fica por conta da plataforma.

**Facebook:** ao postar no Instagram, ative **"Compartilhar no Facebook"**. O Reel vai junto, já com o áudio.

**TikTok:**
1. Procure um vídeo desse trend no TikTok e toque no **som** dele, depois em **"Usar este som"**. Assim vem a versão já cortada, com os silêncios.
2. Se não achar, procure a música **"Class-Sikh Maut Vol. II"** na biblioteca do TikTok. Ela vem inteira, sem os cortes de silêncio, então as telas pretas vão tocar com música. Ajuste o começo no botão de cortar o som até a batida encaixar.

Evite postar o vídeo já com a música colada: o TikTok e o Facebook podem silenciar o vídeo por direito autoral.

---

## Como funciona (para curiosos)

| Arquivo | O que faz |
|---|---|
| `scripts/folhas.py` | Cria miniaturas com o tempo para a IA "ver" os vídeos |
| `scripts/gerar_plano.py` | Encaixa os momentos escolhidos na linha do tempo do trend |
| `scripts/montar.py` | Renderiza tudo com ffmpeg: cortes, swipe, telas pretas, freeze, imagem crescendo |
| `scripts/card_resultado.py` | Cria um card com números (distância, ritmo, tempo…) se você não tiver imagem |
| `LINHA_DO_TEMPO.md` | Segundo a segundo do que entra onde |

Só precisa de Python 3 e ffmpeg, sem nenhuma biblioteca extra.

## Créditos

A edição foi inspirada no trend de um Reel original ([link](https://www.instagram.com/reel/DfpNJX4hEu_/)). A música é "Class-Sikh Maut, Vol. II", de Prabh Deep, Seedhe Maut e Sez on the Beat. Ela **não está neste repositório**: o som entra pelo "Usar áudio" do Instagram.
