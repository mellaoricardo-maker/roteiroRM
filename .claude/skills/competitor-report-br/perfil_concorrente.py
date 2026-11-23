#!/usr/bin/env python3
"""
competitor-report-br — coleta e pré-análise de UM perfil do Instagram pela API
oficial da Meta (Business Discovery), para o relatório de concorrente.

Baseado em `competitor-report` de creator-skills (c) 2026 Cristiano Capasso, MIT
(ver LICENSE-original). Mudanças: usa o motor da skill content-ideas-br (só API
oficial, sem navegador automatizado), chamadas à ação e mobilização em português
(link na bio, compartilhe, abaixo-assinado, Pix/doação, grupo de WhatsApp…),
menções e hashtags mais frequentes, dias e horários de postagem no fuso de
Brasília, sinalização de patrocínio nos outliers, comparação com a conta do
usuário (--eu) e transcrição em português.

  python3 perfil_concorrente.py <@conta|link> [--n 60] [--transcribe-top 0]
                                [--cookies "chrome:Profile 2"] [--eu @suaconta] [--out arquivo.json]
"""
import argparse
import json
import re
import statistics
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "content-ideas-br"))
try:
    from scan_concorrentes import ApiStop, analyse, business_discovery, graph_get, is_paid, transcribe  # noqa: E402
except ImportError:
    sys.exit("ERRO: esta skill usa o motor da skill content-ideas-br; as duas pastas precisam ficar lado a lado.")

try:
    from zoneinfo import ZoneInfo
    BRT = ZoneInfo("America/Sao_Paulo")
except Exception:  # sem base de fusos: Brasília sem horário de verão desde 2019
    BRT = timezone(timedelta(hours=-3))

DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

# Chamadas à ação / mobilização mais comuns em perfis políticos e de comunicação.
CTA_PATTERNS = {
    "link_na_bio": r"link na bio|link no perfil|link nos stories",
    "comente": r"\bcomente\b|\bcomenta\b|deixe (?:nos|aqui nos) coment",
    "comente_palavra": r"[Cc]omente [\"“']?[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3,}\b",
    "compartilhe": r"compartilh[ea]|mande (?:para|pra) (?:alguém|quem)|marque (?:alguém|quem|um amigo)",
    "siga": r"\bsiga\b|\bsegue\b(?: o perfil| a gente)|ative (?:as )?notifica",
    "salve": r"\bsalve (?:esse|este)|\bsalva (?:esse|este)",
    "assine_peticao": r"abaixo[- ]assinado|peti[cç][aã]o|assine\b",
    "doacao_pix": r"\bpix\b|doa[cç][aã]o|\bdoe\b|contribua|vaquinha",
    "grupo_canal": r"grupo (?:do|de) whats|canal (?:do|no) (?:whats|telegram)|telegram|lista de transmiss",
    "evento": r"\bato\b|manifesta[cç][aã]o|audi[eê]ncia p[uú]blica|live\b|ao vivo",
    "newsletter_site": r"newsletter|inscreva|cadastre",
}


def handle_of(arg):
    m = re.search(r"instagram\.com/([A-Za-z0-9._]+)", arg)
    return (m.group(1) if m else arg).lstrip("@").strip("/")


def website_info(url):
    """Título e descrição do site da bio (só leitura de uma página pública)."""
    if not url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read(400_000).decode("utf-8", "ignore")
            final = r.geturl()
        title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        desc = re.search(r'<meta[^>]+(?:name|property)=["\'](?:og:)?description["\'][^>]+content=["\'](.*?)["\']',
                         html, re.I)
        links = sorted(set(re.findall(r'href=["\'](https?://[^"\']+)["\']', html)))[:40]
        return {"final_url": final, "title": title and title.group(1).strip()[:200],
                "description": desc and desc.group(1).strip()[:400], "outbound_links": links}
    except Exception as e:
        return {"error": str(e)[:200]}


def slim(m):
    keep = ("permalink", "media_product_type", "media_type", "view_count", "like_count",
            "comments_count", "days_ago", "outlier", "caption", "timestamp")
    out = {k: m.get(k) for k in keep if k in m}
    if out.get("caption"):
        out["caption"] = out["caption"][:600]
    return out


