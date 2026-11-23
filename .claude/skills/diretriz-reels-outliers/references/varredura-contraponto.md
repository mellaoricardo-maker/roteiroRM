# Varredura de contraponto — orientação completa

Objetivo: encontrar, nas últimas 72 horas, falas públicas de figuras conhecidas que contrariem a pauta **liberal na economia e conservadora nos costumes**, com potencial de reação (frase forte + rosto conhecido + vídeo circulando), e transformar cada achado num cartão de pauta.

Alvo é **declaração pública de pessoa pública** (entrevista, podcast, plenário, sessão, discurso, post). Nunca pessoa comum, vida privada ou família.

## 1. Quem monitorar (lista de partida — conferir cada @ pela bio e atualizar mensalmente)

- **Governo e ministros:** Lula, Haddad, Boulos (Secretaria-Geral), ministros da área econômica e social; presidência do Banco Central quando defender intervenção.
- **Parlamentares de esquerda com alcance:** Erika Hilton, Sâmia Bomfim, Tabata Amaral, André Janones; lideranças do PT e do PSOL na Câmara, no Senado e na Alesp.
- **STF e tribunais:** ministros em sessões, votos, palestras e entrevistas (Moraes, Gilmar Mendes, Dino, Fachin, Zanin, Cármen Lúcia e demais).
- **Influenciadores e comentaristas:** Felipe Neto, Jones Manoel, Breno Altman, Eduardo Moreira (ICL); perfis pequenos de reação de esquerda que estão crescendo (ex.: @umjovempaulo, @sitetudoepolitica, @pedro.costajr).
- **Jornalistas e analistas** que defendem posições contrárias em TV, colunas e podcasts.
- **Economistas** que propõem mais gasto, taxação, controle de preços ou intervenção.
- **Veículos que amplificam:** Mídia Ninja, Brasil de Fato, ICL Notícias, TV 247, Fórum, Quebrando o Tabu, Meteoro Brasil.

Handles confirmados na pesquisa de 23/11/2026: @lulaoficial, @hilton_erika, @samiabomfim, @tabataamaralsp, @andrejanones, @guilhermeboulos.oficial, @felipeneto, @midianinja, @brasildefato, @quebrandootabu, @meteorobrasil, @umjovempaulo, @sitetudoepolitica, @pedro.costajr.

## 2. Onde procurar (ordem de prioridade)

1. **Fontes oficiais (frase exata, incontestável):**
   - Câmara — Banco de Discursos e Notas Taquigráficas, busca por orador, partido e período (discursos sem revisão saem em ~2 h): camara.leg.br → Discursos e Notas Taquigráficas → Pesquisa avançada.
   - Senado — busca de Pronunciamentos por senador e notas taquigráficas em PDF: senado.leg.br.
   - STF — sessões ao vivo e acervo no canal do STF no YouTube e na TV Justiça (Plenário e Turmas).
   - Alesp — TV Alesp e notas das sessões.
2. **Entrevistas e podcasts:** em 2026 o presidente priorizou podcasts (Inteligência Ltda., Mano a Mano) e entrevistas digitais. Monitorar Roda Viva, GloboNews, CNN Brasil, ICL Notícias, TV 247, Flow, Podpah quando recebem políticos.
3. **Redes:** Reels, TikTok, X, Shorts e lives dos perfis da lista.
4. **Cortes viralizando:** páginas que recortam falas — achar sempre a origem.

## 3. Como buscar

- **Automático (Claude Code com ScrapeCreators):** `python3 scripts/varrer.py --arquivo termos.txt --dias 3` — Reels, YouTube e TikTok, filtrados por idade e ordenados por views. Termos no formato **[nome] + [tema]**: "Haddad imposto", "Moraes redes sociais", "Erika Hilton escala 6x1".
- **Web:** `site:youtube.com "[nome]" "[tema]"` com filtro "última semana"; `"[frase entre aspas]"` para achar a origem; Google Alerts por nome + tema.
- **YouTube:** "Data de envio: hoje/esta semana" + "Classificar por: visualizações".
- **X:** `from:[perfil] [tema] min_faves:500`.

## 4. Temas que disparam o alerta

- **Economia:** taxar ricos e grandes fortunas; aumento de impostos (IOF, ICMS); mais gasto público; socorro a estatais; contra privatização; controle/tabelamento de preços; ataque ao Banco Central e aos juros; 6×1 sem custo para quem emprega; crédito subsidiado; regulação excessiva.
- **Costumes:** aborto; descriminalização de drogas; gênero nas escolas; linguagem neutra; armas; liberdade religiosa; educação domiciliar; família.
- **Segurança pública:** desencarceramento, "saidinha", críticas à polícia.
- **Liberdade e instituições:** regulação das redes e censura; decisões monocráticas e ativismo do STF; inquéritos de ofício.

## 5. O que torna um achado forte

- **Máximo:** rosto conhecido + frase curta e forte + vídeo circulando nas últimas 72 h + contradição provável com dado oficial, documento ou fala anterior da mesma pessoa.
- **Contradição da própria pessoa** ("disse X em 2022, faz Y hoje") vale mais que opinião contrária.
- **Efeito no bolso ou na vida** (imposto, preço, emprego, segurança) vale mais que debate abstrato.
- Pontuar no Modo 1 da skill; só vira vídeo com 3 pontos ou mais.

## 6. Cartão de pauta

```
QUEM / CARGO:
ONDE E QUANDO: programa, plataforma, data
FRASE EXATA (transcrita do áudio, sem cortar o sentido):
LINK + MINUTO:
ALCANCE: views (e, se possível, múltiplo da média da conta de origem)
CONTEXTO: o que veio antes e depois da frase — muda o sentido?
POR QUE CONTRARIA A NOSSA PAUTA:
CONTRA-ARGUMENTO: dado, documento ou fala anterior, com fonte primária
PONTUAÇÃO NA DIRETRIZ: X pontos (critérios)
FORMATO SUGERIDO: reação / corte de momento real / autoridade em cima e criador embaixo
RISCOS: contexto, direito autoral, regras eleitorais
```

## 7. Integridade (inegociável)

- **Frase completa e no contexto.** Ouvir antes e depois; se o contexto muda o sentido, descartar. Nada de corte que faça a pessoa dizer o que não disse.
- **Fonte original sempre.** Nunca de print, corte anônimo ou "dizem que disse"; sem origem, não usar.
- **Nunca vídeo manipulado ou gerado por IA**; nunca atribuir frase que a pessoa não disse.
- **Criticar a ideia e o ato público, não a pessoa.** Sem ofensa pessoal, apelido depreciativo ou ataque a característica pessoal.
- **Trecho de terceiros:** só o necessário para comentar e criticar, com crédito (Lei 9.610/98, art. 46, III — citação para crítica "na medida justificada"; na dúvida, assessoria jurídica).
- **Período eleitoral:** conteúdo sobre candidatos segue regras próprias da Justiça Eleitoral; na dúvida, assessoria jurídica antes de publicar.
- **Todo dado do contra-argumento** passa pela checagem da skill de roteiro (fonte primária) antes de gravar.

## 8. Rotina e custo

- Duas varreduras por dia: manhã (madrugada e noite anterior) e fim da tarde (sessões do Congresso e do STF).
- Entrega: os 5 melhores cartões do dia, por pontuação.
- Semanal: revisar a lista de nomes; comparar cartões que viraram vídeo × desempenho (calibração).
- Custo no ScrapeCreators: 1 crédito por termo e por fonte. 15 termos × 3 fontes ≈ 45 créditos por varredura; com poucos créditos, use `--fontes ig,tt` e menos termos.
