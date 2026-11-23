---
name: diretriz-reels-outliers
description: Aplica a diretriz de Reels que estouram (padrões de outliers de perfis políticos, jurídicos e econômicos) para pontuar pautas, escrever ou revisar roteiros e planejar a edição de vídeos curtos (Reels, TikTok, Shorts), e faz a varredura de contraponto. Use sempre que o usuário pedir para escolher ou ranquear pautas do radar, saber qual pauta tem mais chance de viralizar, escrever ou revisar roteiro ou gancho de Reel político, jurídico ou econômico, sugerir formato de edição ou entender por que um vídeo não performou, mesmo sem citar a diretriz. Use também para procurar falas, vídeos, entrevistas, podcasts ou posts de políticos, ministros, ministros do STF, influenciadores, jornalistas ou especialistas que contrariem a pauta liberal na economia e conservadora nos costumes, para rebater ("faz a varredura de contraponto", "o que a esquerda falou essa semana sobre imposto"). Funciona junto das skills de roteiro e de radar de pautas.
---

# Diretriz de Reels outliers

Esta skill transforma a pesquisa de 23/11/2026 (Reels que estouraram em perfis de 9 mil a 2 milhões de seguidores, de todo o espectro político, mais pautas jurídicas e econômicas) em critérios práticos. A evidência completa, com números e exemplos, está em `references/diretriz-completa.md` — leia a parte relevante quando precisar justificar uma regra ou citar um exemplo.

## A ideia central (o porquê de todas as regras)

Quem não conhece o criador não para por ele. Para porque **reconhece algo** (um rosto, um lugar, o próprio bolso) e fica porque **há algo em jogo que ainda não se resolveu** (quem tem razão, quem é o culpado, o que vai perder). Sai satisfeito e compartilha quando sente que **descobriu a verdade com uma prova** e ganhou um argumento.

- Em pauta **política**, o que está em jogo é uma briga (quem decidiu, quem mentiu).
- Em pauta **jurídica e econômica**, é algo pessoal (a conta, o salário, a empresa, o benefício).
- Perfil pequeno vive de **atenção emprestada**: o rosto e a briga são de outra pessoa; o criador é guia e testemunha.

Use isso para decidir casos que as regras não cobrem.

## Modo 1 — Pontuar pautas (radar)

Some os pontos de cada pauta:

| Critério | Pontos |
|---|---|
| Nome conhecido no centro (político, ministro, governador, prefeito, autoridade) | +2 |
| Disputa de responsabilidade com efeito no bolso ("quem decide / de quem é a culpa") | +2 |
| Vídeo de origem viralizando nas últimas 72 h, que dá para mostrar e reagir | +2 |
| *Jurídica/econômica:* instituição que decide (STF, Receita, INSS, CNJ, TCU…) | +2 |
| *Jurídica/econômica:* regra nova com efeito pessoal (conta, salário, imposto, benefício, empresa) | +2 |
| Fala de autoridade × realidade verificável (imagem, documento, local) | +1 |
| Objeto concreto ou com preço conhecido (iPhone, carro, carpete, conta de luz) | +1 |
| Fato da semana | +1 |
| Data ou prazo à frente ("a partir de fevereiro", "o STF julga amanhã") | +1 |
| Debate do momento que precisa de tradução ("ninguém entendeu…") | +1 |
| Só instituição sem rosto, sem trecho real | −1 |
| Mais de 14 dias sem fato novo | −1 |

**Vira vídeo com 3 pontos ou mais.** Para cada pauta aprovada, informe também: existe **trecho real** para mostrar (link ou onde procurar)? Qual **formato de edição** (lista abaixo)? Qual **gancho** de uma frase?

Formato de saída:

```
| Pauta | Critérios que pontuaram | Total | Trecho real | Formato | Gancho (1 frase) |
```
Depois da tabela: as 3 melhores em ordem, com o principal risco de cada (fato a verificar, isca, direito de imagem).

## Modo 2 — Escrever roteiro

Se o usuário tem skill de roteiro própria (`roteiro`, `roteiro-viral-reels-ricardomellao` ou de estilo), ela continua mandando em voz, estilo e checagem de fatos; esta skill entra como critérios de estrutura e edição. Se não houver, siga a estrutura abaixo.

