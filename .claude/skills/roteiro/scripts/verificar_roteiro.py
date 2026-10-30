#!/usr/bin/env python3
"""Verifica um teleprompter limpo (Versão A): duração estimada, frases longas e expressões proibidas.

Uso:
    python3 verificar_roteiro.py roteiro.txt [--ppm 155] [--max-palavras 18] [--pausa 0.5] [--alvo 60]

Entrada: texto puro. Blocos separados por linha em branco; cada linha é uma unidade de respiração.
Saída: tabela por bloco com tempo acumulado, alertas e resumo. Código de saída 1 se houver alertas.
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
    ap.add_argument("--ppm", type=float, default=155, help="palavras por minuto do apresentador")
    ap.add_argument("--max-palavras", type=int, default=18, help="limite de palavras por frase")
    ap.add_argument("--pausa", type=float, default=0.5, help="segundos somados por quebra de linha entre frases")
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
