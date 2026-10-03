#!/usr/bin/env python3
"""GCOY-WRITEUP: CTF writeup 沉淀工具。零依赖，单文件，Python 3.10+。"""

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

CATS = ["web", "pwn", "reverse", "crypto", "misc", "forensics", "osint"]
STATUS = ["draft", "solved"]

TMPL = """# {title}

| 字段 | 值 |
| --- | --- |
| ID | {wid} |
| 分类 | {cat} |
| 分值 | {pts} |
| 赛事 | {event} |
| 状态 | {status} |
| 日期 | {today} |
| FLAG | {flag} |

## 题目描述

（附件、给题方式、题目链接）

## 思路

（第一直觉、关键观察）

## 步骤

1.
2.

## FLAG

```
{flag}
```

## 复盘

（卡了多久、学到什么、下次怎么更快）
"""


def home(args):
    root = Path(getattr(args, "root", None) or os.environ.get("GCOY_WRITEUP_HOME", "."))
    return root / "writeups"


def load_index(hdir):
    f = hdir / "index.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {"seq": 0, "items": []}


def save_index(hdir, idx):
    hdir.mkdir(parents=True, exist_ok=True)
    (hdir / "index.json").write_text(
        json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def find_item(idx, wid):
    for it in idx["items"]:
        if it["id"] == wid:
            return it
    return None


def slugify(title):
    s = re.sub(r"[^\w-]+", "-", title.strip(), flags=re.UNICODE)
    return s.strip("-")[:40] or "untitled"


def cmd_new(args):
    hdir = home(args)
    idx = load_index(hdir)
    idx["seq"] += 1
    wid = f"{idx['seq']:04d}"
    if args.cat not in CATS:
        sys.exit(f"未知分类 {args.cat}，可选：{'/'.join(CATS)}")
    title = args.title
    item = {
        "id": wid,
        "title": title,
        "cat": args.cat,
        "pts": args.pts,
        "event": args.event or "-",
        "status": "draft",
        "flag": "",
        "date": date.today().isoformat(),
        "file": f"{wid}-{slugify(title)}.md",
    }
    idx["items"].append(item)
    save_index(hdir, idx)
    path = hdir / item["file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        TMPL.format(
            title=title,
            wid=wid,
            cat=args.cat,
            pts=args.pts,
            event=item["event"],
            status="draft",
            today=item["date"],
            flag="待填写",
        ),
        encoding="utf-8",
    )
    print(f"[+] {wid} {title} ({args.cat}, {args.pts}pts) -> {path}")


def cmd_done(args):
    hdir = home(args)
    idx = load_index(hdir)
    item = find_item(idx, args.wid)
    if not item:
        sys.exit(f"找不到 writeup {args.wid}")
    item["flag"] = args.flag
    item["status"] = "solved"
    save_index(hdir, idx)
    path = hdir / item["file"]
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(\| 状态 \|).*", r"\1 solved |", text)
    text = re.sub(r"(\| FLAG \|).*", rf"\1 {args.flag} |", text)
    text = text.replace("```\n待填写\n```", f"```\n{args.flag}\n```")
    path.write_text(text, encoding="utf-8")
    print(f"[+] {args.wid} 标记 solved，flag 已写入")


def cmd_edit(args):
    hdir = home(args)
    idx = load_index(hdir)
    item = find_item(idx, args.wid)
    if not item:
        sys.exit(f"找不到 writeup {args.wid}")
    changed = []
    if args.title:
        item["title"] = args.title
        changed.append("title")
    if args.cat:
        item["cat"] = args.cat
        changed.append("cat")
    if args.pts is not None:
        item["pts"] = args.pts
        changed.append("pts")
    if args.event:
        item["event"] = args.event
        changed.append("event")
    if not changed:
        sys.exit("未指定要改的字段（--title/--cat/--pts/--event）")
    save_index(hdir, idx)
    path = hdir / item["file"]
    if path.exists():
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^# .*$", f"# {item['title']}", text, count=1)
        text = re.sub(r"(\| 分类 \|).*", rf"\1 {item['cat']} |", text)
        text = re.sub(r"(\| 分值 \|).*", rf"\1 {item['pts']} |", text)
        text = re.sub(r"(\| 赛事 \|).*", rf"\1 {item['event']} |", text)
        path.write_text(text, encoding="utf-8")
    print(f"[+] {args.wid} 已更新字段：{', '.join(changed)}")


def cmd_list(args):
    idx = load_index(home(args))
    if not idx["items"]:
        print("（空）先执行 new 创建第一篇")
        return
    print(f"{'ID':<5}{'分类':<10}{'分值':<6}{'状态':<8}{'赛事':<12}标题")
    for it in idx["items"]:
        print(
            f"{it['id']:<5}{it['cat']:<10}{it['pts']:<6}{it['status']:<8}{it['event']:<12}{it['title']}"
        )


def cmd_stats(args):
    idx = load_index(home(args))
    items = idx["items"]
    if not items:
        print("（空）")
        return
    by = {}
    for it in items:
        d = by.setdefault(it["cat"], {"n": 0, "solved": 0, "pts": 0})
        d["n"] += 1
        if it["status"] == "solved":
            d["solved"] += 1
            d["pts"] += it["pts"]
    total_solved = sum(d["solved"] for d in by.values())
    total_pts = sum(d["pts"] for d in by.values())
    print(f"总计 {len(items)} 题 | solved {total_solved} | 得分 {total_pts}")
    print(f"{'分类':<12}{'总题数':<8}{'solved':<8}{'得分':<8}")
    for c in CATS:
        if c in by:
            d = by[c]
            print(f"{c:<12}{d['n']:<8}{d['solved']:<8}{d['pts']:<8}")
    weak = [c for c in CATS if c in by and by[c]["solved"] < by[c]["n"]]
    if weak:
        print(f"建议主攻：{'/'.join(weak)}（存在未解决题目）")