1. **Gancho (0–3 s):** uma frase, falada e escrita na tela desde o primeiro quadro. Nome ou lugar concreto na primeira frase quando a pauta permitir. Três moldes que funcionaram:
   - *Você foi/vai ser enganado:* "Contaram que [nome] aumentou o imposto? Preste atenção: é mentira."
   - *Isso vai te atingir* (jurídico/econômico): "Se a sua empresa está no Simples, essa mudança vai te atingir."
   - *Pergunta com nome ou lugar:* "A Cracolândia acabou mesmo?"
2. **Mostrar antes de comentar:** se existe trecho real (plenário, entrevista, vídeo de alguém), ele entra primeiro; o comentário vem depois. Ver é mais forte que ouvir contar.
3. **Corpo:** 2–3 perguntas que o próprio autor responde ("Quer ver?", "De quem é a culpa?"); a prova aparece na tela no momento em que é citada; deixe claro **quem decide**, com a regra ou o documento. Em pauta jurídica, a estrutura **antes × agora** resolve quase tudo. Em pauta econômica, uma **conta de três números** que o espectador consegue refazer.
4. **Fechamento:** cobrança ou ação concreta ("cobre o governador", "salve se você tem dívida"). Pedido de seguir, se houver, em uma frase no fim.
5. **Medidas:** fala própria a 3,0–3,5 palavras por segundo (jurídico/econômico até 3,7). Rode `python3 scripts/medir_roteiro.py <arquivo>` (ou cole o texto) para ver palavras e duração estimada. Não corte o que a prova exige: os outliers tinham de 30 s a 3 min.

Formato de saída:

```
PAUTA E PONTUAÇÃO: … (X pontos: critérios)
FORMATO DE EDIÇÃO: …
GANCHO — falado: … | texto na tela (até 8 palavras): … | primeiro quadro: …
ROTEIRO (um bloco por parágrafo, com marcações):
  [TRECHO REAL: o quê, de quantos segundos]
  [NA TELA: manchete / documento / foto / conta]
  [VERIFICAR: fato que precisa de fonte primária]
FECHAMENTO: …
MEDIDAS: N palavras · ~X s a 3,2 palavras/s
CHECKLIST: itens atendidos / pendentes
```

## Modo 3 — Revisar roteiro ou vídeo pronto

Passe o checklist abaixo item a item, diga o que falta e por que importa, e entregue: (1) as 3 mudanças de maior efeito, em ordem; (2) o gancho reescrito em 2 versões; (3) o formato de edição sugerido. Se houver métricas do vídeo, compare com o patamar orgânico da conta (não com a mediana inflada por vídeos impulsionados ou de campanha).

## Modo 4 — Plano de edição

Escolha **um** formato e descreva segundo a segundo os primeiros 5 s e, depois, por bloco:

- **Reação:** vídeo alheio num quadro no canto superior; autor em casa olhando para ele; depois fala direta no mesmo cenário.
- **Molde dividido:** personagem ou vídeo em cima; título forte e marca embaixo, fixos.
- **Autoridade em cima, criador embaixo:** foto/vídeo da autoridade com manchete em caixa; criador falando na metade de baixo (forte em pauta jurídica).
- **No local ou selfie + provas em tela cheia:** alternar rosto (~40%) e tela cheia com trecho de TV e print da manchete (~60%).
- **Corte de momento real:** plenário, entrevista, TV; quadro estático e a frase-bomba entre aspas, em letras grandes, embaixo.
- **Gravação da tela fazendo a conta:** busca, calculadora, gráfico — o espectador vê o caminho.

Em todos: texto-gancho no quadro zero; legenda palavra a palavra quando há fala própria; produção simples (celular, luz natural); sem trilha de efeito nem transições elaboradas; cortes secos (6–15 por minuto na fala própria).

## Modo 5 — Varredura de contraponto

Procura, nas últimas 72 h, falas públicas de figuras conhecidas (governo, parlamentares de esquerda, ministros do STF, influenciadores, jornalistas, economistas) que contrariem a pauta **liberal na economia e conservadora nos costumes**, para o usuário rebater. Leia `references/varredura-contraponto.md` antes de começar: lá estão a lista de quem monitorar, as fontes por prioridade, os temas que disparam o alerta, o cartão de pauta e as regras de integridade.

