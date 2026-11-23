#!/bin/bash
# video-breakdown-br — baixa um vídeo (ou usa um arquivo local), separa áudio,
# extrai quadros com horário, folhas de contato, os 3 primeiros segundos em
# detalhe, detecta cortes de cena e transcreve com Whisper local.
#
# Baseado em `video-breakdown` de creator-skills (c) 2026 Cristiano Capasso, MIT
# (ver LICENSE-original). Mudanças: português como padrão, glossário de nomes
# próprios, arquivo local como entrada, fps automático pela duração, quadros do
# gancho (0–3 s), detecção de cortes com ritmo (cortes/min e duração média de
# plano), ficha técnica (duração, resolução, vertical/horizontal), instalação
# fora do Mac.
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Uso: breakdown.sh <link-ou-arquivo> [opções]

  -f FPS       quadros por segundo; padrão automático: 2 (até 60 s), 1 (até 3 min), 0.5 (mais longo)
  -m MODELO    tiny | base | small | medium | large-v3          (padrão: medium)
  -l IDIOMA    pt, en, es… ou "auto"                            (padrão: pt)
  -s LIMIAR    sensibilidade da detecção de cortes, 0–1         (padrão: 0.3;
               use 0.06 para pessoa falando com o mesmo fundo: corte seco com
               zoom de 10–40% marca só 0,07–0,26)
  -o PASTA     pasta de saída (padrão: ./video-breakdown-<data-hora>)
  -g ARQUIVO   glossário de nomes próprios;  -G  sem glossário
  -T           não transcrever (só a parte visual)
  -c NAVEGADOR cookies do navegador (chrome, safari, firefox) para conteúdo com login

Gera em <PASTA>/:
  info.txt           ficha técnica e ritmo de edição
  video.mp4          vídeo completo
  audio.mp3          trilha de áudio
  transcript.txt     transcrição
  transcript.srt     transcrição com horários
  cortes.txt         horário de cada corte detectado
  gancho/            quadros a cada 0,25 s nos 3 primeiros segundos
  frames/            quadros amostrados, horário gravado no canto
  sheets/            folhas de contato (grade 5x6)
USAGE
  exit 1
}

[ $# -lt 1 ] && usage
SRC="$1"; shift
FPS=""; MODEL="medium"; LANG_OPT="pt"; SCENE="0.3"; OUTDIR=""; GLOSS=""; NO_GLOSS=0; NO_TR=0; COOKIES=""
while getopts "f:m:l:s:o:g:GTc:h" opt; do
  case "$opt" in
    f) FPS="$OPTARG" ;;   m) MODEL="$OPTARG" ;;   l) LANG_OPT="$OPTARG" ;;
    s) SCENE="$OPTARG" ;; o) OUTDIR="$OPTARG" ;;  g) GLOSS="$OPTARG" ;;
    G) NO_GLOSS=1 ;;      T) NO_TR=1 ;;           c) COOKIES="$OPTARG" ;;
    *) usage ;;
  esac
done
OUTDIR="${OUTDIR:-./video-breakdown-$(date +%Y%m%d-%H%M%S)}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Dependências ------------------------------------------------------------
NEED=(ffmpeg ffprobe)
[ "$NO_TR" -eq 0 ] && NEED+=(whisper)
[ -f "$SRC" ] || NEED+=(yt-dlp)
MISSING=()
for c in "${NEED[@]}"; do command -v "$c" >/dev/null 2>&1 || MISSING+=("$c"); done
if [ ${#MISSING[@]} -gt 0 ]; then
  echo "ERRO: faltam programas: ${MISSING[*]}. Instale com:" >&2
  case "$(uname -s)" in
    Darwin) echo "  brew install yt-dlp ffmpeg openai-whisper" >&2 ;;
    Linux)  echo "  sudo apt install ffmpeg && pipx install yt-dlp && pipx install openai-whisper" >&2 ;;
    *)      echo "  winget install yt-dlp.yt-dlp Gyan.FFmpeg && pip install openai-whisper" >&2 ;;
  esac
  exit 10
fi

FONT=""
for f in /System/Library/Fonts/Supplemental/Arial.ttf /Library/Fonts/Arial.ttf \
         /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /usr/share/fonts/TTF/DejaVuSans.ttf \
         /c/Windows/Fonts/arial.ttf; do
  [ -f "$f" ] && FONT="$f" && break
done

mkdir -p "$OUTDIR/frames" "$OUTDIR/sheets" "$OUTDIR/gancho"
LOG="$OUTDIR/.ffmpeg.log"; : > "$LOG"

