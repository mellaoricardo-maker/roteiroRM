---
name: video-breakdown-br
description: Disseca um vídeo (link de Reels, TikTok, YouTube/Shorts, X, Vimeo ou arquivo local) em imagem e fala, para estudar gancho, ritmo de edição e estrutura. Gera ficha técnica (duração, vertical/horizontal, cortes por minuto, plano médio, palavras por segundo), quadros dos 3 primeiros segundos, folhas de contato, lista de cortes com horário e transcrição em português com horários. Use quando o usuário colar um vídeo e pedir "analisa esse vídeo", "como ele editou", "disseca", "o que acontece na tela", "por que esse Reel funcionou", "ritmo dos cortes", "decupagem", ou quiser modelar a edição de uma referência ou revisar um vídeo próprio antes de publicar.
---

# Video Breakdown BR

Versão adaptada de `video-breakdown` (creator-skills, de Cristiano Capasso, licença MIT — ver `LICENSE-original`).

**O que mudou em relação ao original:**
- Português por padrão, modelo `medium`, glossário de nomes da política brasileira (igual à `transcribe-br`).
- Aceita **arquivo local** (ex.: revisar o próprio vídeo antes de postar).
- **fps automático** pela duração: 2 (até 60 s), 1 (até 3 min), 0,5 (mais longo).
- **`gancho/`**: os 3 primeiros segundos a cada 0,25 s, porque é onde se decide se a pessoa fica.
- **`cortes.txt`** e **ritmo**: horário de cada corte detectado, cortes por minuto e duração média do plano.
- **`info.txt`**: duração, resolução, vertical/horizontal, palavras por segundo.
- Mensagens de instalação para Mac, Linux e Windows.

## Como rodar

```bash
"${CLAUDE_SKILL_DIR}/breakdown.sh" "<link-ou-arquivo>" [-o pasta] [-f fps] [-m modelo] [-l idioma] [-s limiar] [-T] [-c navegador]
```

| Opção | Padrão | Quando mudar |
|---|---|---|
| `-o` | `./video-breakdown-<data-hora>` | Sempre que quiser guardar num lugar conhecido |
| `-f` | automático | `2`–`4` para edição muito rápida |
| `-m` | `medium` | `small` em vídeo longo |
| `-l` | `pt` | Vídeo estrangeiro: `en`, `es`, ou `auto` |
| `-s` | `0.3` | **`0.06` para pessoa falando com o mesmo fundo** (cortes secos quase não mudam a imagem) |
| `-T` | — | Só a parte visual, sem transcrição |
| `-c` | — | Conteúdo com login: `chrome`, `safari`, `firefox` |

## Como analisar (ordem)

1. **`info.txt`** — formato, duração e ritmo em números.
2. **`gancho/`** — o que aparece e o que é dito nos 3 primeiros segundos: rosto, texto na tela, movimento, primeira frase (`transcript.srt`).
3. **`sheets/`** — visão geral da sequência: mudanças de cenário, prints e documentos na tela, B-roll, legendas.
4. **`cortes.txt` + `transcript.srt`** — alinhar cada corte com a fala: corta a cada frase? a cada ideia? Onde estão as retomadas de atenção?
5. **`frames/`** — detalhe de um momento específico.

Entregue a análise em tópicos curtos:
- **Gancho:** imagem, texto na tela e frase de abertura, e por que segura.
- **Estrutura:** blocos com horário (gancho → contexto → prova → virada → fechamento/chamada).
- **Edição:** cortes por minuto, plano médio, tipos de recurso visual (zoom, print, legenda, B-roll), como a legenda é usada.
- **Fala:** palavras por segundo (referência: ~2,5 é ritmo de Reel acelerado; abaixo de 2 tende a parecer lento).
- **O que copiar e o que não copiar** para o estilo do usuário. Se houver a skill `videomaker`, use o padrão dela como comparação.

## Limites dos números (diga isso ao usuário quando relevante)

- **Detecção de cortes é aproximada.** Mede mudança de imagem, não decisão de edição. Em teste com imagem sintética, um corte seco com zoom de 10%, 20% e 40% na mesma cena marcou 0,07, 0,13 e 0,26 — ou seja, **o padrão `0.3` não pega cortes secos de pessoa falando**, e mesmo `0.06` pode perder corte sem zoom. No sentido oposto, limiar baixo gera **falso corte** com movimento de câmera, flash ou legenda grande (cortes a menos de 0,25 s um do outro já são descartados). Confira nas folhas de contato antes de afirmar um número de cortes.
- **Palavras por segundo** vem da transcrição automática e da duração total (inclui silêncios e trechos sem fala).
- Transcrição automática erra: citação literal precisa ser conferida no áudio (ver `transcribe-br`).
- Analisar vídeo de terceiros para estudo é uma coisa; republicar trechos é outra (direito autoral).

## Saída

```
<pasta>/
  info.txt  video.mp4  audio.mp3  transcript.txt  transcript.srt  transcript.json
  cortes.txt  gancho/gancho_01..12.jpg  frames/frame_0001.jpg…  sheets/sheet_001.png…
```

## Requisitos

`yt-dlp` (só para links), `ffmpeg`/`ffprobe` e `whisper` (openai-whisper; dispensável com `-T`). O script mostra o comando de instalação do seu sistema se faltar algum.
