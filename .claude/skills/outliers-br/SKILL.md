---
name: outliers-br
description: Detector de outliers do YouTube adaptado ao Brasil e a Shorts. Dado um tema, acha os vídeos recentes em português que mais superaram o desempenho normal do próprio canal (views ÷ mediana do canal no mesmo formato — um 10x fez 10 vezes o normal), lê as transcrições e propõe ganchos e títulos adaptados ao nicho e à voz do usuário. Use quando o usuário pedir "outliers", "/outliers-br", "o que está viralizando no YouTube/Shorts sobre X", vídeos fora da curva, ou referências de gancho para Reels/Shorts a partir de um tema.
---

# Outliers BR

Versão adaptada de `outliers` (creator-skills, de Cristiano Capasso, licença MIT — ver `LICENSE-original`).

**O que mudou em relação ao original:**
- Busca em **português / Brasil** (o original era fixo em inglês / EUA e descartava áudio não inglês).
- Formato **Shorts por padrão** (até 3 min). O original buscava só vídeos de 4 a 20 min.
- **Linha de base por formato:** Shorts comparados com os Shorts do canal, longos com os longos. Sem isso, um Short de canal que também posta vídeos longos recebe score distorcido.
- Transcrições em pt/pt-BR (o original só pedia inglês).
- Paginação opcional (`--pages`) e score mínimo padrão 2x.

## Como rodar

```bash
cd "${CLAUDE_SKILL_DIR}"
source venv/bin/activate 2>/dev/null || (python3 -m venv venv && source venv/bin/activate && pip install -q -r requirements.txt)

ARGS="$1"
if [ -z "$ARGS" ]; then
  echo "Passe um tema, ex.: /outliers-br reforma tributária" && exit 1
elif [[ "$ARGS" == --* ]]; then
  python outlier_detector.py $ARGS
else
  python outlier_detector.py --terms "$ARGS"
fi
```

Opções:
- `--terms "X" "Y"` — um ou mais temas (obrigatório)
- `--format shorts|longos|todos` — padrão `shorts` (≤ 180 s)
- `--max_days N` — idade máxima (padrão 30; para política quente use 7)
- `--min_score N` — score mínimo (padrão 2)
- `--min_views N` — views mínimas (padrão 10.000)
- `--pages N` — páginas de busca por tema (cada uma custa 100 unidades de cota)
- `--strict_lang` — descarta vídeos sem idioma de áudio declarado (menos ruído, mas perde vídeos)
- `--lang` / `--region` — padrão `pt` / `BR`
- `--exclude_terms "X" "Y"`, `--limit N`, `--skip_transcripts`

## Passos

1. **Rodar o detector.** Saída em `${CLAUDE_SKILL_DIR}/output/outliers_<data>.json`.
2. **Ler o JSON mais recente.** Campos: `title`, `channel_name`, `view_count`, `duration_seconds`, `days_old`, `outlier_score`, `channel_median_views`, `baseline_type`, `baseline_sample`, `audio_language`, `url`, `transcript_excerpt`.
3. **Ler o contexto do usuário.** `~/CLAUDE.md` e, se existir, o `CLAUDE.md` do projeto: nicho, público, regras de voz, palavras proibidas. Sem isso, perguntar uma vez nicho + público em uma linha.
4. **Resumo do conteúdo** (2–3 frases por outlier com transcrição): o que o vídeo mostra de concreto, qual o fato/dado/demonstração, e por que o gancho funcionou (aversão à perda, contraste, número específico, indignação, revelação, etc.).
5. **3 ganchos/títulos por outlier**, cada um:
   - ancorado em um detalhe real da transcrição (não variação genérica do título);
   - no nicho e na voz do usuário;
   - mantendo o mecanismo psicológico que funcionou;
   - diferentes entre si; até 100 caracteres.
6. **Apresentar:**

```
**#N — "Título original" (SCOREx)**
Canal | views | duração | dias
URL
Base: mediana de N vídeos do mesmo formato (ou "todos os formatos" — ver ressalvas)

Resumo: ...

Ganchos/títulos:
1. ...
2. ...
3. ...
```

## Ressalvas obrigatórias ao apresentar

- **Score < 2x não é sinal de viral**; não chame de outlier.
- `baseline_type = "todos"` → o canal tinha menos de 5 vídeos do formato na amostra; o score é menos confiável. Sinalize.
- `audio_language = "não declarado"` → idioma não confirmado pela API; pode ser vídeo de Portugal ou de outro país lusófono. Confira antes de usar como referência.
- **Shorts aqui = vídeo de até 3 min**, identificado pela duração. A API não informa se é vertical; um vídeo horizontal curto também entra.
- **A mediana usa os uploads recentes**, inclusive vídeos de poucos dias que ainda não acumularam views. Isso pode baixar a mediana e inflar o score de canais que postam muito.
- **Só YouTube.** Não mede Instagram nem TikTok. Um gancho que funcionou no Shorts é indício, não prova, de que funciona em Reels.
- Fatos tirados dos vídeos precisam ser verificados em fonte primária antes de virarem roteiro.

## Configuração

- Chave **YouTube Data API v3** (gratuita): console.cloud.google.com → ativar a API → Credenciais → Chave de API.
- Colocar `YOUTUBE_API_KEY=...` em `~/.config/outliers-br/.env` (recomendado) ou no `.env` desta pasta. Também lê `~/.config/outliers/.env`, se já existir do plugin original.
- Cota gratuita: 10.000 unidades/dia; uma busca de 1 tema e 1 página usa até ~200.
