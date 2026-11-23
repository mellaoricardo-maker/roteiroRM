---
name: content-ideas-br
description: Pesquisa de pautas a partir de uma lista de contas do Instagram (políticos, comunicadores, jornalistas, perfis de utilidade pública). Usa a API oficial da Meta para achar os Reels recentes que mais superaram a mediana de views da própria conta, descarta os patrocinados/impulsionados, opcionalmente transcreve em português, filtra pelo público do usuário e entrega um relatório com os Reels para assistir e como adaptar cada um (ângulo, 3 ganchos, estrutura, chamada final). Use quando o usuário pedir "ideias de conteúdo", "ideias de Reels", "o que está funcionando no meu nicho", "o que os outros políticos estão postando que bombou", "pesquisa semanal de conteúdo", "/content-ideas-br".
---

# Content Ideas BR — dos concorrentes às pautas adaptadas

Uma varredura, um relatório. O usuário sai com 5–8 Reels para assistir e, para cada um, o que gravar.

Versão adaptada de `content-ideas` + `competitor-report` (creator-skills, de Cristiano Capasso, licença MIT — ver `LICENSE-original`).

**O que mudou em relação ao original:**
- **Autocontida e só com API oficial.** Não depende da pasta `competitor-report` nem de navegador automatizado com conta secundária.
- **Filtro de patrocínio em português** (`#publi`, `#publicidade`, "parceria paga", "conteúdo patrocinado"…). Só hashtags e expressões inequívocas, porque em política "publicidade" ou "impulsionada" costumam ser o assunto. Impulsionamento sem marcação é pego pela regra de curtidas/views (abaixo de 1/4 do normal da conta).
- **Para quando precisa:** limite de uso da API ou token vencido interrompem a varredura com aviso claro, e o que já foi lido fica salvo (salva a cada conta).
- **`--eu @suaconta`:** traz sua própria mediana como referência.
- **Transcrição em português** pela skill `transcribe-br` (desligada por padrão, ver abaixo).
- Filtro de público, ganchos e chamada final pensados para conteúdo político (sem "comente a palavra X" por padrão).

## 1. Varrer as contas

```bash
python3 "${CLAUDE_SKILL_DIR}/scan_concorrentes.py" --days 30 --min-outlier 2 --top 15 \
  --out ~/.config/content-ideas-br/dados/scan-<AAAA-MM-DD>.json [--eu @suaconta] [--transcribe 8 --cookies "chrome:Profile 2"]
```

- Lê `~/.config/content-ideas-br/concorrentes.md` (ou `--lista`). Só linhas que começam com `@`.
- Uma consulta por página de 50 posts por conta. **Limite da Meta: ~200 consultas por hora**; para listas grandes use `--per-account 30` (padrão).
- Mantém Reels: dos últimos `--days` dias, com views ÷ mediana da conta ≥ `--min-outlier`, não patrocinados, no máximo 3 por conta.
- **Sem lista ainda:** ajude o usuário a montar uma a partir de `concorrentes.exemplo.md`. **Nunca invente @contas.**
- Tema específico pedido ("ideias sobre segurança pública"): varra tudo e filtre pelo tema no passo 3.
- `stopped_early` preenchido no JSON → diga o motivo e quantas contas faltaram.

**Transcrição (opcional).** O Instagram exige login para baixar Reels. `--cookies` usa a sessão de um navegador: **use um perfil do navegador logado numa conta secundária, nunca a conta oficial do mandato.** Sem transcrição, o julgamento é feito pela legenda, que muitas vezes não diz o conteúdo — avise isso no relatório.

## 2. Carregar o contexto do usuário

Ler `~/CLAUDE.md` e o `CLAUDE.md` do projeto: público, temas/bandeiras, voz, regras de gancho e de roteiro, chamadas finais que já usa. Sem isso, perguntar uma vez: quem é o público e qual o objetivo dos vídeos (crescer, mobilizar, prestar contas, pautar debate).

## 3. Filtrar pelo público (o passo que importa)

Para cada candidato, ler transcrição e legenda e decidir:
- **Fala com o público do usuário?** Mesmo tipo de dor, de indignação ou de interesse. Um Reel que fez milhões sobre um tema que o público não liga é **não**.
- **O mecanismo é transferível?** O usuário consegue refazer com um fato, dado, documento, votação ou experiência **dele** (mandato, projeto, fiscalização, discurso)? Se exigiria inventar número, experiência ou posição que ele não tem, descarte.
- **Cabe no posicionamento?** Não proponha adaptar conteúdo que contradiga posições públicas do usuário; se houver conflito, sinalize em vez de adaptar.

