---
name: transcribe-br
description: Transcreve vídeo em português a partir de link (Reels, TikTok, YouTube/Shorts, X, Facebook, Vimeo — tudo que o yt-dlp aceita) ou de arquivo local (gravação bruta, vídeo próprio), com Whisper rodando no computador e glossário de nomes da política brasileira. Gera texto e legenda .srt com horários. Use quando o usuário colar um link ou enviar um vídeo e pedir "transcreve", "o que ele fala", "tira o texto", "pega a fala", "legenda", ou precisar da fala exata de um vídeo para citar, roteirizar ou responder.
---

# Transcribe BR

Versão adaptada de `transcribe` (creator-skills, de Cristiano Capasso, licença MIT — ver `LICENSE-original`).

**O que mudou em relação ao original:**
- Português por padrão. O original detectava o idioma sozinho, o que falha em clipes curtos.
- Modelo `medium` por padrão (o original usava `small`): grafa melhor nomes próprios e falas rápidas.
- **Glossário** (`glossario.txt`) passado ao Whisper para acertar a grafia de nomes e siglas (Alesp, Tarcísio, TCE-SP…).
- Gera também `.srt` (com horários) e `.json`. Os horários servem para conferir citações e para a edição.
- Aceita **arquivo local**, não só link.
- `-y`: no YouTube, tenta primeiro a legenda oficial do canal (instantâneo).
- `-o`: guarda os arquivos numa pasta (no original tudo era apagado).
- Mensagens de instalação para Mac, Linux e Windows.

## Como rodar

```bash
"${CLAUDE_SKILL_DIR}/transcribe.sh" "<link-ou-arquivo>" [-m modelo] [-l idioma] [-o pasta] [-y] [-c navegador] [-G]
```

- `-m` — `tiny` | `base` | `small` | `medium` (padrão) | `large-v3`. Vídeo longo (> 10 min): use `small` ou `base` e avise o usuário do tempo.
- `-l` — `pt` (padrão), `en`, `es`… ou `auto`.
- `-o PASTA` — guarda `transcript.txt`, `transcript.srt`, `transcript.json` e `audio.mp3`. **Use sempre que a fala for ser citada ou editada.**
- `-y` — YouTube: legenda oficial primeiro; se não houver, Whisper. A legenda automática do YouTube não é usada.
- `-c chrome` (ou `safari`, `firefox`) — para conteúdo que exige login.
- `-G` — sem glossário. `-g ARQUIVO` — outro glossário.

Glossário pessoal: copie `glossario.txt` para `~/.config/transcricao-br/glossario.txt` e edite (tem prioridade).

## Como apresentar

1. Transcrição num bloco limpo.
2. Se for Reel ou Short, ofereça (sem fazer antes de perguntar): análise do gancho, estrutura, chamada final, ou passar para as skills `roteiro` / `video-breakdown-br`.
3. Se for vídeo longo, ofereça resumo, trechos com horário e citações.

## Cuidados obrigatórios

- **Transcrição automática erra.** Toda citação literal usada em vídeo, post ou documento precisa ser **conferida no áudio**, no horário indicado pelo `.srt`. Isso vale principalmente para falas de adversários e autoridades, porque citação errada pode gerar direito de resposta ou processo.
- O glossário melhora a grafia, mas pode **induzir** o Whisper a "ouvir" um termo da lista quando o som é parecido. Se aparecer um nome do glossário em lugar estranho, confira; se necessário, rode de novo com `-G`.
- Trechos com música alta, várias pessoas falando ou áudio ruim → use `-m large-v3` ou avise que a transcrição é parcial.
- Conteúdo privado ou de terceiros: transcrever para análise interna é uma coisa; republicar é outra (direito autoral).

## Falhas comuns

- **Privado ou com login** → `-c chrome`.
- **403 / SABR no YouTube** → yt-dlp desatualizado: `yt-dlp -U` ou `brew upgrade yt-dlp`.
- **Transcrição vazia** → vídeo sem fala (só música).
- **Idioma errado** → `-l` explícito.

## Requisitos

`yt-dlp`, `ffmpeg` e `whisper` (openai-whisper). O script mostra o comando de instalação do seu sistema se faltar algum. Na primeira vez, cada modelo é baixado (~1,5 GB o `medium`) e fica em `~/.cache/whisper/`.
