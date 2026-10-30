# Métricas, Plano de Verificação e Experimentos

## 1. Plano de verificação pós-publicação (item 12 da entrega)

Para cada roteiro, defina antes de publicar:

- **Hipótese do vídeo:** o que se espera que este vídeo teste (ex.: "abertura com documento na tela retém mais nos 3 primeiros segundos que abertura com pergunta").
- **Variável testada:** apenas uma (abertura, duração, estrutura, interpretação, edição, horário ou tema).
- **Métricas a coletar e quando:** 24 h, 72 h e 7 dias após a publicação, nas três plataformas.
- **Base de comparação:** mediana dos últimos 5 a 10 vídeos comparáveis da mesma conta (mesmo formato e duração próxima).

## 2. Métricas a comparar

- Retenção inicial (proporção que passa dos primeiros segundos, conforme a plataforma informa).
- Tempo médio assistido.
- Percentual médio assistido.
- Compartilhamentos/envios por alcance.
- Salvamentos por alcance, quando disponíveis.
- Comentários substantivos (que discutem o conteúdo), contados à parte dos genéricos.
- Seguidores obtidos.
- Alcance de não seguidores.
- Desempenho relativo à mediana da conta.

Cuidados:

- Cada plataforma define e conta métricas de forma diferente (ex.: o que é "visualização"). Compare dentro da mesma plataforma.
- Use razões (por alcance), não números absolutos, para comparar vídeos com alcances diferentes.
- Prefira mediana à média: um vídeo fora da curva distorce a média.

## 3. Análise

Compare por assunto, duração, formato, período e plataforma.

- Formule **hipóteses** de melhoria, não relações causais que os dados não permitem.
- Diferenças pequenas em poucos vídeos costumam ser ruído. Só trate como padrão o que se repete em vários vídeos comparáveis.
- Considere fatores externos: assunto em alta, dia da semana, mudança da plataforma, impulsionamento, compartilhamento por perfil grande.
- Não declare fórmula vencedora com base em um único vídeo.

## 4. Próximo experimento

Proponha um experimento por ciclo:

- Mude **uma** variável, mantendo as demais o mais estáveis possível.
- Defina o que contaria como sinal ("percentual assistido acima da mediana em pelo menos 3 de 4 vídeos").
- Quando a plataforma oferecer teste nativo (ex.: versões de teste exibidas a não seguidores), prefira-o, porque reduz a variação de público.

## 5. Registro de experimentos

Mantenha o registro em `roteiros/registro-experimentos.md` (crie se não existir) com esta tabela:

| Data | Vídeo (slug) | Plataforma | Variável testada | Hipótese | Duração real | Retenção inicial | % assistido | Envios/alcance | Salvos/alcance | Comentários substantivos | Seguidores | Alcance não seguidores | vs. mediana | Leitura (hipótese) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Registre também a duração real gravada e as palavras do teleprompter, para recalibrar a velocidade de fala no perfil.

Quando um padrão se repetir em vários experimentos, promova-o para "Aprendizados acumulados" no perfil do apresentador, com o número de vídeos que o sustentam.
