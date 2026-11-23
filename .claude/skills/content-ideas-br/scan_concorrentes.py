#!/usr/bin/env python3
"""
content-ideas-br — varre uma lista de contas do Instagram pela API oficial da Meta
(Business Discovery) e devolve os Reels recentes que superaram a mediana de views
da própria conta, sem os patrocinados/impulsionados, opcionalmente transcritos.

Baseado em `content-ideas` + `competitor-report` de creator-skills (c) 2026
Cristiano Capasso, MIT (ver LICENSE-original). Mudanças: autocontido (não depende
da pasta competitor-report nem de navegador automatizado), filtros de patrocínio
em português e para conteúdo político, salvamento parcial a cada conta, parada
limpa em limite de uso ou token vencido, conta própria como referência (--eu) e
transcrição em português pela skill transcribe-br.

  python3 scan_concorrentes.py [--lista arquivo.md] [--days 30] [--min-outlier 2]
                               [--top 15] [--transcribe 0] [--cookies chrome] [--eu @handle]
                               [--out arquivo.json]

Configuração (variáveis de ambiente ou ~/.config/content-ideas-br/.env):
  IG_GRAPH_TOKEN, IG_GRAPH_USER_ID   (ver SKILL.md, seção Configuração)
  IG_GRAPH_VERSION                   (opcional, padrão v23.0)
"""
import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_DIR = Path(os.environ.get("CONTENT_IDEAS_BR_HOME", Path.home() / ".config" / "content-ideas-br"))
LEGACY_ENV = Path.home() / ".creator-skills" / ".env"
DEFAULT_LIST = CONFIG_DIR / "concorrentes.md"
MEDIA_FIELDS = "id,caption,timestamp,media_type,media_product_type,like_count,comments_count,view_count,permalink"

# Patrocínio e publicidade (pt + en). Só hashtags e expressões inequívocas: em conteúdo
# político, palavras soltas como "publicidade" ou "impulsionada" costumam ser o ASSUNTO.
# Impulsionamento sem marcação na legenda é pego pela regra de curtidas/views (is_paid).
PAID = re.compile(
    r"#(?:ad|ads|publi|publipost|publicidade|patrocinado|parceriapaga|sponsored|impulsionado|\w*partner)\b"
    r"|parceria paga|paid partnership|conte[uú]do (?:pago|patrocinado)",
    re.I,
)
RATE_LIMIT_CODES = {4, 17, 32, 613}
TOKEN_CODES = {190, 102}


def env(key):
    if os.environ.get(key):
        return os.environ[key]
    for path in (CONFIG_DIR / ".env", LEGACY_ENV):
        if path.exists():
            for line in path.read_text().splitlines():
                if line.startswith(key + "="):
                    return line.split("=", 1)[1].strip().strip('"')
    return None


class ApiStop(Exception):
    """Erro que impede continuar a varredura (limite de uso ou token)."""


