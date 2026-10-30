#!/usr/bin/env python3
"""Verifica um teleprompter limpo (Versão A): duração, frases longas, expressões proibidas e ritmo.

Uso:
    python3 verificar_roteiro.py roteiro.txt [--ppm 190] [--max-palavras 15] [--pausa 0.1] [--alvo 60]

Entrada: texto puro. Blocos separados por linha em branco; cada linha é uma unidade de respiração.
Saída: tabela por bloco com tempo acumulado, alertas, painel de ritmo e resumo. Código de saída 1 se houver alertas.
"""
import argparse
import re
import sys
import unicodedata

PROIBIDAS = [
    # vícios de texto de IA
    "vamos falar sobre", "hoje eu vou falar", "neste video", "nesse video",
    "e importante ressaltar", "vale lembrar que", "vale destacar",
    "nesse contexto", "neste contexto", "diante desse cenario", "no cenario atual",
    "em suma", "em resumo", "concluindo",
    "mas aqui esta o ponto", "e ai que a coisa fica interessante", "spoiler",
    "isso diz muito sobre", "a pergunta que fica",
    "mergulhar", "desvendar", "jornada",
    # iscas de engajamento
    "voce nao vai acreditar", "fique ate o final", "ate o final do video",
    "comenta ai", "a verdade que escondem", "a midia nao mostra",
    "ninguem esta falando sobre",
]

ENCHIMENTO = ["simplesmente", "literalmente", "basicamente"]

CHAMADAS = ["segue", "siga", "compartilh", "comenta", "inscrev", "curt", "manda esse", "ativa o sino", "vira membro"]


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", sem_acento.lower())


def palavras(texto):
    return re.findall(r"[\wÀ-ÿ%$]+(?:[.,][\d]+)*", texto)


def frases(texto):
    partes = re.split(r"(?<=[.!?…])\s+|\n", texto)
    return [p.strip() for p in partes if p.strip()]


def fmt(segundos):
    return f"{int(segundos // 60)}:{segundos % 60:04.1f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo")
    ap.add_argument("--ppm", type=float, default=190, help="palavras por minuto do apresentador")
    ap.add_argument("--max-palavras", type=int, default=15, help="limite de palavras por frase")
    ap.add_argument("--pausa", type=float, default=0.1, help="segundos extras por quebra de linha (a velocidade medida já inclui as pausas naturais)")
    ap.add_argument("--alvo", type=float, default=60, help="duração-alvo em segundos")
    args = ap.parse_args()

    with open(args.arquivo, encoding="utf-8") as f:
        texto = f.read()

    if re.search(r"\[[^\]]*\]|^#", texto, re.M):
        print("ALERTA: há colchetes ou cabeçalhos; a Versão A deve conter só o texto falado.\n")

    blocos = [b.strip() for b in re.split(r"\n\s*\n", texto) if b.strip()]
    alertas = 0
    acumulado = 0.0
    total_palavras = 0

    print(f"{'Bloco':<6}{'Palavras':>9}{'Duração':>9}{'Início':>9}{'Fim':>9}  Primeira frase")
    for i, bloco in enumerate(blocos, 1):
        n = len(palavras(bloco))
        linhas = [l for l in bloco.splitlines() if l.strip()]
        dur = n / args.ppm * 60 + max(len(linhas) - 1, 0) * args.pausa
        inicio = acumulado
        acumulado += dur + args.pausa
        total_palavras += n
        primeira = linhas[0][:50] if linhas else ""
        print(f"{i:<6}{n:>9}{dur:>8.1f}s{fmt(inicio):>9}{fmt(inicio + dur):>9}  {primeira}")

    print()
    for i, bloco in enumerate(blocos, 1):
        for fr in frases(bloco):
            n = len(palavras(fr))
            if n > args.max_palavras:
                alertas += 1
                print(f"FRASE LONGA (bloco {i}, {n} palavras): {fr}")
        norm = normalizar(bloco)
        for termo in PROIBIDAS:
            if re.search(r"\b" + re.escape(termo) + r"\b", norm):
                alertas += 1
                print(f"EXPRESSÃO PROIBIDA (bloco {i}): \"{termo}\"")
        for termo in ENCHIMENTO:
            if re.search(r"\b" + termo + r"\b", norm):
                alertas += 1
                print(f"ENCHIMENTO (bloco {i}): \"{termo}\"")

    # Painel de ritmo
    todas = [fr for b in blocos for fr in frases(b)]
    tam = [len(palavras(fr)) for fr in todas]
    pr = sum(1 for a, b in zip(todas, todas[1:]) if a.endswith("?") and len(palavras(b)) <= 6)
    staccato, seq = 0, 0
    for n in tam:
        seq = seq + 1 if n <= 4 else 0
        if seq == 3:
            staccato += 1
    vistas = {}
    for fr in todas:
        chave = normalizar(fr).strip(" .!?")
        if 5 <= len(chave.split()) <= 14:
            vistas[chave] = vistas.get(chave, 0) + 1
    ancoras = [k for k, v in vistas.items() if v >= 2]
    chamadas = sorted({c for c in CHAMADAS if re.search(r"\b" + c, normalizar(blocos[-1] if blocos else ""))})
    print()
    print("RITMO")
    if tam:
        print(f"  Palavras por frase: média {sum(tam) / len(tam):.1f} (alvo 8 a 12)")
    print(f"  Pergunta-resposta: {pr} (alvo 2 a 4)")
    print(f"  Sequências em staccato (3+ frases de até 4 palavras): {staccato} (alvo 1 ou mais)")
    print(f"  Frase-âncora repetida: {ancoras[0] if ancoras else 'nenhuma'}")
    print(f"  Chamadas no último bloco: {', '.join(chamadas) if chamadas else 'nenhuma'}")
    if tam and sum(tam) / len(tam) > 12:
        alertas += 1
        print("  ALERTA: frases longas em média; quebre em frases menores.")
    if not ancoras:
        alertas += 1
        print("  ALERTA: nenhuma frase-âncora repetida (diga no meio e repita no fim).")
    if len(chamadas) > 2:
        alertas += 1
        print("  ALERTA: mais de 2 chamadas no fechamento.")

    duracao = max(acumulado - args.pausa, 0)
    print()
    print(f"Total: {total_palavras} palavras | {len(blocos)} blocos | duração estimada {duracao:.0f}s a {args.ppm:.0f} ppm")
    if duracao > args.alvo:
        alertas += 1
        excesso = (duracao - args.alvo) * args.ppm / 60
        print(f"ACIMA DO ALVO de {args.alvo:.0f}s: corte cerca de {excesso:.0f} palavras ou justifique a duração.")
    print("Estimativa provisória: confirme com a gravação e registre a duração real.")
    print(f"Alertas: {alertas}")
    sys.exit(1 if alertas else 0)


if __name__ == "__main__":
    main()
