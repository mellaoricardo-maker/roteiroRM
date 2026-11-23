#!/usr/bin/env python3
"""
ig-competitor-research-br — pesquisa semanal: aprofunda os melhores Reels da
varredura (quadros do gancho, transcrição, ritmo de cortes) e gera um relatório
HTML autocontido, ranqueado por múltiplo da mediana.

  python3 pesquisa_semanal.py enriquecer RUN [--n 12] [--cookies X] [--limiar 0.06] [--modelo medium]
  python3 pesquisa_semanal.py relatorio  RUN [--top 30] [--saida arquivo.html]

RUN/candidatos.json vem de scan_concorrentes.py (skill content-ideas-br).
RUN/analise.json (opcional, escrito pelo Claude) traz resumo, padrões e, por Reel,
tema / por que funcionou / gancho falado.
Aprofundamento: skill video-breakdown-br (pasta irmã).

Baseado em `ig-competitor-research` de creator-skills (c) 2026 Cristiano Capasso,
MIT (ver LICENSE-original). Reescrito: sem navegador automatizado, sem padrões
fixos no código, relatório em português com tema claro/escuro e imagens embutidas.
"""
import argparse
import base64
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
BREAKDOWN = HERE.parent / "video-breakdown-br" / "breakdown.sh"
HOOK_FRAMES = {0: "gancho_01.jpg", 1: "gancho_05.jpg", 2: "gancho_09.jpg"}  # 4 fps: 0 s, 1 s, 2 s


def code_of(url):
    m = re.search(r"/(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)", url or "")
    return m.group(1) if m else re.sub(r"\W", "_", url or "reel")[-20:]


def load_candidates(run):
    p = Path(run) / "candidatos.json"
    if not p.exists():
        sys.exit(f"Não achei {p}. Rode antes a varredura (scan_concorrentes.py --out {p}).")
    return json.loads(p.read_text(encoding="utf-8"))


def enriched_ok(d):
    return (d / "gancho" / HOOK_FRAMES[0]).exists() and (d / "info.txt").exists()


def breakdown_one(url, dest, a, runner=subprocess.run):
    cmd = ["bash", str(BREAKDOWN), url, "-o", str(dest), "-s", str(a.limiar), "-m", a.modelo]
    if a.cookies:
        cmd += ["-c", a.cookies]
    r = runner(cmd, capture_output=True, text=True, timeout=1800)
    return r.returncode == 0


def cmd_enriquecer(a, runner=subprocess.run):
    if not BREAKDOWN.exists():
        sys.exit("ERRO: skill video-breakdown-br não encontrada ao lado desta.")
    run = Path(a.run).expanduser()
    data = load_candidates(run)
    cands = data.get("candidates", [])[: a.n]
    out = run / "enrich"
    out.mkdir(parents=True, exist_ok=True)
    status = {}
    # uma passada sequencial (baixar em paralelo provoca bloqueio), depois nova tentativa dos que falharam
    for tentativa in (1, 2):
        for c in cands:
            code = code_of(c["permalink"])
            d = out / code
            if enriched_ok(d):
                status[code] = "ok"
                continue
            print(f"[{tentativa}] {code} @{c['handle']}", file=sys.stderr, flush=True)
            breakdown_one(c["permalink"], d, a, runner)
            status[code] = "ok" if enriched_ok(d) else "falhou"
            # o vídeo completo não é necessário para o relatório: libera espaço
            if not a.manter_video:
                for f in ("video.mp4", "audio.mp3"):
                    (d / f).unlink(missing_ok=True)
    (run / "enrich" / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2))
    ok = sum(1 for v in status.values() if v == "ok")
    print(json.dumps({"aprofundados": ok, "falharam": [k for k, v in status.items() if v != "ok"]},
                     ensure_ascii=False))


# ---------------------------------------------------------------- relatório --

def read_info(d):
    info = {}
    p = d / "info.txt"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                info[k.strip()] = v.strip()
    return info


def first_spoken_line(d):
    srt = d / "transcript.srt"
    if not srt.exists():
        return ""
    for line in srt.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.isdigit() and "-->" not in s:
            return s
    return ""


def img_data(path, width=300):
    """Miniatura embutida (data URI). Reduz com ffmpeg se disponível."""
    if not path.exists():
        return None
    raw = None
    if shutil.which("ffmpeg"):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp) / "t.jpg"
            r = subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(path),
                                "-vf", f"scale={width}:-2", "-q:v", "5", str(t)], capture_output=True)
            if r.returncode == 0 and t.exists():
                raw = t.read_bytes()
    raw = raw or path.read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode()


def fmt(n):
    if n is None:
        return "–"
    n = float(n)
    if n >= 1e6:
        return f"{n/1e6:.1f} mi".replace(".", ",")
    if n >= 1e4:
        return f"{n/1e3:.0f} mil"
    if n >= 1e3:
        return f"{n/1e3:.1f} mil".replace(".", ",")
    return f"{int(n)}"


def esc(t):
    return html.escape(str(t or ""))


