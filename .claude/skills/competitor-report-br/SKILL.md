---
name: competitor-report-br
description: Relatório baseado em dados sobre UM perfil do Instagram (político, comunicador, jornalista, adversário ou aliado) a partir do link ou @: quem é, temas e bandeiras, quais posts funcionaram (outliers contra a mediana da própria conta, patrocinados sinalizados), para quem fala, para onde leva o público (link, abaixo-assinado, grupo, doação), com quem dialoga ou briga, cadência e horários, e o que o usuário pode aproveitar. Usa a API oficial da Meta. Use quando o usuário mandar um perfil do Instagram e pedir "analisa esse perfil", "quem é esse", "o que ele posta que funciona", "relatório de concorrente", "raio-x do perfil", "compara comigo", "/competitor-report-br".
---

# Competitor Report BR

O usuário manda um perfil; você devolve um relatório feito de dados, não de impressões.

Versão adaptada de `competitor-report` (creator-skills, de Cristiano Capasso, licença MIT — ver `LICENSE-original`).

**O que mudou em relação ao original:**
- **Só API oficial.** Sem o navegador automatizado com conta secundária do original (risco de bloqueio e de exposição para um mandato). Consequência: contas pessoais ou privadas não são lidas.
- **Usa o motor da `content-ideas-br`** (mesma consulta, mediana e filtro de patrocínio). As duas pastas precisam ficar lado a lado; a configuração do token é a mesma.
- **Chamadas à ação de política e comunicação em português:** link na bio, comente, "comente a palavra X", compartilhe, siga, salve, abaixo-assinado/petição, Pix/doação/vaquinha, grupo ou canal de WhatsApp/Telegram, ato/audiência/live, newsletter.
- **Menções mais frequentes** (com quem dialoga ou briga) e **dias e horários de postagem** no fuso de Brasília.
- **Patrocínio sinalizado nos outliers** e lista de outliers recentes só orgânicos.
- **`--eu @suaconta`:** comparação direta de seguidores, mediana de views e frequência.
- Seções do relatório adaptadas a perfis políticos ("o que vende" vira "para onde leva o público").

## 1. Coletar os dados

```bash
python3 "${CLAUDE_SKILL_DIR}/perfil_concorrente.py" "<link ou @conta>" --n 60 [--eu @suaconta] \
  [--transcribe-top 6 --cookies "chrome:Profile 2"] \
  --out ~/.config/content-ideas-br/perfis/dados/<conta>-<AAAA-MM-DD>.json
```

- 1 a 2 consultas à API (+1 com `--eu`). Leva segundos; com transcrição, alguns minutos.
- **Transcrição (opcional):** os maiores outliers orgânicos, pela skill `transcribe-br`. O Instagram exige login para baixar: use um perfil do navegador logado numa **conta secundária**, nunca a oficial. Sem transcrição, o tema de cada Reel vem só da legenda — diga isso no relatório.
- `--sem-site` evita visitar o site da bio.

Erros comuns: token ausente ou vencido (90 dias) → seção Configuração da `content-ideas-br`. "Não foi possível ler" → conta pessoal/privada ou @ errado.

## 2. Carregar o contexto do usuário

`~/CLAUDE.md` e o `CLAUDE.md` do projeto: público, bandeiras, posicionamento, voz. É contra isso que se mede "fala com o mesmo público?" e "o que dá para aproveitar". Sem isso, pergunte uma vez quem é o público do usuário.

## 3. Escrever o relatório

Arquivo: `~/.config/content-ideas-br/perfis/<conta>-<AAAA-MM-DD>.md`, em português.

1. **Quem é:** nome, @, seguidores, total de posts, o que a bio diz (cargo, partido, região, se constar), site. 2–4 linhas.
2. **Temas e bandeiras:** 3–5 temas recorrentes, cada um com 1–2 posts de exemplo (links). A partir de legendas e transcrições, não só de hashtags.
3. **O que funcionou:** tabela com os 5–8 melhores outliers — link, views, múltiplo (×), há quantos dias, gancho (primeira frase da transcrição ou da legenda), por que provavelmente funcionou. Separe **recentes (≤ 60 dias)** de sucessos antigos. Patrocinados/impulsionados: marcar e **não** usar como prova do que funciona organicamente.
4. **Para quem fala:** público provável, com evidência (bio, legendas, falas). Compare com o público do usuário: mesmo, sobreposto ou diferente.
5. **Para onde leva o público:** chamadas à ação mais usadas (contagens do JSON), site, links do site, palavras de "comente X". Doação, petição, grupo, newsletter, evento — só o que aparece nos dados.
6. **Com quem dialoga:** menções mais frequentes, em tom neutro (aliados, adversários, instituições, imprensa). Se o tom da menção (apoio ou ataque) não estiver claro na legenda, não afirme.
7. **Cadência e formatos:** posts por semana, Reels × carrossel × imagem, mediana de views, dias e horários mais usados. Com `--eu`: tabela lado a lado com o usuário.
8. **O que o usuário pode aproveitar:** 3–5 ideias concretas (formato, tipo de gancho, chamada à ação, horário), adaptadas ao público, à voz e ao posicionamento dele. Para virar vídeo, passar para `roteiro`; para dissecar a edição de um Reel, `video-breakdown-br`.

**Regras:**
- Todo número vem do JSON.
- O que é inferência (público, por que um Reel funcionou, tom de uma menção) é escrito como inferência, com a evidência ao lado.
- Seção sem dados → diga que faltam dados, não preencha.
- **Não atribua posições, intenções ou condutas à pessoa analisada além do que ela própria publicou.** O relatório é análise de comunicação, não dossiê. Afirmações sobre fatos (votações, gastos, processos) exigem fonte primária, verificada à parte.
- Dias e horários de postagem mostram **quando a pessoa posta**, não quando o público engaja mais.

## 4. Responder no chat

8–12 linhas: quem é, temas principais, para quem fala, para onde leva o público, os 3 Reels para assistir (links) e as 2 ideias mais úteis. Depois o caminho do relatório completo.

## Limites dos números

- `view_count` inclui views pagas; pode incluir views do Facebook em posts cruzados (a documentação da Meta é contraditória nisso). Ver `content-ideas-br`.
- Mediana com poucos Reels (`reels_na_amostra` < 8) é instável.
- Curtidas ocultas pelo dono vêm vazias (`posts_com_curtidas_ocultas`); a detecção de impulsionamento não funciona nesses posts.
- A API não informa Reels fixados, compartilhamentos, salvamentos nem alcance; não estime esses números.
