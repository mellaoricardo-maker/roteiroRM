# Direção de Interpretação, Teleprompter, Edição e Referências

## Sumário
1. Direção de interpretação
2. Teleprompter: Versões A e B
3. Direção audiovisual 9:16
4. Aprendizado com referências

## 1. Direção de interpretação

Ficha por frase ou pequeno bloco, com os campos:

| Bloco | Intenção | Tom | Velocidade | Ênfase (palavra) | Pausa | Expressão | Olhar | Corpo | Transição |
|---|---|---|---|---|---|---|---|---|---|

- **Intenção:** o que a frase precisa fazer com o espectador (situar, intrigar, explicar, ponderar, concluir).
- **Tom:** curiosidade, seriedade, surpresa genuína, preocupação fundamentada, serenidade, convicção, humor apropriado.
- **Velocidade:** lenta, natural, ágil.
- **Ênfase:** uma palavra por frase, no máximo duas. Ênfase em tudo é ênfase em nada.
- **Pausa:** antes do número ou da informação-chave; depois da pergunta.
- **Olhar:** na lente na maior parte do tempo; desviar brevemente ao "pensar" ou ao apontar um elemento gráfico.
- **Corpo:** só quando o gesto ilustra (contar nos dedos, mostrar tamanho). Nada de gestos repetitivos.
- **Transição:** como entrar na frase seguinte (respirar, sorriso leve, virada de tom).

Regras:

- Emoção proporcional à evidência. Nada de indignação artificial ou dramatização.
- O apresentador soa como quem entende e acredita no que diz.
- **Fale com uma pessoa, não com uma multidão.** Imagine um amigo inteligente do outro lado da lente.
- Variação de intensidade: a energia sobe na abertura e na conclusão, baixa um pouco no contraponto (sinal de ponderação).

## 2. Teleprompter: Versões A e B

### Versão A — Teleprompter limpo

- Apenas as palavras faladas.
- Sem cabeçalhos, instruções, indicações de câmera ou colchetes.
- Uma frase ou unidade de respiração por linha; linha em branco entre blocos.
- Pontuação que ajude a respirar e interpretar (vírgula para pausa curta, ponto para pausa, reticências com parcimônia).
- Números por extenso quando a leitura puder travar ("dois vírgula três bilhões" ou "2,3 bilhões", conforme o costume do apresentador; padrão: algarismos com unidade por extenso, "2,3 bilhões de reais").
- Oralidade brasileira ("pra" e "tá" só se fizerem parte da voz do apresentador).
- Salve também como `.txt` puro para colar no aplicativo de teleprompter.

### Versão B — Direção de gravação

- As mesmas frases, na mesma ordem e com os mesmos números de bloco.
- Para cada bloco: interpretação, ênfase (em **negrito** na própria frase), pausas (marcadas com `/` curta e `//` longa), enquadramento e observações de gravação.
- Indique blocos que podem ser gravados separadamente (facilita cortes e regravação).

**Sincronização:** depois de escrever, confira que A e B têm o mesmo número de blocos e o mesmo texto falado. O script `verificar_roteiro.py` aceita a Versão A e estima tempo por bloco, servindo de base para os tempos do plano de edição.

## 3. Direção audiovisual 9:16

Padrões visuais observados nos referentes (legenda dinâmica com palavra destacada, tela dividida, print com número circulado, cartela de número, preto e branco na crítica, objeto de cena): ver `estilo-e-tecnicas.md` §8.

Folha de edição por momento:

| Momento | Início–fim | Fala | Enquadramento | Corte | Texto na tela | Imagem / documento / gráfico / B-roll (com fonte) | Som | Música |
|---|---|---|---|---|---|---|---|---|

Diretrizes:

- **Primeiro quadro:** já com o rosto ou a imagem-chave e o texto de abertura. Ele frequentemente vira a capa.
- **Zonas seguras:** mantenha textos e rosto fora da faixa inferior (aprox. 20–25% da altura, onde ficam legenda da plataforma e botões) e da lateral direita (ícones). Margem superior também reduzida pela interface.
- **Legendas:** grandes, alto contraste, 1 a 2 linhas, revisadas palavra a palavra (nomes, números e siglas são os erros mais comuns).
- **Enquadramento:** plano médio-fechado (peito para cima) como base; aproximação pontual para ênfase. Olhos no terço superior.
- **Cortes:** retire respirações longas e erros. Cortes e zooms quando mudarem a informação, não por hábito. Inteligibilidade acima de ritmo.
- **Documentos na tela:** mostre o documento real (print do Diário Oficial, tabela oficial) com destaque no trecho citado e fonte visível ("Fonte: DOM-SP, 12/10/2026").
- **Gráficos:** simples, uma mensagem por gráfico, eixo honesto (barras começam no zero), fonte e data visíveis.
- **Imagens sintéticas:** nunca como evidência de acontecimento real. Ilustração gerada por IA recebe rótulo visível. Nada de voz ou rosto sintético de pessoa real.
- **Declarações públicas:** nunca recorte retirando o trecho que muda o sentido. Cite a data e o contexto da fala.
- **Som:** efeitos só quando agregam significado. Música baixa, sem competir com a voz, da biblioteca licenciada da plataforma ou livre de direitos.
- **Áudio:** voz limpa é requisito; microfone de lapela ou próximo; sem eco.

## 4. Aprendizado com referências

Repertório de observação informado pelo usuário: Caio Coppolla, Samer Agi, Leo Siqueira, Nine Borg, Renan Santos, Raphael Lima, Deltan Dallagnol, Marina Helena e Ostermann. A análise de 12 vídeos de parte deles já está consolidada em `estilo-e-tecnicas.md`; novas análises devem atualizar aquele arquivo (técnicas, tabela de velocidade, o que não copiar).

Não pressuponha ter visto os vídeos deles. Só analise o que for fornecido (vídeo, link acessível ou transcrição verificável) e diga quando a análise se baseia apenas em transcrição (sem acesso a voz, pausas e imagem).

Ao receber material, examine:

- Abertura e promessa narrativa.
- Sequência de argumentos.
- Vocabulário e ritmo (palavras por minuto, se der para medir).
- Analogias.
- Silêncios e pausas.
- Variação de intensidade vocal.
- Enquadramento e cortes.
- Legendas, gráficos e B-roll.
- Conclusão e fechamento.
- Como lidam (ou não) com contraponto e fontes.

Entregue: técnicas gerais transferíveis, o que **não** combina com a voz do apresentador e um exercício prático. Não copie bordões, identidade visual, estrutura integral de um vídeo específico ou personagem de outro comunicador.
