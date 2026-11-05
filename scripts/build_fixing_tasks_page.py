#!/usr/bin/env python3
"""Build a self-contained GitHub Pages viewer for the 172 fixing tasks."""
import json
import subprocess
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
REPO = "HuggingFriends/PhysFixBench"
REVISION = "main"


def hf_token() -> str:
    result = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=huggingface.co\n\n",
        text=True,
        capture_output=True,
        check=True,
    )
    return dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)["password"]


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    token = hf_token()
    annotations_path = Path(
        hf_hub_download(
            repo_id=REPO,
            repo_type="dataset",
            filename="data/reviewed_batch1/annotations.jsonl",
            revision=REVISION,
            token=token,
        )
    )
    prompts_path = Path(
        hf_hub_download(
            repo_id=REPO,
            repo_type="dataset",
            filename="data/reviewed_batch1/fixing_prompts_3way_en.jsonl",
            revision=REVISION,
            token=token,
        )
    )
    summary_path = Path(
        hf_hub_download(
            repo_id=REPO,
            repo_type="dataset",
            filename="data/reviewed_batch1/summary.json",
            revision=REVISION,
            token=token,
        )
    )
    annotations = {row["record_id"]: row for row in read_jsonl(annotations_path)}
    prompt_rows = read_jsonl(prompts_path)
    rows = []
    for prompt in prompt_rows:
        ann = annotations[prompt["record_id"]]
        rows.append(
            {
                "record_id": ann["record_id"],
                "dir_name": ann["dir_name"],
                "source": ann["source"],
                "generator": ann["generator"],
                "error_family": ann.get("error_family", ""),
                "scenario_domain": ann.get("scenario_domain", ""),
                "interaction_primitive": ann.get("interaction_primitive", ""),
                "duration_seconds": ann.get("duration_seconds"),
                "width": ann.get("width"),
                "height": ann.get("height"),
                "issue_count": len(ann["issues"]),
                "issues": ann["issues"],
                "fix_keep": ann["fix_keep"],
                "video_url": ann["video_url"],
                "prompts": {
                    "self_fixing": prompt["self_fixing_prompt_en"],
                    "problem_only": prompt["problem_only_prompt_en"],
                    "problem_expected": prompt["problem_expected_prompt_en"],
                },
            }
        )
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert len(rows) == summary["count"]
    assert all("【应修改为】" not in row["prompts"]["problem_only"] for row in rows)
    assert all("Expected behavior:" in row["prompts"]["problem_expected"] for row in rows)
    assert all("Expected behavior:" not in row["prompts"]["problem_only"] for row in rows)
    html = build_html(rows, summary)
    (ROOT / "fixing_tasks.html").write_text(html, encoding="utf-8")
    print("wrote", ROOT / "fixing_tasks.html", len(rows))


def build_html(rows, summary):
    payload = json.dumps({"summary": summary, "records": rows}, ensure_ascii=False).replace("<", "\\u003c")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PhyFixBench · Fixing Tasks</title>
