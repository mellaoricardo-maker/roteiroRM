---
name: ig-competitor-research-br
description: Pesquisa semanal de Reels no Instagram com relatório visual. Varre a lista de contas acompanhadas pela API oficial da Meta, ranqueia os Reels pelo múltiplo da mediana da própria conta (sem patrocinados), aprofunda os melhores (quadros dos 3 primeiros segundos, transcrição em português, cortes por minuto, palavras por segundo) e gera um relatório HTML autocontido, com tema claro/escuro, para escolher o que modelar. Use quando o usuário pedir "pesquisa semanal", "relatório visual dos concorrentes", "ranking de Reels", "o que bombou essa semana", "pesquisa de concorrentes no Instagram", "/ig-competitor-research-br".
---

# IG Competitor Research BR

Uma rodada por semana: o usuário abre o relatório, passa os olhos e separa ~10 Reels para modelar.

Versão reescrita de `ig-competitor-research` (creator-skills, de Cristiano Capasso, licença MIT — ver `LICENSE-original`).

**O que mudou em relação ao original:**
- **Sem navegador automatizado.** O original rolava grades com vários agentes no Claude in Chrome logado. Aqui a coleta é pela **API oficial** (motor da `content-ideas-br`), com views exatas.
- **Ranking pelo múltiplo da mediana** (views ÷ mediana da própria conta), não por views brutas — assim conta pequena com Reel fora da curva aparece, e conta grande que sempre faz milhões não domina.
- **Aprofundamento pela `video-breakdown-br`**: quadros em 0 s, 1 s e 2 s, transcrição em português com glossário, cortes por minuto (limiar para pessoa falando), palavras por segundo. Uma passada sequencial e nova tentativa dos que falharam; vídeos apagados depois.
- **Relatório novo**: em português, tema claro/escuro, funciona no celular, imagens embutidas (um único arquivo para abrir ou compartilhar). Os **padrões da semana são escritos pelo Claude a cada rodada** a partir dos dados — o original tinha padrões fixos no código, sobre o nicho do autor.
- **Sem descoberta por hashtag.** No original ela já vinha degradada (o próprio autor registra que o Instagram passou a esconder views e bloquear as páginas de hashtag). Pela API oficial, segundo o guia do autor original, a busca por hashtag exige uma permissão ("Instagram Public Content Access") que a Meta só libera após revisão do app — não conferi isso na documentação da Meta. Para achar contas novas, use o passo 2 da `content-team-br`.

Pré-requisitos: pastas `content-ideas-br`, `transcribe-br` e `video-breakdown-br` ao lado desta; token configurado (ver `content-ideas-br`, Configuração); `yt-dlp`, `ffmpeg` e `whisper` para o aprofundamento.

## 1. Varredura (API)

```bash
RUN=~/.config/content-ideas-br/semanal/<AAAA-MM-DD>
python3 "${CLAUDE_SKILL_DIR}/../content-ideas-br/scan_concorrentes.py" \
  --days 30 --min-outlier 2 --max-per-account 4 --top 40 --out "$RUN/candidatos.json"
```
- Lista: `~/.config/content-ideas-br/concorrentes.md`. Sem lista: ajude a montar uma (nunca invente @contas).
- Pauta muito quente: `--days 14`. Pouca coisa passou: `--min-outlier 1.5`.
- `stopped_early` preenchido → diga o motivo; o que foi lido está salvo.

## 2. Aprofundamento dos melhores

```bash
python3 "${CLAUDE_SKILL_DIR}/pesquisa_semanal.py" enriquecer "$RUN" --n 12 --cookies "<navegador>"
```
- Baixar Reels exige login: `--cookies` com **um perfil do navegador logado numa conta secundária** (ex.: `"chrome:Profile 2"`), nunca a conta oficial. Pergunte ao usuário antes.
- ~1–2 min por Reel (transcrição). Rode em segundo plano e siga para o passo 3 com o que já estiver pronto.
- Sem `--cookies` ou com falhas: o relatório sai assim mesmo; esses Reels aparecem sem quadros e com o gancho pela legenda.

## 3. Análise (Claude escreve `RUN/analise.json`)

Leia `candidatos.json`, as pastas `RUN/enrich/<código>/` (`gancho/`, `transcript.srt`, `info.txt`) e o `CLAUDE.md` do usuário. Escreva:

```json
{
  "resumo": "1–2 frases: o que dominou esta semana nas contas acompanhadas",
  "padroes": [
    {"titulo": "até 6 palavras", "texto": "o padrão, com os Reels (@conta) que o mostram"}
  ],
  "reels": {
    "<permalink exato>": {
      "tema": "2–4 palavras",
      "por_que": "o mecanismo do gancho/estrutura, não o tema",
      "gancho_falado": "só se precisar corrigir a primeira frase da transcrição (nomes, por exemplo)"
    }
  }
}
```

Regras:
- 3–5 padrões, cada um apoiado em **pelo menos 2 Reels** do ranking. Padrão com um exemplo só não é padrão.
- "Por que funcionou" é inferência: escreva como hipótese plausível, apoiada no que se vê (gancho, quadros, ritmo).
- Números só dos arquivos. Não comente Reels sem dados (sem transcrição e sem legenda útil): deixe sem análise.
- Cortes por minuto é estimativa automática; não tire conclusão forte de diferença pequena.

## 4. Relatório

```bash
python3 "${CLAUDE_SKILL_DIR}/pesquisa_semanal.py" relatorio "$RUN" --top 30
```
Gera `RUN/pesquisa-reels-<data>.html`, um arquivo só (imagens embutidas). Se o usuário quiser compartilhar com a equipe, ofereça publicar como página (Artifact) — o conteúdo tem legendas e transcrições de terceiros, então pergunte antes.

## 5. Responder no chat

Duas linhas com o padrão principal, os 5 primeiros do ranking (link + múltiplo + gancho), o caminho do HTML. Pergunte quais modelar — e encaminhe: roteiro (`roteiro` / `roteiro-viral-reels-ricardomellao`), edição (`video-breakdown-br` com mais detalhe), ou adaptação em lote (`content-team-br`).

## Limites

- Views da API incluem alcance pago e podem somar views do Facebook em posts cruzados (ver `content-ideas-br`).
- Mediana com poucos Reels é marcada no relatório ("mediana com só N Reels").
- Só contas Profissionais; pessoais e privadas ficam de fora.
- Fatos ditos nos Reels de terceiros não são fonte: verificar antes de usar em roteiro.
- Rodar no máximo uma vez por semana; muitas rodadas seguidas consomem o limite de ~200 consultas/hora da API.
