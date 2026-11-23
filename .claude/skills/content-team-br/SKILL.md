---
name: content-team-br
description: Do perfil do Instagram do usuário a roteiros de Reels na voz dele. Lê o próprio perfil pela API oficial da Meta (temas, legendas, Reels mais vistos) e transcreve uma amostra para aprender como ele fala; monta ou amplia a lista de contas parecidas (menções nas legendas + sugestões conferidas na API); acha os Reels recentes dessas contas que superaram a própria mediana; transcreve os melhores; filtra pelo público do usuário; e escreve 3–5 roteiros adaptados, com fatos a verificar. Use quando o usuário mandar o próprio perfil e pedir "pesquisa de conteúdo completa", "me dá roteiros a partir do que está bombando", "o que eu devo postar", "equipe de conteúdo", "/content-team-br".
---

# Content Team BR

O usuário dá o @ do próprio perfil. Recebe 3–5 roteiros, cada um construído sobre um Reel que recentemente superou a média da própria conta no nicho dele, escritos do jeito que ele fala.

Versão adaptada de `content-team` (creator-skills, de Cristiano Capasso, licença MIT — ver `LICENSE-original`).

**O que mudou em relação ao original:**
- **Sem navegador automatizado no Instagram.** O original rolava grades e abria a faixa de "contas sugeridas" com o Claude in Chrome logado — com risco de bloqueio, e usando a conta que estivesse logada. Aqui tudo vem da **API oficial** (motor da `content-ideas-br`), com views exatas em vez dos números abreviados das miniaturas.
- **Contas parecidas** saem de: lista existente (`concorrentes.md`, compartilhada com a `content-ideas-br`) + **@menções** nas suas legendas e nas das contas da lista + sugestões suas ou do Claude. **Toda candidata é conferida na API** (existe? o que diz a bio? tem Reels?) antes de entrar na lista.
- **Português**, transcrição pela `transcribe-br`, filtro de patrocínio em português.
- **Roteiros pela skill de roteiro do usuário** quando existir; senão, pelo `references/guia-roteiro.md`, adaptado a opinião e explicação política, com **regra dura de fonte primária** para todo fato.

Pré-requisitos: as pastas `content-ideas-br` e `transcribe-br` ao lado desta; token configurado (ver `content-ideas-br`, seção Configuração).

## 0. Preparar

1. `python3 "${CLAUDE_SKILL_DIR}/equipe.py" check`. Faltando ferramenta ou token: mostre o que falta e espere o usuário antes de instalar qualquer coisa.
2. Pasta da rodada: `RUN=~/.config/content-ideas-br/equipe/<conta>/<AAAA-MM-DD>`.
3. Pergunte uma vez se pode transcrever. Transcrever exige `--cookies` com **um perfil do navegador logado numa conta secundária** (ex.: `"chrome:Profile 2"`), nunca a conta oficial. Sem isso, o trabalho segue só com legendas — e a amostra de voz fica fraca; avise.

## 1. Aprender o usuário

1. `python3 "${CLAUDE_SKILL_DIR}/equipe.py" voz "$RUN" --eu @<conta> [--cookies "<navegador>"]`
   Lê o perfil, as legendas recentes, a mediana, e transcreve 3 Reels (os 2 mais vistos + o mais recente).
2. Leia `~/CLAUDE.md` e o `CLAUDE.md` do projeto; onde discordarem do que você inferiu, eles valem.
3. Escreva `RUN/perfil.md`:
   - para quem fala e o que defende (bio, link, como as legendas terminam);
   - temas recorrentes;
   - **como fala**: tamanho de frase, 1ª ou 2ª pessoa, palavras que repete, como abre ganchos, como pede ação. **Cite 5–8 frases reais** das transcrições ou legendas. Este arquivo é a voz dos roteiros.

## 2. Montar a lista de contas parecidas

Lista: `~/.config/content-ideas-br/concorrentes.md` (mesma da `content-ideas-br`).

