# Usar no ChatGPT

O ChatGPT roda Python e ffmpeg na própria "Análise de dados", então os mesmos scripts funcionam lá.

## Criar o GPT (uma vez só)

1. No ChatGPT, vá em **Explorar GPTs → Criar**, e depois na aba **Configurar**.
2. **Nome:** Corte na batida
3. **Instruções:** cole todo o conteúdo de [`INSTRUCOES_GPT.md`](INSTRUCOES_GPT.md).
4. **Conhecimento:** envie estes arquivos da pasta `skills/corte-na-batida/`:
   - `scripts/montar.py`
   - `scripts/gerar_plano.py`
   - `scripts/folhas.py`
   - `scripts/card_resultado.py`
   - `LINHA_DO_TEMPO.md`
   - `GRAVACAO.md`
5. **Recursos:** marque **Interpretador de código e análise de dados**.
6. Salve.

## Usar

Abra o GPT, envie os 6 vídeos e a imagem do final, e escreva: **"Faz o corte na batida"**.

**Atenção ao tamanho:** o ChatGPT aceita até ~512 MB por arquivo. Vídeos em 4K de 30 s passam disso, então grave em **1080p** ou exporte nessa resolução antes de enviar.