# --- 1. Vídeo ----------------------------------------------------------------
if [ -f "$SRC" ]; then
  echo "[1/6] Usando arquivo local: $SRC" >&2
  ffmpeg -hide_banner -loglevel error -y -i "$SRC" -c copy "$OUTDIR/video.mp4" 2>>"$LOG" \
    || ffmpeg -hide_banner -loglevel error -y -i "$SRC" "$OUTDIR/video.mp4" 2>>"$LOG"
else
  echo "[1/6] Baixando vídeo: $SRC" >&2
  COOKIE_ARGS=(); [ -n "$COOKIES" ] && COOKIE_ARGS=(--cookies-from-browser "$COOKIES")
  yt-dlp --no-playlist -f "bv*+ba/b" --merge-output-format mp4 \
    ${COOKIE_ARGS[@]+"${COOKIE_ARGS[@]}"} -o "$OUTDIR/video.%(ext)s" "$SRC" >&2 || true
  V=$(find "$OUTDIR" -maxdepth 1 -name 'video.*' | head -n1)
  if [ -z "$V" ]; then
    echo "ERRO: não foi possível baixar o vídeo." >&2
    echo "  - Privado ou com login? Use -c chrome (ou safari/firefox)." >&2
    echo "  - Erro 403/SABR no YouTube? Atualize: yt-dlp -U ou brew upgrade yt-dlp." >&2
    exit 2
  fi
  [ "$V" != "$OUTDIR/video.mp4" ] && mv -f "$V" "$OUTDIR/video.mp4"
fi
VIDEO="$OUTDIR/video.mp4"

# --- Ficha técnica -----------------------------------------------------------
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VIDEO" | cut -d. -f1 || true)
DUR=${DUR:-0}
read -r W H < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height \
                 -of csv=s=x:p=0 "$VIDEO" | tr 'x' ' ' | head -n1) || true
ROT=$(ffprobe -v error -select_streams v:0 -show_entries stream_side_data=rotation \
       -of default=nw=1:nk=1 "$VIDEO" 2>/dev/null | head -n1 | tr -d '-' || true)
if [ "${ROT:-0}" = "90" ] || [ "${ROT:-0}" = "270" ]; then T=$W; W=$H; H=$T; fi
if [ "${H:-0}" -gt "${W:-0}" ]; then ORIENT="vertical"; elif [ "${H:-0}" -lt "${W:-0}" ]; then ORIENT="horizontal"; else ORIENT="quadrado"; fi

if [ -z "$FPS" ]; then
  if [ "$DUR" -le 60 ]; then FPS=2; elif [ "$DUR" -le 180 ]; then FPS=1; else FPS=0.5; fi
fi
TS_DRAW=""
[ -n "$FONT" ] && TS_DRAW=",drawtext=fontfile='${FONT}':text='%{pts\:hms}':x=20:y=20:fontsize=40:fontcolor=yellow:box=1:boxcolor=black@0.6:boxborderw=10"

# --- 2. Áudio ----------------------------------------------------------------
echo "[2/6] Extraindo áudio" >&2
if ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" -vn -acodec libmp3lame -q:a 2 "$OUTDIR/audio.mp3" 2>>"$LOG" \
   && [ -s "$OUTDIR/audio.mp3" ]; then HAS_AUDIO=1; else HAS_AUDIO=0; rm -f "$OUTDIR/audio.mp3"; echo "  (sem trilha de áudio)" >&2; fi

# --- 3. Quadros e folhas de contato ------------------------------------------
echo "[3/6] Quadros a ${FPS} fps e folhas de contato" >&2
ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" -vf "fps=${FPS}${TS_DRAW}" -q:v 3 \
  "$OUTDIR/frames/frame_%04d.jpg" 2>>"$LOG"
ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" \
  -vf "fps=${FPS},scale=360:-2${TS_DRAW},tile=5x6:padding=8:margin=8:color=white" \
  "$OUTDIR/sheets/sheet_%03d.png" 2>>"$LOG"
NFRAMES=$(find "$OUTDIR/frames" -name '*.jpg' | wc -l | tr -d ' ')
NSHEETS=$(find "$OUTDIR/sheets" -name '*.png' | wc -l | tr -d ' ')