CSS = """
:root{--bg:#f7f6f2;--card:#ffffff;--ink:#1d1c19;--muted:#6b675e;--line:#e4e1d8;--accent:#0b7a43;--accent2:#b58600;--chip:#eef4ef;--warn:#b3261e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121310;--card:#1b1c18;--ink:#f1efe8;--muted:#a19d92;--line:#2c2d27;--accent:#3ccf7d;--accent2:#f0c33c;--chip:#1f2a22;--warn:#ff8a80}}
:root[data-theme="dark"]{--bg:#121310;--card:#1b1c18;--ink:#f1efe8;--muted:#a19d92;--line:#2c2d27;--accent:#3ccf7d;--accent2:#f0c33c;--chip:#1f2a22;--warn:#ff8a80}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:32px 16px 64px}
header h1{font-size:clamp(26px,5vw,40px);line-height:1.15;margin:6px 0 10px}
.kicker{color:var(--accent);font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:12px}
.sub{color:var(--muted);max-width:720px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:28px 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.stat b{display:block;font-size:26px;color:var(--accent)}
.stat span{color:var(--muted);font-size:13px}
h2{font-size:22px;margin:40px 0 6px}
.desc{color:var(--muted);margin-bottom:18px;font-size:15px}
.patterns{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.pat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.pat h3{font-size:16px;margin-bottom:4px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:16px}
.top{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:baseline}
.rank{font-weight:800;color:var(--accent2);font-size:20px}
.top a{color:var(--ink);font-weight:700;text-decoration:none}
.top a:hover{text-decoration:underline}
.mult{background:var(--chip);color:var(--accent);font-weight:800;border-radius:999px;padding:2px 10px;font-size:14px}
.tag{color:var(--muted);font-size:13px}
.flag{color:var(--warn);font-size:13px;font-weight:600}
.nums{display:flex;flex-wrap:wrap;gap:6px 18px;color:var(--muted);font-size:14px;margin:8px 0}
.nums b{color:var(--ink)}
.frames{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;max-width:420px;margin:10px 0}
.frames figure{margin:0}.frames img{width:100%;border-radius:8px;display:block;border:1px solid var(--line)}
.frames figcaption{font-size:12px;color:var(--muted);text-align:center}
.hook{border-left:3px solid var(--accent);padding:4px 12px;margin:10px 0;font-size:17px}
.hook small{display:block;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}
.why{margin:8px 0}
details{margin-top:8px}summary{cursor:pointer;color:var(--accent);font-weight:600}
details div{white-space:pre-wrap;color:var(--muted);font-size:14px;margin-top:6px}
.cap{color:var(--muted);font-size:14px;margin-top:8px;overflow-wrap:anywhere}
footer{color:var(--muted);font-size:13px;margin-top:40px;border-top:1px solid var(--line);padding-top:16px}
@media (max-width:520px){.frames{max-width:100%}}
"""


def card_html(i, c, d, ann):
    frames = ""
    if d and (d / "gancho").exists():
        cells = []
        for s, name in HOOK_FRAMES.items():
            src = img_data(d / "gancho" / name)
            if src:
                cells.append(f'<figure><img src="{src}" alt="Quadro em {s} s" loading="lazy"><figcaption>{s} s</figcaption></figure>')
        if cells:
            frames = f'<div class="frames">{"".join(cells)}</div>'
    info = read_info(d) if d else {}
    spoken = ann.get("gancho_falado") or (first_spoken_line(d) if d else "")
    hook = (f'<div class="hook"><small>Gancho falado</small>“{esc(spoken)}”</div>' if spoken else
            f'<div class="hook"><small>Gancho (pela legenda — sem transcrição)</small>{esc((c.get("caption") or "").splitlines()[0][:160] if c.get("caption") else "–")}</div>')
    ritmo = ""
    if info:
        br = lambda v: esc(v).replace(".", ",")
        wps = re.search(r"\(([\d.]+) por segundo\)", info.get("Palavras faladas", ""))
        ritmo = (f'<span>cortes/min <b>{br(info.get("Cortes por minuto","–"))}</b></span>'
                 f'<span>plano médio <b>{br(info.get("Plano médio","–"))}</b></span>'
                 f'<span>duração <b>{br(info.get("Duração","–"))}</b></span>'
                 + (f'<span>fala <b>{br(wps.group(1))} palavras/s</b></span>' if wps else ""))
    tr = ""
    if d and (d / "transcript.txt").exists():
        t = (d / "transcript.txt").read_text(encoding="utf-8").strip()
        if t and t != "(sem trilha de áudio)":
            tr = f"<details><summary>Transcrição completa</summary><div>{esc(t)}</div></details>"
    why = f'<p class="why"><b>Por que funcionou:</b> {esc(ann["por_que"])}</p>' if ann.get("por_que") else ""
    tema = f'<span class="tag">{esc(ann["tema"])}</span>' if ann.get("tema") else ""
    base_flag = (f'<span class="flag">mediana com só {c["baseline_sample"]} Reels</span>'
                 if (c.get("baseline_sample") or 99) < 8 else "")
    cap = c.get("caption") or ""
    cap_html = f'<p class="cap"><b>Legenda:</b> {esc(cap[:400])}{"…" if len(cap) > 400 else ""}</p>' if cap else ""
    return f"""<article class="card">
<div class="top"><span class="rank">#{i}</span><a href="{esc(c['permalink'])}" target="_blank" rel="noopener">@{esc(c['handle'])}</a>
<span class="mult">{str(c['outlier']).replace('.', ',')}×</span>{tema}{base_flag}</div>
<div class="nums"><span>views <b>{fmt(c.get('views'))}</b></span><span>mediana da conta <b>{fmt(c.get('account_median_views'))}</b></span>
<span>curtidas <b>{fmt(c.get('likes'))}</b></span><span>comentários <b>{fmt(c.get('comments'))}</b></span><span>há <b>{c.get('days_ago','–')}</b> dias</span>{ritmo}</div>
{frames}{hook}{why}{tr}{cap_html}
</article>"""


