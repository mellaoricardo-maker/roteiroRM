#!/usr/bin/env python3
"""
content-team-br — partes da skill que não devem ser deixadas a adivinhação.
Só API oficial da Meta (motor da skill content-ideas-br); sem navegador automatizado.

  python3 equipe.py check                                  # yt-dlp, ffmpeg, whisper e token presentes?
  python3 equipe.py voz RUN --eu @conta [--cookies X]      # seu perfil + 3 Reels seus transcritos (amostra de voz)
  python3 equipe.py candidatas RUN --eu @conta [--lista L] [--extra @a @b]
                                                           # contas mencionadas por você e pela lista,
                                                           # conferidas na API (existe? bio? mediana?)

A classificação dos Reels e a transcrição dos escolhidos usam scan_concorrentes.py
(content-ideas-br). Baseado em `content-team` de creator-skills (c) 2026 Cristiano
Capasso, MIT (ver LICENSE-original).
"""
import argparse
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "content-ideas-br"))
try:
    from scan_concorrentes import (ApiStop, analyse, business_discovery, env, graph_get,  # noqa: E402
                                   handles, transcribe)
except ImportError:
    sys.exit("ERRO: esta skill usa o motor da skill content-ideas-br; as duas pastas precisam ficar lado a lado.")

TOOLS = ("yt-dlp", "ffmpeg", "whisper")
MENTION = re.compile(r"(?<![\w.])@([A-Za-z0-9._]{2,30})")


def clean(h):
    return h.lstrip("@").strip().rstrip(".").lower()


def cmd_check(_a):
    missing = [t for t in TOOLS if not shutil.which(t)]
    token = bool(env("IG_GRAPH_TOKEN") and env("IG_GRAPH_USER_ID"))
    print(json.dumps({"ferramentas_faltando": missing, "token_configurado": token,
                      "transcribe_br": (HERE.parent / "transcribe-br" / "transcribe.sh").exists()},
                     ensure_ascii=False))
    if missing or not token:
        sys.exit(10)


def cmd_voz(a, getter=graph_get, transcriber=transcribe):
    run = Path(a.run).expanduser()
    (run / "eu").mkdir(parents=True, exist_ok=True)
    me = clean(a.eu)
    try:
        profile, err = business_discovery(me, a.n, getter)
    except ApiStop as e:
        sys.exit(f"PARADA: {e}")
    if not profile:
        sys.exit(f"Não foi possível ler @{me}: {err}")
    s = analyse(profile)
    reels = s["reels"]
    by_views = sorted(reels, key=lambda m: m["view_count"], reverse=True)[:2]
    recent = sorted((m for m in reels if m.get("days_ago") is not None), key=lambda m: m["days_ago"])[:1]
    chosen = list({m["permalink"]: m for m in by_views + recent}.values())

    for m in chosen:
        m["transcript"] = transcriber(m["permalink"], a.cookies, a.whisper_model) if a.cookies else \
            {"error": "sem --cookies: transcrição não feita"}

    out = {
        "handle": me,
        "perfil": {k: v for k, v in profile.items() if k != "media"},
        "mediana_views_reels": s["median_reel_views"],
        "posts_por_semana": s["posts_per_week"],
        "legendas_recentes": [(m.get("caption") or "")[:500] for m in profile["media"][:15]],
        "reels_amostra_de_voz": [{k: m.get(k) for k in ("permalink", "view_count", "days_ago", "caption", "transcript")}
                                 for m in chosen],
    }
    (run / "eu" / "perfil.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(run / "eu" / "perfil.json")
    return out


def cmd_candidatas(a, getter=graph_get):
    """Junta @menções das suas legendas e das contas da lista, mais --extra, e confere cada uma na API."""
    run = Path(a.run).expanduser()
    run.mkdir(parents=True, exist_ok=True)
    me = clean(a.eu)
    origem = {}
    seen_lista = set()
    if a.lista and Path(a.lista).exists():
        for h in handles(a.lista):
            seen_lista.add(clean(h))
    # contas estacionadas ("> @conta") não voltam como candidatas
    parked = set()
    if a.lista and Path(a.lista).exists():
        parked = {clean(m.group(1)) for line in Path(a.lista).read_text(encoding="utf-8").splitlines()
                  if (m := re.match(r">\s*@([A-Za-z0-9._]+)", line.strip()))}

    mentions = Counter()
    fontes = [me] + sorted(seen_lista)[: a.max_fontes]
    stopped = None
    checked = []
    try:
        for src in fontes:
            p, _ = business_discovery(src, 30, getter)
            if not p:
                continue
            for m in p["media"]:
                for h in MENTION.findall(m.get("caption") or ""):
                    h = clean(h)
                    mentions[h] += 1
                    origem.setdefault(h, set()).add(src)
        for h in a.extra or []:
            h = clean(h)
            mentions[h] += 0
            origem.setdefault(h, set()).add("sugerida (conferir)")

        pool = [h for h, _ in mentions.most_common() if h != me and h not in seen_lista and h not in parked]
        for h in pool[: a.max_checar]:
            p, err = business_discovery(h, 30, getter)
            if not p:
                checked.append({"handle": h, "ok": False, "erro": err, "origem": sorted(origem[h])})
                continue
            s = analyse(p)
            checked.append({"handle": h, "ok": True, "nome": p.get("name"), "bio": p.get("biography"),
                            "site": p.get("website"), "seguidores": p.get("followers_count"),
                            "mediana_views_reels": s["median_reel_views"], "reels_na_amostra": s["reels_in_sample"],
                            "mencoes": mentions[h], "origem": sorted(origem[h])})
    except ApiStop as e:
        stopped = str(e)

    out = {"eu": me, "contas_da_lista": sorted(seen_lista), "candidatas": checked, "parou_antes": stopped}
    (run / "candidatas.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(run / "candidatas.json")
    return out


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    v = sub.add_parser("voz")
    v.add_argument("run")
    v.add_argument("--eu", required=True)
    v.add_argument("--n", type=int, default=30)
    v.add_argument("--cookies", default=None, help='navegador com conta SECUNDÁRIA logada, ex.: "chrome:Profile 2"')
    v.add_argument("--whisper-model", default="medium")
    c = sub.add_parser("candidatas")
    c.add_argument("run")
    c.add_argument("--eu", required=True)
    c.add_argument("--lista", default=str(Path.home() / ".config" / "content-ideas-br" / "concorrentes.md"))
    c.add_argument("--extra", nargs="*", help="contas sugeridas (por você ou pelo Claude) para conferir")
    c.add_argument("--max-fontes", type=int, default=10, help="contas da lista cujas legendas são lidas")
    c.add_argument("--max-checar", type=int, default=20, help="candidatas conferidas na API")
    return ap


def main():
    a = build_parser().parse_args()
    {"check": cmd_check, "voz": cmd_voz, "candidatas": cmd_candidatas}[a.cmd](a)


if __name__ == "__main__":
    main()