# --- 4. Gancho: 0–3 s a cada 0,25 s ------------------------------------------
echo "[4/6] Quadros do gancho (0–3 s)" >&2
ffmpeg -hide_banner -loglevel error -y -t 3 -i "$VIDEO" -vf "fps=4${TS_DRAW}" -q:v 3 \
  "$OUTDIR/gancho/gancho_%02d.jpg" 2>>"$LOG"

# --- 5. Cortes de cena -------------------------------------------------------
echo "[5/6] Detectando cortes (limiar ${SCENE})" >&2
ffmpeg -hide_banner -nostats -i "$VIDEO" -an \
  -vf "select='gt(scene,${SCENE})',showinfo" -f null - 2>&1 \
  | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 \
  | awk 'NR==1 || $1-last >= 0.25 {printf "%02d:%05.2f\n", int($1/60), $1-60*int($1/60); last=$1}' > "$OUTDIR/cortes.txt" || true
NCUTS=$(grep -c . "$OUTDIR/cortes.txt" || true)
if [ "$DUR" -gt 0 ]; then
  CPM=$(awk -v n="$NCUTS" -v d="$DUR" 'BEGIN{printf "%.1f", n*60/d}')
  ASL=$(awk -v n="$NCUTS" -v d="$DUR" 'BEGIN{printf "%.1f", d/(n+1)}')
else CPM="?"; ASL="?"; fi

# --- 6. Transcrição ----------------------------------------------------------
if [ "$NO_TR" -eq 1 ]; then
  echo "[6/6] Transcrição desativada (-T)" >&2
elif [ "$HAS_AUDIO" -eq 1 ]; then
  WARGS=(--model "$MODEL" --output_dir "$OUTDIR" --output_format all --fp16 False --verbose False)
  [ "$LANG_OPT" != "auto" ] && WARGS+=(--language "$LANG_OPT")
  if [ "$NO_GLOSS" -eq 0 ]; then
    if [ -z "$GLOSS" ]; then
      for g in "$HOME/.config/transcricao-br/glossario.txt" "$HERE/glossario.txt"; do
        [ -f "$g" ] && GLOSS="$g" && break
      done
    fi
    if [ -n "$GLOSS" ] && [ -f "$GLOSS" ]; then
      TERMS=$(grep -vE '^\s*(#|$)' "$GLOSS" | head -n 60 | paste -sd ',' - | sed 's/,/, /g')
      [ -n "$TERMS" ] && WARGS+=(--initial_prompt "Vídeo sobre política brasileira. Termos: ${TERMS}.")
    fi
  fi
  echo "[6/6] Transcrevendo com Whisper ($MODEL, idioma: $LANG_OPT)…" >&2
  whisper "$OUTDIR/audio.mp3" "${WARGS[@]}" >"$OUTDIR/.whisper.log" 2>&1 || echo "  (Whisper falhou; ver .whisper.log)" >&2
  for ext in txt srt json; do
    [ -f "$OUTDIR/audio.$ext" ] && mv -f "$OUTDIR/audio.$ext" "$OUTDIR/transcript.$ext"
  done
  rm -f "$OUTDIR/audio.vtt" "$OUTDIR/audio.tsv"
else
  echo "[6/6] Sem áudio; transcrição pulada." >&2
  echo "(sem trilha de áudio)" > "$OUTDIR/transcript.txt"
fi

WORDS=0; WPS="?"
if [ -f "$OUTDIR/transcript.txt" ] && [ "$HAS_AUDIO" -eq 1 ] && [ "$DUR" -gt 0 ]; then
  WORDS=$(wc -w < "$OUTDIR/transcript.txt" | tr -d ' ')
  WPS=$(awk -v w="$WORDS" -v d="$DUR" 'BEGIN{printf "%.1f", w/d}')
fi

cat > "$OUTDIR/info.txt" <<EOF
Origem:           $SRC
Duração:          ${DUR} s
Resolução:        ${W}x${H} (${ORIENT})
Cortes detectados: ${NCUTS} (limiar ${SCENE})
Cortes por minuto: ${CPM}
Plano médio:       ${ASL} s
Palavras faladas:  ${WORDS} (${WPS} por segundo)
Quadros:           ${NFRAMES} a ${FPS} fps | folhas: ${NSHEETS} | gancho: 0–3 s a 4 fps
EOF

echo ""
echo "=== VIDEO BREAKDOWN PRONTO ==="
echo "Pasta: $OUTDIR"
cat "$OUTDIR/info.txt"
echo ""
echo "Ordem de leitura: info.txt → gancho/ → sheets/ → cortes.txt + transcript.srt → frames/ para detalhe."