def cmd_relatorio(a):
    run = Path(a.run).expanduser()
    data = load_candidates(run)
    cands = data.get("candidates", [])[: a.top]
    ann_p = run / "analise.json"
    ann = json.loads(ann_p.read_text(encoding="utf-8")) if ann_p.exists() else {}
    per = ann.get("reels", {})

    cards, n_enr, n_tr = [], 0, 0
    for i, c in enumerate(cands, 1):
        d = run / "enrich" / code_of(c["permalink"])
        d = d if d.exists() else None
        if d and enriched_ok(d):
            n_enr += 1
        if d and (d / "transcript.txt").exists():
            n_tr += 1
        cards.append(card_html(i, c, d, per.get(c["permalink"], {})))

    pats = "".join(f'<div class="pat"><h3>{esc(p.get("titulo"))}</h3><p>{esc(p.get("texto"))}</p></div>'
                   for p in ann.get("padroes", []))
    pats_html = (f'<h2>Padrões da semana</h2><p class="desc">Escritos a partir dos Reels abaixo; '
                 f'inferências, não regras.</p><div class="patterns">{pats}</div>') if pats else ""
    resumo = esc(ann.get("resumo") or "Reels que mais superaram a mediana de views da própria conta.")
    ok_acc = len(data.get("accounts_ok", []))
    failed = data.get("accounts_failed", [])
    stopped = data.get("stopped_early")
    params = data.get("params", {})
    gerado = data.get("generated_at", datetime.now().isoformat(timespec="minutes"))

    notes = []
    if stopped:
        notes.append(f"Varredura interrompida: {esc(stopped)}")
    if failed:
        notes.append("Contas não lidas: " + ", ".join("@" + esc(f["handle"]) for f in failed))
    if data.get("dropped_paid"):
        notes.append(f"{len(data['dropped_paid'])} Reels descartados como patrocinados/impulsionados")
    notes.append("Views da API incluem alcance pago e podem somar views do Facebook em posts cruzados; "
                 "cortes por minuto é estimativa automática.")

    doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pesquisa de Reels</title><style>{CSS}</style></head><body><div class="wrap">
<header><div class="kicker">Pesquisa semanal · Instagram</div>
<h1>O que superou a média nas contas acompanhadas</h1><p class="sub">{resumo}</p></header>
<section class="stats">
<div class="stat"><b>{ok_acc}</b><span>contas lidas</span></div>
<div class="stat"><b>{len(cands)}</b><span>Reels no ranking</span></div>
<div class="stat"><b>{n_enr}</b><span>com quadros do gancho</span></div>
<div class="stat"><b>{n_tr}</b><span>com transcrição</span></div>
<div class="stat"><b>{params.get('days','–')} d</b><span>janela · mín. {str(params.get('min_outlier','–')).replace('.', ',')}×</span></div>
</section>
{pats_html}
<h2>Ranking</h2><p class="desc">Ordenado pelo múltiplo: views do Reel ÷ mediana de views dos Reels recentes da mesma conta.</p>
{''.join(cards) or '<p class="desc">Nenhum Reel passou nos filtros.</p>'}
<footer>Gerado em {esc(gerado)} · {' · '.join(notes)}</footer>
</div></body></html>"""
    out = Path(a.saida) if a.saida else run / f"pesquisa-reels-{datetime.now():%Y-%m-%d}.html"
    out.write_text(doc, encoding="utf-8")
    print(out)
    return out


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enriquecer")
    e.add_argument("run")
    e.add_argument("--n", type=int, default=12, help="quantos aprofundar (padrão 12)")
    e.add_argument("--cookies", default=None, help='navegador com conta SECUNDÁRIA logada, ex.: "chrome:Profile 2"')
    e.add_argument("--limiar", type=float, default=0.06, help="limiar de corte (0.06 = pessoa falando)")
    e.add_argument("--modelo", default="medium", help="modelo do Whisper")
    e.add_argument("--manter-video", action="store_true", help="não apagar video.mp4/audio.mp3")
    r = sub.add_parser("relatorio")
    r.add_argument("run")
    r.add_argument("--top", type=int, default=30)
    r.add_argument("--saida", default=None)
    return ap


def main():
    a = build_parser().parse_args()
    {"enriquecer": cmd_enriquecer, "relatorio": cmd_relatorio}[a.cmd](a)


if __name__ == "__main__":
    main()
