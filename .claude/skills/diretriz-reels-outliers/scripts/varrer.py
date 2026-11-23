#!/usr/bin/env python3
"""Varredura de contraponto: busca vídeos recentes por termo no Instagram (Reels),
YouTube e TikTok via ScrapeCreators e devolve candidatos ordenados por views.

  python3 varrer.py "Haddad imposto" "Moraes redes sociais" --dias 3
  python3 varrer.py --arquivo termos.txt --dias 3 --fontes ig,tt --out candidatos.json

Custo: 1 crédito por termo e por fonte. Sem ScrapeCreators disponível (fora do Claude Code
com o ambiente configurado), o script avisa e a varredura segue só pela busca na web.
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

API = "https://api.scrapecreators.com"
AGORA = datetime.now(timezone.utc)


def get(path, **params):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            return json.load(r), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)[:120]


def parse_data(v):
    """Aceita timestamp (segundos) ou texto ISO 8601."""
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v, timezone.utc)
    if isinstance(v, str) and v:
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def dias_desde(dt):
    return round((AGORA - dt).total_seconds() / 86400, 1) if dt else None


def instagram(termo):
    d, err = get("v2/instagram/reels/search", query=termo)
    if err:
        return [], err, None
    out = []
    for r in d.get("reels") or []:
        dt = parse_data(r.get("taken_at"))
        out.append({"fonte": "instagram", "url": r.get("url"), "autor": (r.get("owner") or {}).get("username"),
                    "seguidores": None, "views": r.get("video_view_count"), "dias": dias_desde(dt),
                    "duracao_s": round(r.get("video_duration") or 0), "texto": (r.get("caption") or "")[:300]})
    return out, None, d.get("credits_remaining")


def youtube(termo):
    d, err = get("v1/youtube/search", query=termo)
    if err:
        return [], err, None
    out = []
    for v in (d.get("videos") or []) + (d.get("shorts") or []):
        dt = parse_data(v.get("publishedTime"))  # aproximada: o YouTube informa "há 3 dias"
        ch = v.get("channel") or {}
        out.append({"fonte": "youtube" + ("-short" if v.get("type") == "short" else ""), "url": v.get("url"),
                    "autor": ch.get("handle") or ch.get("title"), "seguidores": None,
                    "views": int(v.get("viewCountInt") or 0), "dias": dias_desde(dt),
                    "duracao_s": int(v.get("lengthSeconds") or 0), "texto": (v.get("title") or "")[:300]})
    return out, None, d.get("credits_remaining")


def tiktok(termo):
    d, err = get("v1/tiktok/search/keyword", query=termo)
    if err:
        return [], err, None
    out = []
    for it in d.get("search_item_list") or []:
        a = it.get("aweme_info", it)
        dt = parse_data(a.get("create_time"))
        au = a.get("author") or {}
        out.append({"fonte": "tiktok", "url": (a.get("share_url") or "").split("?")[0],
                    "autor": au.get("unique_id"), "seguidores": au.get("follower_count"),
                    "views": (a.get("statistics") or {}).get("play_count"), "dias": dias_desde(dt),
                    "duracao_s": round(((a.get("video") or {}).get("duration") or 0) / 1000),
                    "texto": (a.get("desc") or "")[:300]})
    return out, None, d.get("credits_remaining")


FONTES = {"ig": instagram, "yt": youtube, "tt": tiktok}


def main():
    ap = argparse.ArgumentParser(description="Varredura de contraponto (ScrapeCreators).")
    ap.add_argument("termos", nargs="*", help='termos no formato "[nome] [tema]"')
    ap.add_argument("--arquivo", help="arquivo com um termo por linha")
    ap.add_argument("--dias", type=float, default=3, help="idade máxima em dias (padrão 3)")
    ap.add_argument("--fontes", default="ig,yt,tt", help="ig,yt,tt (padrão: as três)")
    ap.add_argument("--min-views", type=int, default=5000, help="views mínimas (padrão 5.000)")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--incluir-sem-data", action="store_true",
                    help="manter resultados sem data (por padrão são descartados)")
    ap.add_argument("--out", help="salvar candidatos em JSON")
    a = ap.parse_args()

    termos = list(a.termos)
    if a.arquivo:
        termos += [l.strip() for l in open(a.arquivo, encoding="utf-8") if l.strip() and not l.startswith("#")]
    if not termos:
        sys.exit("Informe ao menos um termo.")
    fontes = [f.strip() for f in a.fontes.split(",") if f.strip() in FONTES]
    print(f"{len(termos)} termos × {len(fontes)} fontes = ~{len(termos) * len(fontes)} créditos", file=sys.stderr)

    jobs = [(t, f) for t in termos for f in fontes]
    itens, erros, creditos, sem_data = {}, [], None, 0
    with ThreadPoolExecutor(5) as ex:
        for (t, f), (res, err, cred) in zip(jobs, ex.map(lambda j: FONTES[j[1]](j[0]), jobs)):
            if err:
                erros.append(f"{f} / {t}: {err}")
            if cred is not None:
                creditos = cred if creditos is None else min(creditos, cred)
            for r in res:
                if not r["url"] or (r["views"] or 0) < a.min_views:
                    continue
                if r["dias"] is None and not a.incluir_sem_data:
                    sem_data += 1
                    continue
                if r["dias"] is not None and r["dias"] > a.dias:
                    continue
                r["termo"] = t
                itens.setdefault(r["url"], r)

    if erros and not itens:
        print("ScrapeCreators indisponível ou sem resultado (" + "; ".join(erros[:3]) +
              "). Siga a varredura pela busca na web e pelas fontes oficiais.", file=sys.stderr)
    ordem = sorted(itens.values(), key=lambda r: -(r["views"] or 0))[: a.top]
    for r in ordem:
        seg = f"{r['seguidores']:,} seg" if r["seguidores"] else ""
        print(f"{r['views'] or 0:>11,} views | {r['dias']}d | {r['fonte']:<13} @{r['autor']} {seg} | {r['url']}\n"
              f"            [{r['termo']}] {r['texto'][:140].replace(chr(10), ' ')}")
    if sem_data:
        print(f"\n{sem_data} resultados sem data descartados (use --incluir-sem-data para ver).", file=sys.stderr)
    if creditos is not None:
        print(f"\nCréditos ScrapeCreators restantes: {creditos}", file=sys.stderr)
    if erros:
        print(f"Falhas: {len(erros)} ({'; '.join(erros[:3])})", file=sys.stderr)
    if a.out:
        json.dump(ordem, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