<style>
:root {{
  --bg:#f5f7fa; --panel:#ffffff; --ink:#1b2637; --muted:#66758a; --line:#d9e1ea;
  --green:#176954; --blue:#2457a6; --red:#9f3d35; --amber:#8c5b17; --soft:#eef4f7;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--bg); color:var(--ink);
  font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",Arial,sans-serif;
}}
header {{
  position:sticky; top:0; z-index:20; background:rgba(245,247,250,.96);
  border-bottom:1px solid var(--line); backdrop-filter:saturate(160%) blur(8px);
}}
.wrap {{ max-width:1500px; margin:0 auto; padding:18px 20px; }}
.eyebrow {{ font-size:12px; letter-spacing:.12em; color:var(--green); font-weight:800; }}
h1 {{ margin:4px 0 10px; font-size:24px; line-height:1.2; }}
.stats {{ display:flex; gap:10px; flex-wrap:wrap; margin:10px 0 14px; }}
.stat {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:8px 12px; min-width:126px; }}
.stat b {{ display:block; font-size:20px; }}
.stat span {{ color:var(--muted); font-size:12px; }}
.toolbar {{ display:grid; grid-template-columns:160px 190px 1fr auto auto; gap:9px; align-items:center; }}
select,input,button,textarea {{ font:inherit; }}
select,input[type=search] {{ height:36px; border:1px solid #c8d2df; border-radius:7px; background:white; color:var(--ink); padding:0 10px; }}
button {{ border:1px solid #c8d2df; border-radius:7px; background:white; color:var(--ink); padding:7px 10px; cursor:pointer; }}
button:hover {{ border-color:var(--green); }}
.seg {{ display:flex; gap:4px; background:#e7edf3; border-radius:8px; padding:3px; }}
.seg button {{ border:0; border-radius:6px; background:transparent; padding:5px 9px; white-space:nowrap; }}
.seg button.active {{ background:white; color:var(--green); box-shadow:0 1px 4px rgba(0,0,0,.08); }}
.count {{ margin-top:9px; color:var(--muted); font-size:13px; }}
main {{ max-width:1500px; margin:0 auto; padding:18px 20px 40px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; margin:0 0 16px; }}
.head {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:12px; }}
.rid {{ font-weight:800; font-size:13px; }}
.badge {{ display:inline-flex; align-items:center; min-height:23px; border-radius:999px; padding:2px 9px; background:var(--soft); color:#334155; font-size:12px; }}
.src-physion_eval {{ background:#e8f5ef; color:#106044; }}
.src-robojudge {{ background:#e8eefb; color:#244b93; }}
.src-phyground {{ background:#fff2df; color:#8a4c11; }}
.src-videophy2 {{ background:#f0eafd; color:#5d3aa8; }}
.grid {{ display:grid; grid-template-columns:minmax(320px,520px) minmax(0,1fr); gap:14px; align-items:start; }}
video {{ width:100%; aspect-ratio:16/9; max-height:390px; border-radius:8px; background:#111; display:block; }}
.media-tools {{ display:flex; gap:6px; flex-wrap:wrap; align-items:center; margin-top:9px; }}
.timebtn {{ font-size:12px; padding:4px 7px; }}
.meta {{ margin-top:8px; color:var(--muted); font-size:12.5px; display:grid; gap:3px; }}
.prompts {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
.promptbox {{ border:1px solid var(--line); border-radius:8px; overflow:hidden; background:#fbfdff; min-height:240px; display:flex; flex-direction:column; }}
.prompthead {{ display:flex; justify-content:space-between; align-items:center; gap:8px; padding:8px 10px; border-bottom:1px solid var(--line); background:#f8fafc; }}
.prompthead strong {{ font-size:13px; }}
.prompthead button {{ font-size:12px; padding:3px 7px; }}
textarea {{ width:100%; min-height:210px; flex:1; border:0; resize:vertical; padding:10px; background:transparent; color:#243244; line-height:1.58; }}
textarea:focus {{ outline:2px solid #9ec1f7; outline-offset:-2px; }}
.self textarea {{ border-left:4px solid var(--amber); }}
.problem textarea {{ border-left:4px solid var(--red); }}
.full textarea {{ border-left:4px solid var(--green); }}
details {{ margin-top:11px; color:#344154; }}
summary {{ cursor:pointer; font-weight:700; }}
.issues {{ display:grid; gap:8px; margin-top:8px; }}
.issue {{ border-left:3px solid var(--line); padding:5px 9px; background:#f8fafc; border-radius:0 6px 6px 0; }}
.issue b {{ color:var(--red); }}
.issue .expected {{ color:var(--green); margin-top:3px; }}
.pager {{ display:flex; gap:12px; justify-content:center; align-items:center; margin:20px 0; }}
.toast {{ position:fixed; right:18px; bottom:18px; background:#152033; color:white; padding:9px 12px; border-radius:8px; opacity:0; transform:translateY(8px); transition:.18s; pointer-events:none; }}
.toast.show {{ opacity:1; transform:translateY(0); }}
@media(max-width:1050px) {{
  .toolbar {{ grid-template-columns:1fr 1fr; }}
  .grid {{ grid-template-columns:1fr; }}
  .prompts {{ grid-template-columns:1fr; }}
}}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="eyebrow">PHYFIXBENCH / FIXING TASK INPUTS</div>
    <h1>{summary["count"]} Final Evaluation Videos · Three Prompt Conditions</h1>
    <div id="stats" class="stats"></div>
    <div class="toolbar">
      <select id="source"><option value="">全部来源</option></select>
      <select id="generator"><option value="">全部生成模型</option></select>
      <input id="search" type="search" placeholder="搜索 record_id、问题、模型">
      <div class="seg" aria-label="显示模式">
        <button data-mode="all" class="active">三列</button>
        <button data-mode="self">Self</button>
        <button data-mode="problem">Problem</button>
        <button data-mode="full">Full</button>
      </div>
      <button id="export">导出当前筛选 JSON</button>
    </div>
    <div id="count" class="count"></div>
  </div>
</header>
<main>
  <div id="cards"></div>
  <div class="pager"><button id="prev">上一页</button><span id="page"></span><button id="next">下一页</button></div>
</main>
<div id="toast" class="toast">已复制</div>
<script id="payload" type="application/json">{payload}</script>
<script>
const DATA = JSON.parse(document.getElementById('payload').textContent);
const RECORDS = DATA.records;
const PAGE_SIZE = 12;
let page = 0;
let mode = 'all';
let filtered = [];
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const uniq = arr => [...new Set(arr)].sort((a,b)=>String(a).localeCompare(String(b)));
const sourceZh = {{physion_eval:'Physion-Eval', robojudge:'RoboJudge', phyground:'PhyGround', videophy2:'VideoPhy2'}};
function init() {{
  const srcCounts = {{}};
  for (const r of RECORDS) srcCounts[r.source] = (srcCounts[r.source] || 0) + 1;
  $('stats').innerHTML = `<div class="stat"><b>${{RECORDS.length}}</b><span>tasks</span></div>` +
    Object.entries(srcCounts).map(([k,v])=>`<div class="stat"><b>${{v}}</b><span>${{esc(sourceZh[k]||k)}}</span></div>`).join('') +
    `<div class="stat"><b>${{DATA.summary.issue_cards}}</b><span>issue cards</span></div>`;
  for (const s of uniq(RECORDS.map(r=>r.source))) $('source').insertAdjacentHTML('beforeend', `<option value="${{esc(s)}}">${{esc(sourceZh[s]||s)}}</option>`);
  for (const g of uniq(RECORDS.map(r=>r.generator))) $('generator').insertAdjacentHTML('beforeend', `<option value="${{esc(g)}}">${{esc(g)}}</option>`);
  $('source').addEventListener('change', resetFilter);
  $('generator').addEventListener('change', resetFilter);
  $('search').addEventListener('input', resetFilter);
  $('prev').onclick = () => {{ page--; render(); scrollTo(0,0); }};
  $('next').onclick = () => {{ page++; render(); scrollTo(0,0); }};
  document.querySelectorAll('.seg button').forEach(b => b.onclick = () => {{
    document.querySelectorAll('.seg button').forEach(x=>x.classList.remove('active'));
    b.classList.add('active'); mode = b.dataset.mode; render();
  }});
  $('export').onclick = exportFiltered;
  resetFilter();
}}
function resetFilter() {{ page = 0; filter(); }}
function filter() {{
  const src = $('source').value, gen = $('generator').value, q = $('search').value.trim().toLowerCase();
  filtered = RECORDS.filter(r => (!src || r.source === src) && (!gen || r.generator === gen) &&
    (!q || JSON.stringify([r.record_id,r.generator,r.error_family,r.scenario_domain,r.issues,r.prompts]).toLowerCase().includes(q)));
  render();
}}
function promptBox(cls, title, text) {{
  return `<div class="promptbox ${{cls}}"><div class="prompthead"><strong>${{title}}</strong><button data-copy="${{esc(text)}}">复制</button></div><textarea readonly>${{esc(text)}}</textarea></div>`;
}}
function card(r, idx) {{
  const prompts = [];
  if (mode === 'all' || mode === 'self') prompts.push(promptBox('self','1 · Self-fixing', r.prompts.self_fixing));
  if (mode === 'all' || mode === 'problem') prompts.push(promptBox('problem','2 · 只给问题', r.prompts.problem_only));
  if (mode === 'all' || mode === 'full') prompts.push(promptBox('full','3 · 问题 + 正确表现', r.prompts.problem_expected));
  const times = r.issues.map((it,i)=> {{
    const start = parseFloat(String(it.timestamp).split(/[–-]/)[0]);
    return Number.isFinite(start) ? `<button class="timebtn" data-seek="${{start}}">▶ ${{esc(it.timestamp)}}秒</button>` : '';
  }}).join('');
  const issues = r.issues.map((it,i)=>`<div class="issue"><b>${{i+1}}. 第${{esc(it.timestamp)}}秒：${{esc(it.problem)}}</b><div class="expected">应修改为：${{esc(it.expected)}}</div></div>`).join('');
  return `<article class="card">
    <div class="head">
      <span class="rid">#${{idx+1}} · ${{esc(r.record_id)}}</span>
      <span class="badge src-${{esc(r.source)}}">${{esc(sourceZh[r.source]||r.source)}}</span>
      <span class="badge">${{esc(r.generator)}}</span>
      <span class="badge">${{r.issue_count}} cards</span>
      <span class="badge">${{r.width}}×${{r.height}}</span>
    </div>
    <div class="grid">
      <section>
        <video controls preload="none" playsinline src="${{esc(r.video_url)}}"></video>
        <div class="media-tools">${{times}}<select data-speed><option value="1">1×</option><option value="0.5">0.5×</option><option value="0.25">0.25×</option></select></div>
        <div class="meta"><div>${{esc(r.dir_name)}}.mp4</div><div>${{esc(r.error_family)}} · ${{esc(r.interaction_primitive || r.scenario_domain)}}</div></div>
        <details><summary>最终问题卡片</summary><div class="issues">${{issues}}</div></details>
      </section>
      <section class="prompts">${{prompts.join('')}}</section>
    </div>
  </article>`;
}}
function render() {{
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  page = Math.min(page, pages - 1);
  const start = page * PAGE_SIZE, chunk = filtered.slice(start, start + PAGE_SIZE);
  $('cards').innerHTML = chunk.map((r,i)=>card(r,start+i)).join('') || '<div class="card">没有匹配任务</div>';
  $('count').textContent = `当前 ${{filtered.length}} / ${{RECORDS.length}} 个 task · 第 ${{page+1}} / ${{pages}} 页`;
  $('page').textContent = `${{page+1}} / ${{pages}}`;
  $('prev').disabled = page === 0;
  $('next').disabled = page >= pages - 1;
}}
document.addEventListener('click', async ev => {{
  const copy = ev.target.closest('[data-copy]');
  if (copy) {{
    await navigator.clipboard.writeText(copy.dataset.copy);
    const t = $('toast'); t.classList.add('show'); setTimeout(()=>t.classList.remove('show'), 900);
  }}
  const seek = ev.target.closest('[data-seek]');
  if (seek) {{
    const video = seek.closest('.card').querySelector('video');
    const t = Number(seek.dataset.seek);
    if (video.readyState >= 1) {{ video.currentTime = t; video.play().catch(()=>{{}}); }}
    else {{ video.addEventListener('loadedmetadata',()=>{{ video.currentTime=t; video.play().catch(()=>{{}}); }},{{once:true}}); video.load(); }}
  }}
}});
document.addEventListener('change', ev => {{
  const speed = ev.target.closest('[data-speed]');
  if (speed) speed.closest('.card').querySelector('video').playbackRate = Number(speed.value);
}});
function exportFiltered() {{
  const rows = filtered.map(r => ({{record_id:r.record_id, dir_name:r.dir_name, source:r.source, generator:r.generator, video_url:r.video_url, prompts:r.prompts}}));
  const blob = new Blob([JSON.stringify({{count: rows.length, records: rows}}, null, 2)], {{type:'application/json'}});
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'physfixbench_fixing_tasks_prompts.json'; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href), 1000);
}}
init();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