def md_to_html(md):
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre>" + "\n".join(buf).replace("&", "&amp;").replace("<", "&lt;") + "</pre>")
        elif re.match(r"^#{1,3} ", ln):
            lvl = len(ln) - len(ln.lstrip("#"))
            out.append(f"<h{lvl}>{ln[lvl + 1:]}</h{lvl}>")
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if not all(re.fullmatch(r"-{2,}", c) for c in cells):
                    rows.append(cells)
                i += 1
            t = "<table><tr>" + "".join(f"<th>{c}</th>" for c in rows[0]) + "</tr>"
            for r in rows[1:]:
                t += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
            out.append(t + "</table>")
        elif ln.strip():
            out.append(f"<p>{ln}</p>")
            i += 1
        else:
            i += 1
    return "\n".join(out)


STYLE = (
    "body{font-family:system-ui,sans-serif;max-width:880px;margin:24px auto;padding:0 16px;"
    "color:#1c2733;line-height:1.6}table{border-collapse:collapse;margin:8px 0}th,td{border:1px solid #ccd;"
    "padding:4px 10px}pre{background:#0f1720;color:#d7e3ee;padding:12px;overflow-x:auto;border-radius:6px}"
    "h2{border-bottom:1px solid #dde;margin-top:28px}details{margin:16px 0}summary{cursor:pointer;font-weight:700}"
    ".stat{background:#f2f6fa;border-radius:8px;padding:10px 16px}"
)


def cmd_export(args):
    hdir = home(args)
    idx = load_index(hdir)
    items = idx["items"]
    parts = [
        "<!doctype html><meta charset='utf-8'><title>CTF Writeups</title>",
        f"<style>{STYLE}</style><h1>CTF Writeups</h1>",
    ]
    solved = [it for it in items if it["status"] == "solved"]
    parts.append(
        f"<div class='stat'>{len(items)} 题 | solved {len(solved)} | "
        f"得分 {sum(i['pts'] for i in solved)}</div>"
    )
    for it in items:
        f = hdir / it["file"]
        body = md_to_html(f.read_text(encoding="utf-8")) if f.exists() else "<p>缺失</p>"
        parts.append(
            f"<details><summary>[{it['id']}] {it['title']} "
            f"（{it['cat']} / {it['pts']}pts / {it['status']}）</summary>{body}</details>"
        )
    out = Path(args.out)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"[+] 已导出 {out.resolve()}")


def cmd_selftest(args):
    tmp = tempfile.mkdtemp(prefix="gcoy-selftest-")
    base = ["--root", tmp]
    def run(*a):
        main(["--root", tmp] + list(a))
    run("new", "ezywaf-bypass", "--cat", "web", "--pts", "200", "--event", "TestCTF")
    run("new", "rot-riddle", "--cat", "crypto", "--pts", "100")
    run("done", "0001", "--flag", "flag{t3st_0k}")
    run("edit", "0002", "--pts", "150", "--event", "RealCTF")
    run("list")
    run("stats")
    run("export", "--out", os.path.join(tmp, "report.html"))
    idx = load_index(home(argparse.Namespace(root=tmp)))
    assert idx["seq"] == 2 and idx["items"][0]["status"] == "solved"
    assert idx["items"][1]["pts"] == 150 and idx["items"][1]["event"] == "RealCTF"
    html = Path(tmp, "report.html").read_text(encoding="utf-8")
    assert "flag{t3st_0k}" in html
    md = (Path(tmp, "writeups", idx["items"][0]["file"])).read_text(encoding="utf-8")
    assert "| 状态 | solved |" in md
    print("[selftest] OK ->", tmp)


def main(argv=None):
    p = argparse.ArgumentParser(prog="gcoy-writeup", description="CTF writeup 沉淀工具")
    p.add_argument("--root", default=None, help="工作目录（默认当前目录）")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("new", help="新建 writeup")
    s.add_argument("title")
    s.add_argument("--cat", required=True, choices=CATS)
    s.add_argument("--pts", type=int, default=100)
    s.add_argument("--event", default="")
    s.set_defaults(fn=cmd_new)
    s = sub.add_parser("done", help="标记 solved 并写入 flag")
    s.add_argument("wid")
    s.add_argument("--flag", required=True)
    s.set_defaults(fn=cmd_done)
    s = sub.add_parser("edit", help="修改 writeup 元数据")
    s.add_argument("wid")
    s.add_argument("--title", default=None)
    s.add_argument("--cat", default=None, choices=CATS)
    s.add_argument("--pts", type=int, default=None)
    s.add_argument("--event", default=None)
    s.set_defaults(fn=cmd_edit)
    s = sub.add_parser("list", help="列出全部")
    s.set_defaults(fn=cmd_list)
    s = sub.add_parser("stats", help="分类统计与薄弱项")
    s.set_defaults(fn=cmd_stats)
    s = sub.add_parser("export", help="导出单文件 HTML 战报")
    s.add_argument("--out", default="writeups-report.html")
    s.set_defaults(fn=cmd_export)
    s = sub.add_parser("selftest", help="自检")
    s.set_defaults(fn=cmd_selftest)
    args = p.parse_args(argv)
    if not hasattr(args, "root"):
        args.root = None
    args.fn(args)


if __name__ == "__main__":
    main()
