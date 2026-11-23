#!/bin/bash
# transcribe-br — transcreve um link de vídeo (Reels, TikTok, YouTube/Shorts, X, …)
# ou um arquivo local, com Whisper rodando no próprio computador.
#
# Baseado em `transcribe` de creator-skills (c) 2026 Cristiano Capasso, MIT
# (ver LICENSE-original). Mudanças: português como padrão, glossário de nomes
# próprios, legenda .srt com horários, entrada por arquivo local, opção de usar
# a legenda oficial do YouTube, pasta de saída opcional, instalação fora do Mac.
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Uso: transcribe.sh <link-ou-arquivo> [opções]

  -m MODELO    tiny | base | small | medium | large-v3      (padrão: medium)
  -l IDIOMA    pt, en, es… ou "auto"                        (padrão: pt)
  -o PASTA     guarda transcript.txt, transcript.srt e audio.mp3 nessa pasta
               (sem -o, os arquivos temporários são apagados ao final)
  -g ARQUIVO   glossário de nomes próprios (padrão: ~/.config/transcricao-br/glossario.txt
               ou glossario.txt da skill)
  -G           não usar glossário
  -y           YouTube: tentar primeiro a legenda oficial em português (rápido,
               sem Whisper); se não houver, cai no Whisper
  -c NAVEGADOR usar cookies do navegador (chrome, safari, firefox) para conteúdo
               que exige login

Saída: a transcrição em texto vai para a saída padrão.
USAGE
  exit 1
}

[ $# -lt 1 ] && usage
SRC="$1"; shift
MODEL="medium"; LANG_OPT="pt"; OUTDIR=""; GLOSS=""; NO_GLOSS=0; YT_SUBS=0; COOKIES=""
while getopts "m:l:o:g:Gyc:h" opt; do
  case "$opt" in
    m) MODEL="$OPTARG" ;;
    l) LANG_OPT="$OPTARG" ;;
    o) OUTDIR="$OPTARG" ;;
    g) GLOSS="$OPTARG" ;;
    G) NO_GLOSS=1 ;;
    y) YT_SUBS=1 ;;
    c) COOKIES="$OPTARG" ;;
    *) usage ;;
  esac