1. **Coleta automática (quando o ScrapeCreators está disponível, no Claude Code):**
   `python3 scripts/varrer.py --arquivo references/termos-contraponto.txt --dias 3 --out candidatos.json`
   (ajuste os termos à semana; com poucos créditos, `--fontes ig,tt`). Custa 1 crédito por termo e por fonte — avise o usuário antes de passar de 30.
   O resultado mistura tudo: a fala original, cortes de terceiros, comentários de canais de **qualquer** lado sobre a pessoa e ruído (homônimos). É só a lista de pistas: o passo 3 separa a fala original. Os títulos do YouTube podem vir traduzidos para o inglês; o vídeo é o original. Resultados sem data são descartados por padrão.
2. **Coleta na web e nas fontes oficiais (sempre):** notas taquigráficas da Câmara e do Senado, canal do STF no YouTube, entrevistas e podcasts da semana, busca `site:youtube.com "[nome]" "[tema]"`. Sem ScrapeCreators (ex.: no chat do claude.ai), é a única via — diga que os números de views ficam incompletos.
3. **Para cada candidato forte:** ache a **fonte original** e a **frase exata no contexto** (transcrição do vídeo ou nota taquigráfica). Se não achar a origem, ou se o contexto muda o sentido, descarte.
4. **Pontue** no Modo 1 e monte o **cartão de pauta** da referência. Entregue os **5 melhores**, ordenados pela pontuação, e uma linha para cada descartado com o motivo.

O alvo é sempre declaração pública de pessoa pública. Critique a ideia e o ato, nunca a pessoa; nada de corte que distorça, vídeo manipulado ou frase atribuída sem fonte — além de errado, isso destrói a credibilidade de quem rebate.

## Checklist (usar nos modos 2 e 3)

1. Nome conhecido, lugar concreto ou "isso te atinge" na primeira frase?
2. Gancho também como texto de tela, no quadro zero?
3. Há trecho real para mostrar em vez de narrar? Está marcado onde entra?
4. A prova aparece na tela quando é citada?
5. Pelo menos uma pergunta respondida pelo próprio autor?
6. Ficou claro quem decide, com regra ou documento?
7. Fechamento com ação ou cobrança concreta?
8. Velocidade de fala dentro da faixa?
9. Todo fato com fonte primária; nada prometido no gancho que o vídeo não entregue?

## Calibração com os resultados da própria conta

A pontuação mede o **potencial da pauta se executada como a diretriz manda** (rosto no primeiro segundo, trecho real, prova na tela). Ela não foi validada na conta do usuário — e o primeiro teste a contradisse: nos 9 Reels de novembro de 2026 da conta @ricardomellao, as pautas com 4–5 pontos (Correios, supersalários, vale-massagem) tiveram 342–866 views, e pautas de curiosidade e história com 0–2 pontos (ônibus sem rodas, Dia da Bandeira) tiveram 2.052–2.308. Os vídeos de 4–5 pontos não usaram rosto no gancho nem trecho real, então a execução pode explicar parte da diferença — mas também pode ser o perfil do público.

Por isso:
- Ao pontuar, separe **pontuação da pauta** e **execução prevista** (o roteiro vai usar rosto, trecho real e prova?). Uma pauta de 5 pontos executada sem isso não deve ser tratada como aposta forte.
- Ao revisar resultados, registre por vídeo: data, pauta, pontos, formato, se usou rosto no gancho e trecho real, views em 7 dias. Com 10 ou mais registros, compare pontos × views e diga ao usuário quais critérios se confirmaram na conta dele e quais não. **Os resultados da própria conta valem mais que esta diretriz** quando contradizem uma regra marcada como [médio] ou [fraco].
- Não descarte pautas de curiosidade e história só por pontuarem pouco: nesta conta elas foram as que melhor performaram até aqui.

## Limites — diga ao usuário quando pesar

- São **correlações** de uma amostra pequena (23 vídeos dissecados, cerca de 1.000 Reels na estatística), em período eleitoral. Só o teste na própria conta confirma. Regras marcadas como [fraco] na referência são sugestão, nunca bloqueio.
- 🚨/"URGENTE" funcionou em perfis políticos pequenos (amostra pequena) e não fez diferença em pautas jurídicas e econômicas: não trate como fórmula.
- **Isca e tese frágil:** alguns outliers prometem o que não entregam ou usam tese contestável. A mecânica pode ser aproveitada; a promessa vazia e o número sem fonte, não.
- Trechos de terceiros: usar para comentar e criticar, com crédito e só o necessário.
- Rever a diretriz a cada 3 meses ou quando os resultados próprios contradisserem alguma regra; atualize `references/diretriz-completa.md`.
