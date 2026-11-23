#!/usr/bin/env python3
"""
Outliers BR — detector de vídeos "fora da curva" no YouTube, adaptado para
conteúdo brasileiro e para Shorts.

Baseado em `outliers` de creator-skills (c) 2026 Cristiano Capasso, licença MIT
(ver LICENSE-original). Mudanças desta versão:
- Busca em português/Brasil por padrão (--lang pt --region BR), configurável.
- Aceita vídeos com áudio em português (ou sem idioma declarado); --strict_lang
  exige idioma declarado.
- Formato selecionável: shorts (padrão, até 3 min), longos (>3 min) ou todos.
- Linha de base por formato: a mediana do canal é calculada só com vídeos do
  mesmo formato (Shorts comparados com Shorts), porque Shorts e vídeos longos
  têm distribuições de views muito diferentes.
- Transcrições pedidas em pt / pt-BR, com inglês como reserva.
- Paginação opcional da busca (--pages) para ampliar a amostra.

Fórmula: outlier_score = views do vídeo / mediana de views do canal (mesmo formato).

Cota gratuita: 10.000 unidades/dia. Cada página de busca custa 100 unidades;
as demais chamadas custam 1 unidade cada.

Uso:
    python outlier_detector.py --terms "reforma tributária"
    python outlier_detector.py --terms "alesp" "tarcísio" --max_days 7
    python outlier_detector.py --terms "inss" --format todos --pages 2
"""

import os
import sys
import json
import time
import datetime
import argparse
import html
import re
import statistics
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))

SHORTS_MAX_SECONDS = 180  # YouTube aceita Shorts de até 3 min desde out/2024
MIN_BASELINE_SAMPLE = 5   # mínimo de vídeos do mesmo formato para usar a mediana por formato

NON_LATIN_SCRIPTS = (
    "CJK", "HIRAGANA", "KATAKANA", "HANGUL", "ARABIC", "DEVANAGARI",
    "BENGALI", "TAMIL", "TELUGU", "THAI", "HEBREW", "CYRILLIC", "GREEK",
    "ARMENIAN", "GEORGIAN", "ETHIOPIC", "KHMER", "LAO", "MYANMAR",
)


def load_api_key():
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(HERE, ".env"))
        load_dotenv(os.path.expanduser("~/.config/outliers-br/.env"))
        load_dotenv(os.path.expanduser("~/.config/outliers/.env"))
    except ImportError:
        pass
    return os.getenv("YOUTUBE_API_KEY")


def has_non_latin_script(text):
    for char in text:
        if not char.isalpha():
            continue
        name = unicodedata.name(char, "")
        if any(script in name for script in NON_LATIN_SCRIPTS):
            return True
    return False


def parse_iso_duration(duration_str):
    """ISO 8601 (P#DT#H#M#S) -> segundos."""
    match = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str or "")
    if not match:
        return 0
    d, h, m, s = (int(g or 0) for g in match.groups())
    return d * 86400 + h * 3600 + m * 60 + s


def matches_format(duration_seconds, fmt):
    if duration_seconds <= 0:
        return False
    if fmt == "shorts":
        return duration_seconds <= SHORTS_MAX_SECONDS
    if fmt == "longos":
        return duration_seconds > SHORTS_MAX_SECONDS
    return True


def lang_ok(audio_lang, lang, strict):
    audio_lang = (audio_lang or "").lower()
    if not audio_lang:
        return not strict
    return audio_lang.startswith(lang.lower())