done

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install_hint() {
  case "$(uname -s)" in
    Darwin) echo "  brew install yt-dlp ffmpeg openai-whisper" ;;
    Linux)  echo "  sudo apt install ffmpeg && pipx install yt-dlp && pipx install openai-whisper" ;;
    *)      echo "  winget install yt-dlp.yt-dlp Gyan.FFmpeg && pip install openai-whisper" ;;
  esac
}
NEED=(ffmpeg whisper)
[ -f "$SRC" ] || NEED+=(yt-dlp)
MISSING=()
for c in "${NEED[@]}"; do command -v "$c" >/dev/null 2>&1 || MISSING+=("$c"); done
if [ ${#MISSING[@]} -gt 0 ]; then
  echo "ERRO: faltam programas: ${MISSING[*]}. Instale com:" >&2
  install_hint >&2
  exit 10
fi

if [ -n "$OUTDIR" ]; then
  mkdir -p "$OUTDIR"; WORK="$OUTDIR"
else
  WORK=$(mktemp -d -t transcribe-br.XXXXXX)
  trap 'rm -rf "$WORK"' EXIT
fi

COOKIE_ARGS=()
[ -n "$COOKIES" ] && COOKIE_ARGS=(--cookies-from-browser "$COOKIES")

# --- Atalho: legenda oficial do YouTube --------------------------------------
if [ "$YT_SUBS" -eq 1 ] && [ ! -f "$SRC" ] && [[ "$SRC" =~ youtu\.?be ]]; then
  SUB_LANG="${LANG_OPT/auto/pt}"
  echo "[0] Procurando legenda oficial ($SUB_LANG) no YouTube…" >&2
  if yt-dlp --no-playlist --skip-download --write-subs --sub-langs "${SUB_LANG}.*,${SUB_LANG}" \
       --convert-subs srt ${COOKIE_ARGS[@]+"${COOKIE_ARGS[@]}"} \
       -o "$WORK/legenda.%(ext)s" "$SRC" >&2 2>/dev/null; then
    SRT=$(find "$WORK" -maxdepth 1 -name 'legenda*.srt' | head -n1)
    if [ -n "$SRT" ]; then
      mv -f "$SRT" "$WORK/transcript.srt"
      # SRT -> texto corrido
      grep -vE '^[0-9]+$|-->|^\s*$' "$WORK/transcript.srt" | tr '\n' ' ' | sed 's/  */ /g' > "$WORK/transcript.txt"
      echo "  legenda oficial encontrada (feita pelo canal; não é a automática)." >&2
      echo "" >&2; echo "=== TRANSCRIÇÃO (legenda oficial do YouTube) ===" >&2
      cat "$WORK/transcript.txt"; echo
      exit 0
    fi
  fi
  echo "  sem legenda oficial; seguindo com o Whisper." >&2
fi

# --- 1. Áudio ----------------------------------------------------------------
if [ -f "$SRC" ]; then
  echo "[1/2] Extraindo áudio do arquivo local: $SRC" >&2
  ffmpeg -hide_banner -loglevel error -y -i "$SRC" -vn -acodec libmp3lame -q:a 2 "$WORK/audio.mp3"
else
  echo "[1/2] Baixando áudio: $SRC" >&2
  yt-dlp --no-playlist --extract-audio --audio-format mp3 --audio-quality 0 \
    ${COOKIE_ARGS[@]+"${COOKIE_ARGS[@]}"} -o "$WORK/audio.%(ext)s" "$SRC" >&2 || {
    echo "ERRO: não foi possível baixar. Conteúdo privado ou com login? Tente -c chrome." >&2
    echo "      Erro 403/SABR no YouTube? Atualize o yt-dlp (yt-dlp -U ou brew upgrade yt-dlp)." >&2
    exit 2; }
fi
AUDIO="$WORK/audio.mp3"
[ -f "$AUDIO" ] || { echo "ERRO: nenhum áudio extraído (vídeo sem som?)." >&2; exit 2; }

# --- 2. Whisper --------------------------------------------------------------
WHISPER_ARGS=(--model "$MODEL" --output_dir "$WORK" --output_format all --fp16 False --verbose False)
[ "$LANG_OPT" != "auto" ] && WHISPER_ARGS+=(--language "$LANG_OPT")

if [ "$NO_GLOSS" -eq 0 ]; then
  if [ -z "$GLOSS" ]; then
    for g in "$HOME/.config/transcricao-br/glossario.txt" "$HERE/glossario.txt"; do
      [ -f "$g" ] && GLOSS="$g" && break
    done
  fi
  if [ -n "$GLOSS" ] && [ -f "$GLOSS" ]; then
    TERMS=$(grep -vE '^\s*(#|$)' "$GLOSS" | head -n 60 | paste -sd ',' - | sed 's/,/, /g')
    [ -n "$TERMS" ] && WHISPER_ARGS+=(--initial_prompt "Vídeo sobre política brasileira. Termos: ${TERMS}.")
  fi
fi

echo "[2/2] Transcrevendo com Whisper ($MODEL, idioma: $LANG_OPT${GLOSS:+, com glossário})…" >&2
whisper "$AUDIO" "${WHISPER_ARGS[@]}" >&2

for ext in txt srt vtt json tsv; do
  [ -f "$WORK/audio.$ext" ] && mv -f "$WORK/audio.$ext" "$WORK/transcript.$ext"
done
rm -f "$WORK/transcript.vtt" "$WORK/transcript.tsv"
[ -f "$WORK/transcript.txt" ] || { echo "ERRO: o Whisper não gerou transcrição." >&2; exit 3; }

echo "" >&2
echo "=== TRANSCRIÇÃO (automática — confira citações no áudio antes de usar) ===" >&2
cat "$WORK/transcript.txt"
[ -n "$OUTDIR" ] && echo "Arquivos em: $OUTDIR (transcript.txt, transcript.srt, transcript.json, audio.mp3)" >&2
exit 0