def graph_get(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return json.load(e)
        except Exception:
            return {"error": {"message": f"HTTP {e.code}", "code": e.code}}
    except Exception as e:
        return {"error": {"message": str(e)[:200], "code": -1}}


def business_discovery(handle, n, getter=graph_get):
    token, uid = env("IG_GRAPH_TOKEN"), env("IG_GRAPH_USER_ID")
    if not token or not uid:
        raise ApiStop(f"IG_GRAPH_TOKEN/IG_GRAPH_USER_ID ausentes (coloque em {CONFIG_DIR / '.env'}).")
    graph = f"https://graph.facebook.com/{env('IG_GRAPH_VERSION') or 'v23.0'}"
    profile, media, after = None, [], None
    while len(media) < n:
        page = f"media.limit({min(50, n - len(media))})" + (f".after({after})" if after else "")
        fields = (f"business_discovery.username({handle}){{username,name,biography,followers_count,"
                  f"media_count,{page}{{{MEDIA_FIELDS}}}}}")
        d = getter(f"{graph}/{uid}?" + urllib.parse.urlencode({"fields": fields, "access_token": token}))
        if "error" in d:
            err = d["error"]
            code = err.get("code")
            if code in RATE_LIMIT_CODES:
                raise ApiStop(f"limite de uso da API atingido (código {code}). Espere ~1 hora e rode de novo.")
            if code in TOKEN_CODES:
                raise ApiStop("token inválido ou acesso a dados vencido (a Meta corta a cada 90 dias). "
                              "Gere um novo token (SKILL.md, Configuração, passos 3–6).")
            if profile is None:
                return None, err.get("message", "erro desconhecido")
            break
        bd = d.get("business_discovery", {})
        profile = profile or {k: v for k, v in bd.items() if k != "media"}
        media += bd.get("media", {}).get("data", [])
        after = bd.get("media", {}).get("paging", {}).get("cursors", {}).get("after")
        if not after:
            break
    profile["media"] = media
    return profile, None


def analyse(profile):
    now = datetime.now(timezone.utc)
    for m in profile["media"]:
        ts = m.get("timestamp")
        m["days_ago"] = (now - datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")).days if ts else None
    reels = [m for m in profile["media"] if m.get("media_product_type") == "REELS" and m.get("view_count")]
    med = statistics.median(m["view_count"] for m in reels) if reels else None
    for m in reels:
        m["outlier"] = round(m["view_count"] / med, 2) if med else None
    rates = [m["like_count"] / m["view_count"] for m in reels if m.get("like_count") is not None]
    dated = [m["days_ago"] for m in profile["media"] if m["days_ago"] is not None]
    weeks = max((max(dated) - min(dated)) / 7, 1) if dated else None
    return {
        "reels": reels,
        "median_reel_views": med,
        "median_like_rate": statistics.median(rates) if rates else None,
        "reels_in_sample": len(reels),
        "posts_per_week": round(len(dated) / weeks, 1) if weeks else None,
    }


def is_paid(m, med_rate):
    if PAID.search(m.get("caption") or ""):
        return "legenda indica publi/impulsionamento"
    if med_rate and m.get("like_count") is not None and m["view_count"]:
        if m["like_count"] / m["view_count"] < 0.25 * med_rate:
            return "curtidas/views muito abaixo do normal da conta (provável impulsionamento)"
    return None


def handles(path):
    """Linhas que começam com @ (ignora '> @conta', estacionadas)."""
    return [m.group(1) for line in Path(path).read_text(encoding="utf-8").splitlines()
            if (m := re.match(r"@([A-Za-z0-9._]+)", line.strip()))]


def transcribe(url, cookies, model):
    script = HERE.parent / "transcribe-br" / "transcribe.sh"
    if not script.exists():
        return {"error": "skill transcribe-br não encontrada ao lado desta"}
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["bash", str(script), url, "-m", model, "-o", tmp]
        if cookies:
            cmd += ["-c", cookies]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        txt = Path(tmp) / "transcript.txt"
        srt = Path(tmp) / "transcript.srt"
        if r.returncode != 0 or not txt.exists():
            return {"error": (r.stderr or "falha").strip()[-200:]}
        return {"text": txt.read_text().strip(),
                "first_line": next((l for l in srt.read_text().splitlines()
                                    if l.strip() and not l.strip().isdigit() and "-->" not in l), "")
                if srt.exists() else ""}


def save(out, result):
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text, encoding="utf-8")
    return text


def run(a, getter=graph_get, transcriber=transcribe):
    result = {"generated_at": datetime.now().isoformat(timespec="minutes"),
              "params": {k: v for k, v in vars(a).items() if k != "out"},
              "own_account": None, "accounts_ok": [], "accounts_failed": [],
              "dropped_paid": [], "candidates": [], "stopped_early": None}
    candidates = []
    try:
        if a.eu:
            p, err = business_discovery(a.eu.lstrip("@"), a.per_account, getter)
            if p:
                s = analyse(p)
                result["own_account"] = {"handle": a.eu.lstrip("@"), "followers": p.get("followers_count"),
                                         "median_reel_views": s["median_reel_views"],
                                         "posts_per_week": s["posts_per_week"]}
        hs = handles(a.lista)
        for i, h in enumerate(hs, 1):
            print(f"[{i}/{len(hs)}] @{h}", file=sys.stderr, flush=True)
            profile, err = business_discovery(h, a.per_account, getter)
            if profile is None:
                result["accounts_failed"].append({"handle": h, "error": err})
                continue
            s = analyse(profile)
            result["accounts_ok"].append({"handle": h, "followers": profile.get("followers_count"),
                                          "median_reel_views": s["median_reel_views"],
                                          "reels_in_sample": s["reels_in_sample"],
                                          "posts_per_week": s["posts_per_week"]})
            picked = 0
            for m in sorted(s["reels"], key=lambda m: m["outlier"] or 0, reverse=True):
                if picked >= a.max_per_account:
                    break
                if m["days_ago"] is None or m["days_ago"] > a.days or (m["outlier"] or 0) < a.min_outlier:
                    continue
                reason = is_paid(m, s["median_like_rate"])
                if reason:
                    result["dropped_paid"].append({"handle": h, "permalink": m["permalink"], "reason": reason})
                    continue
                picked += 1
                candidates.append({
                    "handle": h, "followers": profile.get("followers_count"),
                    "account_median_views": s["median_reel_views"],
                    "baseline_sample": s["reels_in_sample"],
                    "permalink": m["permalink"], "views": m["view_count"], "outlier": m["outlier"],
                    "days_ago": m["days_ago"], "likes": m.get("like_count"),
                    "comments": m.get("comments_count"), "caption": m.get("caption") or "",
                })
            result["candidates"] = sorted(candidates, key=lambda c: c["outlier"], reverse=True)
            save(a.out, result)  # salvamento parcial
            time.sleep(a.pause)
    except ApiStop as e:
        result["stopped_early"] = str(e)
        print(f"PARADA: {e}", file=sys.stderr)

    candidates.sort(key=lambda c: c["outlier"], reverse=True)
    result["candidates"] = candidates[: a.top]
    for c in result["candidates"][: a.transcribe]:
        print(f"Transcrevendo @{c['handle']} {c['permalink']}", file=sys.stderr, flush=True)
        c["transcript"] = transcriber(c["permalink"], a.cookies, a.whisper_model)
    return result


def build_parser():
    ap = argparse.ArgumentParser(description="Reels fora da curva dos concorrentes (API oficial da Meta).")
    ap.add_argument("--lista", default=str(DEFAULT_LIST), help=f"lista de contas (padrão: {DEFAULT_LIST})")
    ap.add_argument("--days", type=int, default=30, help="idade máxima dos Reels em dias (padrão 30)")
    ap.add_argument("--per-account", type=int, default=30, help="posts lidos por conta (padrão 30)")
    ap.add_argument("--min-outlier", type=float, default=2.0, help="views ÷ mediana mínima (padrão 2)")
    ap.add_argument("--max-per-account", type=int, default=3, help="máximo de Reels por conta (padrão 3)")
    ap.add_argument("--top", type=int, default=15, help="candidatos mantidos (padrão 15)")
    ap.add_argument("--transcribe", type=int, default=0,
                    help="quantos transcrever (padrão 0; exige transcribe-br e, no Instagram, --cookies)")
    ap.add_argument("--cookies", default=None,
                    help='navegador logado para baixar os Reels, ex.: chrome ou "chrome:Profile 2" (use conta secundária)')
    ap.add_argument("--whisper-model", default="medium")
    ap.add_argument("--eu", default=None, help="sua conta, para comparar medianas (ex.: @seuperfil)")
    ap.add_argument("--pause", type=float, default=1.0, help="pausa entre contas em segundos")
    ap.add_argument("--out", default=None, help="arquivo JSON de saída (salvo também a cada conta)")
    return ap


def main():
    a = build_parser().parse_args()
    if not Path(a.lista).exists():
        sys.exit(f"Lista não encontrada: {a.lista}. Copie concorrentes.exemplo.md para lá e edite.")
    result = run(a)
    text = save(a.out, result)
    print(a.out if a.out else text)


if __name__ == "__main__":
    main()