def get_channel_baseline(youtube, channel_id, fmt, max_videos=50, cache=None):
    """
    Mediana de views dos uploads recentes do canal, filtrando pelo mesmo formato.
    Retorna (mediana, n_amostra, base) — base = 'formato' ou 'todos' (fallback).
    """
    key = (channel_id, fmt)
    if cache is not None and key in cache:
        return cache[key]

    result = (1.0, 0, "indisponível")
    try:
        uploads_playlist_id = "UU" + channel_id[2:]
        pl_response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part="contentDetails",
            maxResults=min(max_videos, 50),
        ).execute()
        video_ids = [it["contentDetails"]["videoId"] for it in pl_response.get("items", [])]

        if video_ids:
            stats_response = youtube.videos().list(
                id=",".join(video_ids),
                part="statistics,contentDetails",
            ).execute()

            all_views, fmt_views = [], []
            for item in stats_response.get("items", []):
                vc = int(item.get("statistics", {}).get("viewCount", 0))
                if vc <= 0:
                    continue
                all_views.append(vc)
                dur = parse_iso_duration(item.get("contentDetails", {}).get("duration"))
                if matches_format(dur, fmt):
                    fmt_views.append(vc)

            if len(fmt_views) >= MIN_BASELINE_SAMPLE:
                result = (statistics.median(fmt_views), len(fmt_views), "formato")
            elif all_views:
                result = (statistics.median(all_views), len(all_views), "todos")
    except Exception as e:
        print(f"    Aviso: sem mediana para o canal {channel_id}: {str(e)[:80]}")

    if cache is not None:
        cache[key] = result
    return result