def deep_analysis(profile):
    base = analyse(profile)  # define days_ago, outlier, mediana
    media = profile["media"]
    reels = base["reels"]
    med_rate = base["median_like_rate"]
    for m in reels:
        reason = is_paid(m, med_rate)
        if reason:
            m["paid_flag"] = reason

    likes = [m["like_count"] for m in media if m.get("like_count") is not None]
    hidden_likes = sum(1 for m in media if m.get("like_count") is None)
    captions = [m.get("caption") or "" for m in media]

    weekday, hour = Counter(), Counter()
    for m in media:
        if m.get("timestamp"):
            t = datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(BRT)
            weekday[DIAS[t.weekday()]] += 1
            hour[f"{t.hour:02d}h"] += 1

    ctas = {k: sum(1 for c in captions if re.search(p, c, 0 if k == "comente_palavra" else re.I))
            for k, p in CTA_PATTERNS.items()}
    mentions = Counter(h.lower() for c in captions for h in re.findall(r"@([A-Za-z0-9._]+)", c))
    hashtags = Counter(h.lower() for c in captions for h in re.findall(r"#(\w+)", c))

    top = sorted(reels, key=lambda m: m.get("outlier") or 0, reverse=True)
    organic_top = [m for m in top if not m.get("paid_flag")]
    non_reels = sorted([m for m in media if m not in reels and m.get("like_count")],
                       key=lambda m: m["like_count"], reverse=True)
    return {
        "posts_analisados": len(media),
        "mix_de_formatos": dict(Counter(m.get("media_product_type") or m.get("media_type") for m in media)),
        "posts_por_semana": base["posts_per_week"],
        "mediana_views_reels": base["median_reel_views"],
        "reels_na_amostra": base["reels_in_sample"],
        "mediana_curtidas": statistics.median(likes) if likes else None,
        "posts_com_curtidas_ocultas": hidden_likes,
        "top_reels_por_outlier": [slim(m) | ({"paid_flag": m["paid_flag"]} if m.get("paid_flag") else {})
                                  for m in top[:10]],
        "outliers_recentes_60d_organicos": [slim(m) for m in organic_top
                                            if m.get("days_ago") is not None and m["days_ago"] <= 60
                                            and (m.get("outlier") or 0) >= 2],
        "top_nao_reels_por_curtidas": [slim(m) for m in non_reels[:5]],
        "chamadas_a_acao": ctas,
        "palavras_de_comente": Counter(k.upper() for c in captions
                                       for k in re.findall(r"[Cc]omente [\"“']?([A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3,})\b", c)).most_common(10),
        "mencoes_frequentes": mentions.most_common(15),
        "hashtags_frequentes": hashtags.most_common(15),
        "postagens_por_dia_da_semana": dict(weekday.most_common()),
        "postagens_por_hora_brasilia": dict(sorted(hour.items())),
    }


def build_parser():
    ap = argparse.ArgumentParser(description="Coleta e pré-análise de um perfil do Instagram (API oficial).")
    ap.add_argument("perfil", help="@conta ou link do perfil")
    ap.add_argument("--n", type=int, default=60, help="posts lidos (padrão 60)")
    ap.add_argument("--transcribe-top", type=int, default=0,
                    help="transcrever os N maiores outliers orgânicos (exige transcribe-br e --cookies)")
    ap.add_argument("--cookies", default=None, help='navegador com conta SECUNDÁRIA logada, ex.: "chrome:Profile 2"')
    ap.add_argument("--whisper-model", default="medium")
    ap.add_argument("--eu", default=None, help="sua conta, para comparação (ex.: @seuperfil)")
    ap.add_argument("--sem-site", action="store_true", help="não visitar o site da bio")
    ap.add_argument("--out", default=None)
    return ap


def run(a, getter=graph_get, transcriber=transcribe, site=website_info):
    handle = handle_of(a.perfil)
    try:
        profile, err = business_discovery(handle, a.n, getter)
    except ApiStop as e:
        sys.exit(f"PARADA: {e}")
    if profile is None:
        sys.exit(f"Não foi possível ler @{handle}: {err}\n"
                 "Se for conta pessoal ou privada, a API oficial não alcança; esta versão não usa navegador automatizado.")

    result = {
        "handle": handle, "fonte": "API oficial da Meta (Business Discovery)",
        "coletado_em": datetime.now().isoformat(timespec="minutes"),
        "perfil": {k: v for k, v in profile.items() if k != "media"},
        "site": None if a.sem_site else site(profile.get("website")),
        "analise": deep_analysis(profile),
        "comparacao_conta_propria": None,
    }
    if a.eu:
        try:
            mine, _ = business_discovery(handle_of(a.eu), min(a.n, 50), getter)
        except ApiStop as e:
            mine = None
            result["comparacao_conta_propria"] = {"erro": str(e)}
        if mine:
            s = analyse(mine)
            result["comparacao_conta_propria"] = {
                "handle": handle_of(a.eu), "seguidores": mine.get("followers_count"),
                "mediana_views_reels": s["median_reel_views"], "posts_por_semana": s["posts_per_week"]}

    alvo = [m for m in result["analise"]["top_reels_por_outlier"] if not m.get("paid_flag")][: a.transcribe_top]
    for m in alvo:
        print(f"Transcrevendo {m['permalink']} …", file=sys.stderr)
        m["transcript"] = transcriber(m["permalink"], a.cookies, a.whisper_model)
    return result


def main():
    a = build_parser().parse_args()
    result = run(a)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        print(a.out)
    else:
        print(text)


if __name__ == "__main__":
    main()
