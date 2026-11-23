#!/usr/bin/env python3
"""Mede um roteiro: palavras faladas e duração estimada nas velocidades da diretriz.

  python3 medir_roteiro.py roteiro.txt
  echo "texto" | python3 medir_roteiro.py

Ignora marcações entre colchetes ([NA TELA: ...], [VERIFICAR: ...]) e linhas de rótulo
como "GANCHO —", "NA TELA:", "CHECKLIST:".
"""
import re
import sys

ROTULOS = ("PAUTA", "FORMATO", "NA TELA", "CHECKLIST", "MEDIDAS", "LEGENDA", "A PREPARAR", "ORIGEM", "POR QUE")


def falado(texto):
    texto = re.sub(r"\[[^\]]*\]", " ", texto)
    linhas = []
    for linha in texto.splitlines():
        s = linha.strip()
        if not s or s.upper().startswith(ROTULOS):
            continue
        s = re.sub(r"^(GANCHO|ROTEIRO|FECHAMENTO)\s*[—:-]*\s*(falado:)?", "", s, flags=re.I)
        s = s.split("| texto na tela")[0]
        linhas.append(s)
    return " ".join(linhas)


def main():
    texto = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    palavras = len(re.findall(r"\w+", falado(texto)))
    print(f"Palavras faladas: {palavras}")
    for vel, rotulo in ((3.0, "fala própria, ritmo calmo"), (3.2, "fala própria, ritmo típico"),
                        (3.5, "fala própria, ritmo rápido"), (3.7, "jurídico/econômico, rápido")):
        print(f"  a {vel:.1f} palavras/s ({rotulo}): ~{palavras / vel:.0f} s")


if __name__ == "__main__":
    main()