def search_topic(youtube, query, args, published_after, channel_cache):
    """Busca um tema, aplica filtros e calcula o outlier score."""
    try:
        items = []
        page_token = None
        for _ in range(max(1, args.pages)):
            params = {
                "q": query,
                "type": "video",
                "part": "snippet",
                "maxResults": min(args.results, 50),
                "order": "viewCount",
                "relevanceLanguage": args.lang,
                "regionCode": args.region,
            }
            if args.format == "shorts":
                params["videoDuration"] = "short"  # < 4 min; refinado depois por duração
            if published_after:
                params["publishedAfter"] = published_after
            if page_token:
                params["pageToken"] = page_token
            resp = youtube.search().list(**params).execute()
            items.extend(resp.get("items", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        if not items:
            return []

        snippet_map = {}
        for item in items:
            vid = item.get("id", {}).get("videoId")
            if vid and vid not in snippet_map:
                snippet_map[vid] = item["snippet"]
        video_ids = list(snippet_map)

        video_stats = {}
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i + 50]
            stats_response = youtube.videos().list(
                id=",".join(chunk),
                part="statistics,contentDetails,snippet",
            ).execute()
            for it in stats_response.get("items", []):
                video_stats[it["id"]] = it

        skipped = {"não latino": 0, "outro idioma": 0, "games": 0,
                   "termo excluído": 0, "formato": 0, "poucas views": 0}
        candidates = []
        for vid in video_ids:
            snippet = snippet_map[vid]
            stats_item = video_stats.get(vid)
            if not stats_item:
                continue
            title = html.unescape(snippet.get("title", ""))
            vsnip = stats_item.get("snippet", {})

            if has_non_latin_script(title):
                skipped["não latino"] += 1
                continue
            audio_lang = vsnip.get("defaultAudioLanguage") or vsnip.get("defaultLanguage") or ""
            if not lang_ok(audio_lang, args.lang, args.strict_lang):
                skipped["outro idioma"] += 1
                continue
            if vsnip.get("categoryId") == "20":
                skipped["games"] += 1
                continue
            if args.exclude_terms and any(t.lower() in title.lower() for t in args.exclude_terms):
                skipped["termo excluído"] += 1
                continue
            duration = parse_iso_duration(stats_item.get("contentDetails", {}).get("duration"))
            if not matches_format(duration, args.format):
                skipped["formato"] += 1
                continue
            stats = stats_item.get("statistics", {})
            view_count = int(stats.get("viewCount", 0))
            if view_count < args.min_views:
                skipped["poucas views"] += 1
                continue
            candidates.append((vid, snippet, stats, duration, title, audio_lang))

        channels = {c[1].get("channelId") for c in candidates if c[1].get("channelId")}
        print(f"    Calculando medianas de {len(channels)} canais (formato: {args.format})...")
        for ch in channels:
            get_channel_baseline(youtube, ch, args.format, args.channel_videos, channel_cache)

        videos = []
        for vid, snippet, stats, duration, title, audio_lang in candidates:
            channel_id = snippet.get("channelId", "")
            median, n, base = channel_cache.get((channel_id, args.format), (1.0, 0, "indisponível"))
            view_count = int(stats.get("viewCount", 0))
            score = round(view_count / median, 2) if median > 0 else 0

            published_at = snippet.get("publishedAt", "")
            date_str, days_old = "", None
            if published_at:
                try:
                    pub = datetime.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    date_str = pub.strftime("%Y-%m-%d")
                    days_old = (datetime.datetime.now(datetime.timezone.utc) - pub).days
                except ValueError:
                    pass

            is_short = duration <= SHORTS_MAX_SECONDS
            thumbs = snippet.get("thumbnails", {})
            videos.append({
                "video_id": vid,
                "title": title,
                "url": (f"https://www.youtube.com/shorts/{vid}" if is_short
                        else f"https://www.youtube.com/watch?v={vid}"),
                "view_count": view_count,
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "duration": duration,
                "audio_language": audio_lang or "não declarado",
                "channel_name": snippet.get("channelTitle", ""),
                "channel_id": channel_id,
                "channel_median_views": int(median),
                "baseline_sample": n,
                "baseline_type": base,
                "thumbnail_url": (thumbs.get("high", {}).get("url")
                                  or thumbs.get("medium", {}).get("url")
                                  or f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"),
                "date": date_str,
                "days_old": days_old,
                "outlier_score": score,
                "source": f"youtube: {query}",
            })

        dropped = {k: v for k, v in skipped.items() if v}
        if dropped:
            print("    Filtrados: " + ", ".join(f"{v} {k}" for k, v in dropped.items()))
        return videos

    except Exception as e:
        print(f"  Erro na API do YouTube: {str(e)[:150]}")
        return []


def fetch_transcript(video_id, lang):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        time.sleep(1)
        api = YouTubeTranscriptApi()
        langs = [lang, f"{lang}-BR", f"{lang}-PT", "en"] if lang == "pt" else [lang, "en"]
        fetched = api.fetch(video_id, languages=langs)
        return " ".join(s.text for s in fetched)
    except Exception as e:
        print(f"    [transcrição] falhou: {str(e)[:100]}")
        return None


def process_outlier(o, index, total, args):
    print(f"\n  [{index}/{total}] {o['title'][:60]}")
    o["transcript_excerpt"] = ""
    if not args.skip_transcripts:
        t = fetch_transcript(o["video_id"], args.lang)
        if t:
            print(f"    Transcrição: {len(t)} caracteres")
            o["transcript_excerpt"] = t[:8000]
    return o


def save_results_json(outliers, output_path, args):
    data = {
        "generated_at": datetime.datetime.now().isoformat(),
        "params": {"terms": args.terms, "format": args.format, "lang": args.lang,
                   "region": args.region, "max_days": args.max_days,
                   "min_views": args.min_views, "min_score": args.min_score},
        "total_outliers": len(outliers),
        "outliers": [{
            "outlier_score": o["outlier_score"],
            "title": o["title"],
            "url": o["url"],
            "thumbnail_url": o["thumbnail_url"],
            "view_count": o["view_count"],
            "like_count": o["like_count"],
            "comment_count": o["comment_count"],
            "duration_seconds": o["duration"],
            "days_old": o["days_old"],
            "date": o["date"],
            "audio_language": o["audio_language"],
            "channel_name": o["channel_name"],
            "channel_median_views": o["channel_median_views"],
            "baseline_sample": o["baseline_sample"],
            "baseline_type": o["baseline_type"],
            "transcript_excerpt": o.get("transcript_excerpt", ""),
            "source": o["source"],
        } for o in outliers],
    }
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return output_path


def print_summary(outliers):
    print("\n" + "=" * 70 + "\n  TOP OUTLIERS\n" + "=" * 70)
    for i, o in enumerate(outliers, 1):
        base = "" if o["baseline_type"] == "formato" else f" [base: {o['baseline_type']}]"
        print(f"\n  #{i}  [{o['outlier_score']}x] {o['title']}")
        print(f"       {o['channel_name']} | {o['view_count']:,} views | "
              f"{o['duration']}s | {o['days_old']}d{base}".replace(",", "."))
        print(f"       {o['url']}")
    print("\n" + "=" * 70)


def build_parser():
    p = argparse.ArgumentParser(description="Outliers do YouTube (Brasil/Shorts): "
                                            "views ÷ mediana do canal no mesmo formato.")
    p.add_argument("--terms", nargs="+", required=True, help="Um ou mais temas (obrigatório).")
    p.add_argument("--format", choices=["shorts", "longos", "todos"], default="shorts",
                   help="shorts (≤3 min, padrão), longos (>3 min) ou todos.")
    p.add_argument("--lang", default="pt", help="Idioma (padrão: pt).")
    p.add_argument("--region", default="BR", help="Região (padrão: BR).")
    p.add_argument("--strict_lang", action="store_true",
                   help="Descarta vídeos sem idioma de áudio declarado.")
    p.add_argument("--results", type=int, default=50, help="Resultados por página (máx. 50).")
    p.add_argument("--pages", type=int, default=1, help="Páginas de busca por tema (100 unidades cada).")
    p.add_argument("--min_views", type=int, default=10000, help="Views mínimas (padrão: 10.000).")
    p.add_argument("--max_days", type=int, default=30, help="Idade máxima em dias (padrão: 30).")
    p.add_argument("--min_score", type=float, default=2.0, help="Score mínimo (padrão: 2.0).")
    p.add_argument("--limit", type=int, default=10, help="Máximo de outliers (padrão: 10).")
    p.add_argument("--channel_videos", type=int, default=50,
                   help="Uploads recentes amostrados por canal (máx. 50).")
    p.add_argument("--exclude_terms", nargs="+", default=None, help="Descarta títulos com estes termos.")
    p.add_argument("--skip_transcripts", action="store_true", help="Não baixa transcrições.")
    p.add_argument("--output", default=None, help="Caminho do JSON de saída.")
    p.add_argument("--workers", type=int, default=3, help="Transcrições em paralelo.")
    return p


def run(args, youtube):
    published_after = (datetime.datetime.now(datetime.timezone.utc)
                       - datetime.timedelta(days=args.max_days)).strftime("%Y-%m-%dT00:00:00Z")
    # por página: busca (100) + estatísticas (1) + até 50 canais × 2 chamadas (100)
    quota = len(args.terms) * args.pages * 201
    print("Outliers BR (YouTube Data API v3)")
    print(f"  Temas: {args.terms} | formato: {args.format} | {args.lang}/{args.region}")
    print(f"  Views mín.: {args.min_views} | idade máx.: {args.max_days}d | score mín.: {args.min_score}x")
    print(f"  Cota estimada: até ~{quota}/10.000 unidades\n")

    cache, all_videos = {}, []
    for term in args.terms:
        print(f"  Buscando: {term}")
        vids = search_topic(youtube, term, args, published_after, cache)
        print(f"    {len(vids)} vídeos após filtros")
        all_videos.extend(vids)

    seen, unique = set(), []
    for v in all_videos:
        if v["video_id"] not in seen:
            seen.add(v["video_id"])
            unique.append(v)

    outliers = [v for v in unique if v["outlier_score"] >= args.min_score]
    outliers.sort(key=lambda x: (x["outlier_score"], x["date"]), reverse=True)
    outliers = outliers[:args.limit]

    if not outliers:
        print(f"\nNenhum vídeo com score >= {args.min_score}x. "
              f"Tente --min_score 1.5, --max_days maior, --pages 2 ou outro tema.")
        return 0, None

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(process_outlier, o, i, len(outliers), args)
                   for i, o in enumerate(outliers, 1)]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"    Erro: {e}")

    out = args.output or os.path.join(
        HERE, "output", f"outliers_{datetime.datetime.now():%Y%m%d_%H%M%S}.json")
    path = save_results_json(outliers, out, args)
    print(f"\nResultados salvos em: {path}")
    print_summary(outliers)
    return 0, path


def main():
    args = build_parser().parse_args()
    key = load_api_key()
    if not key:
        print("ERRO: YOUTUBE_API_KEY não definida.")
        print("  Coloque em ~/.config/outliers-br/.env (recomendado) ou no .env desta pasta.")
        print("  Chave gratuita: console.cloud.google.com → ativar 'YouTube Data API v3' → Credenciais → Chave de API.")
        return 1
    from googleapiclient.discovery import build
    youtube = build("youtube", "v3", developerKey=key)
    code, _ = run(args, youtube)
    return code


if __name__ == "__main__":
    sys.exit(main())