- **Se já tiver 8+ contas ativas**, use-a e pule para o passo 3 (o usuário pode tê-la editado).
- **Senão, amplie:**
  1. Opcional: proponha até 10 contas que você acredita serem do mesmo nicho/público. **Não as trate como certas.**
  2. `python3 "${CLAUDE_SKILL_DIR}/equipe.py" candidatas "$RUN" --eu @<conta> [--extra @sugestao1 @sugestao2 …]`
     Junta as @menções das suas legendas e das contas da lista, mais as sugestões, e confere cada uma na API.
  3. Para cada candidata com `ok: true`, **verifique o nicho pela bio**: fala com o mesmo tipo de público ou sobre os mesmos temas? Tamanho, formato e estilo não importam. Sugestão sua cuja bio não confirma quem você pensava → descarte (pode ser homônimo ou perfil falso). `ok: false` → descarte.
  4. **Mostre a proposta ao usuário antes de gravar**: entram (com uma linha do porquê) e ficam de fora (com o motivo). Depois de aprovada, acrescente na lista: aceitas como `@conta  # motivo`, recusadas como `> @conta  # motivo` (não voltam nas próximas rodadas).
- Origem de cada conta (menção sua, menção de aliado, sugestão conferida) vai no relatório.

## 3. Achar os Reels fora da curva

```bash
python3 "${CLAUDE_SKILL_DIR}/../content-ideas-br/scan_concorrentes.py" \
  --days 90 --min-outlier 2 --max-per-account 2 --top 10 --transcribe 6 \
  [--cookies "<navegador>"] --eu @<conta> --out "$RUN/candidatos.json"
```
Reels dos últimos 90 dias com views ≥ 2× a mediana da conta, sem patrocinados, até 2 por conta, 10 no total; transcreve os 6 primeiros. Para pauta quente, use `--days 30`.

## 4. Ficar com o que serve ao público do usuário

Para cada candidato transcrito, leia transcrição e legenda e decida:
- **Fala com o público do usuário?** Mesma dor, indignação ou interesse. Milhões de views em tema que o público dele não liga → não.
- **Dá para refazer com algo dele de verdade?** Projeto, votação, fiscalização, dado oficial, história vivida. Se exigiria inventar, descarte.
- **Cabe no posicionamento?** Não adapte o que contradiz posições públicas do usuário; sinalize.

Fique com os 3–5 melhores; os descartados ganham uma linha com o motivo. Para entender a edição de um escolhido, ofereça `video-breakdown-br`.

## 5. Escrever os roteiros

Siga `references/guia-roteiro.md` — que manda usar a skill de roteiro do usuário quando existir. Um roteiro por Reel mantido, em português, na voz de `RUN/perfil.md`. **Fatos dos Reels de origem não são fonte**: tudo que for afirmado precisa de fonte primária ou vira `[PROVA: …]` em "A PREPARAR".

## 6. Relatório

`RUN/relatorio.md`:
1. **Em resumo:** 3 linhas sobre o que está funcionando no nicho agora.
2. **Roteiros**, um bloco cada: Reel de origem (link, @conta, views, múltiplo, há quantos dias), gancho original e por que funcionou, o roteiro no formato do guia, e o que preparar antes de gravar (provas e checagens).
3. **Descartados:** link e motivo.
4. **Dados:** contas lidas, contas novas (com origem) e recusadas, contas com falha, se a varredura parou antes do fim, caminhos de `candidatos.json` e `candidatas.json`.

No chat: o padrão em duas linhas, uma linha por roteiro (gancho + Reel de origem), o caminho do relatório. Pergunte qual refinar.

## Notas

- Números só dos arquivos em `RUN`. Reel sem transcrição é julgado pela legenda, e o relatório diz isso.
- Limites dos números (views pagas, possível soma com Facebook, mediana com poucos Reels): ver `content-ideas-br`.
- Rodar no máximo uma vez por semana; um Reel que bombou há 3 meses já é notícia velha.
- Nenhuma conta utilizável (todas pessoais/privadas, sem Reels): diga isso e peça ao usuário 5 contas que ele considera referência.