Ficar com os 5–8 melhores. Os descartados ganham uma linha com o motivo.

## 4. Escrever o relatório

Arquivo: `~/.config/content-ideas-br/relatorios/<AAAA-MM-DD>.md`, em português.

1. **Em resumo:** 3–4 linhas sobre o que está funcionando agora (padrões entre os Reels mantidos: tipo de gancho, formato, tema).
2. **Reels para assistir**, cada um com:
   - link, @conta, views, múltiplo (×), há quantos dias, tamanho da amostra da mediana;
   - **gancho original** (primeira frase da transcrição; sem transcrição, diga "pela legenda") e **por que funciona** (o mecanismo: revelação, contraste, número, indignação, nome de autoridade, documento na tela, pergunta);
   - **Versão do usuário:** ângulo para o público dele · **3 ganchos** na voz dele (até 12 palavras, com a dor ou o conflito dentro) · estrutura em 4–5 linhas · o **fato/documento/dado real dele** a usar · chamada final no padrão dele (seguir, compartilhar, comentar opinião, link) — evite "comente a palavra X" se não for o padrão do usuário.
3. **Descartados:** uma linha cada — link e motivo (fora do público / não transferível / patrocinado / conflita com posicionamento).
4. **Dados:** contas lidas, contas com falha (e por quê), parâmetros, caminho do JSON, se parou antes do fim.

**Regras:**
- Números só do JSON.
- **Fatos mencionados nos Reels de terceiros não são fonte.** Antes de virarem roteiro, precisam ser verificados em fonte primária (a skill `roteiro` faz isso).
- Não escreva roteiro completo aqui. Quando o usuário escolher uma ideia, passe para `roteiro` ou `roteiro-viral-reels-ricardomellao`; para dissecar a edição de um Reel, `video-breakdown-br`.

## 5. Responder no chat

O padrão em 2 linhas, depois uma linha por ideia (link + melhor gancho), depois o caminho do relatório. Perguntar qual desenvolver.

## Limites dos números (dizer ao usuário quando relevante)

- **`view_count` inclui views pagas** (documentação da Meta). O filtro de curtidas/views pega impulsionamento grosseiro, não todo.
- A Meta registrou mudança para somar views do Facebook em vídeos publicados nas duas redes, mas há nota conflitante dizendo que, nesta consulta, continua só Instagram. Contas que cruzam postagem podem ter números inflados; trate múltiplos muito altos com cautela.
- Mediana com poucos Reels (`baseline_sample` < 8) é instável; sinalize.
- Só contas Profissionais. Contas pessoais e privadas ficam de fora.
- Em período eleitoral, conteúdo impulsionado de candidatos segue regras próprias da Justiça Eleitoral; não trate como orgânico e, em caso de dúvida sobre o que pode ser feito, consulte a assessoria jurídica.

## Configuração (uma vez, ~30–60 min)

Precisa de: Instagram como conta **Profissional** (Empresa ou Criador) ligada a uma **Página do Facebook**.

Passos (resumo do guia do autor original; os menus da Meta mudam com frequência):
1. Criar um app em developers.facebook.com/apps, caso de uso de gerenciar mensagens e conteúdo do Instagram. Deixar em **modo de desenvolvimento** (como administrador, você usa sem revisão da Meta).
2. Em Casos de uso → Instagram → Personalizar → configuração da API com login do Facebook → Permissões: `instagram_basic`, `instagram_manage_insights`, `pages_read_engagement`, `pages_show_list`, `business_management`.
3. No Graph API Explorer: escolher o app, gerar token de usuário com essas permissões, selecionando sua Página e seu Instagram.
4. No Access Token Debugger: **Extend Access Token**.
5. De volta ao Explorer, com o token estendido: `GET me/accounts?fields=name,access_token,instagram_business_account` → copiar o `access_token` da Página e o `instagram_business_account.id`.
6. Salvar em `~/.config/content-ideas-br/.env`:
   ```
   IG_GRAPH_TOKEN=<access_token da Página>
   IG_GRAPH_USER_ID=<id do instagram_business_account>
   ```
   (O script também lê `~/.creator-skills/.env`, se você já configurou o original.)
7. Testar: `python3 scan_concorrentes.py --lista <arquivo com uma @conta conhecida> --top 3`.

**Renovação a cada 90 dias:** a Meta corta o acesso a dados mesmo com token de Página. Quando o script avisar "token inválido ou acesso a dados vencido", repita os passos 3–6. Ponha um lembrete na agenda.

**Segurança:** o token dá acesso à sua Página e ao seu Instagram. Não o coloque no repositório nem em mensagens; o `.env` fica fora do git.
