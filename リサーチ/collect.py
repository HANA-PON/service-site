#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「Claude Codeで会社を回す」系の伸びている動画を yt-dlp で収集するスクリプト。

条件:
  - 直近 N 日以内に投稿された動画（既定 180 日 = 約半年）
  - 登録者が少ないチャンネル（既定 3 万人以下）
  - それなりに再生されている（既定 1 万再生以上）
  - 「登録者のわりに伸びている」= 再生数 / 登録者数 の比率が高い順に上位 10 本

出力:
  out/candidates.json  … 全候補のメタデータ
  out/selected.json    … 条件を満たした上位 10 本
  out/selected.csv     … 同上（表計算で開ける形）
  out/subs/            … 選ばれた動画の字幕（自動生成字幕含む）
  out/transcripts/     … 字幕をプレーンテキストに整形したもの

前提:
  pip install yt-dlp
  ネットワークから www.youtube.com に到達できること

使い方:
  python3 collect.py                 # 収集 → 選定 → 文字起こし取得まで一気に
  python3 collect.py --no-subs       # メタデータの選定だけ
  python3 collect.py --days 90 --max-subs 10000
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# 検索クエリ。狙うテーマに合わせて増減させる。
QUERIES = [
    "Claude Code 会社 経営 AI社員",
    "Claude Code 会社を回す",
    "Claude Code 一人会社 自動化",
    "Claude Code AIチーム 組織",
    "Claude Code サブエージェント 業務自動化",
    "Claude Code 個人事業主 仕組み化",
    "Claude Code 会社 作ってみた",
]

# 1 クエリあたり何件まで拾うか
PER_QUERY = 30

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def run_json(args):
    """yt-dlp を実行して JSON Lines を辞書のリストで返す。"""
    proc = subprocess.run(args, capture_output=True, text=True)
    rows = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    if not rows and proc.returncode != 0:
        print(f"  ! yt-dlp 失敗: {proc.stderr.strip().splitlines()[-1:] or proc.returncode}",
              file=sys.stderr)
    return rows


def search_ids(query, limit):
    """検索して動画 ID を集める（軽量な flat モード）。"""
    rows = run_json([
        "yt-dlp", "--flat-playlist", "--dump-json",
        "--ignore-errors", "--no-warnings",
        f"ytsearch{limit}:{query}",
    ])
    return [r["id"] for r in rows if r.get("id")]


def fetch_meta(video_id):
    """動画 1 本の詳細メタデータを取得する（登録者数はここでしか取れない）。"""
    rows = run_json([
        "yt-dlp", "--dump-json", "--skip-download",
        "--ignore-errors", "--no-warnings",
        "--sleep-requests", "1",
        f"https://www.youtube.com/watch?v={video_id}",
    ])
    if not rows:
        return None
    r = rows[0]
    return {
        "id": r.get("id"),
        "title": r.get("title"),
        "channel": r.get("channel") or r.get("uploader"),
        "channel_id": r.get("channel_id"),
        "subscribers": r.get("channel_follower_count"),
        "views": r.get("view_count"),
        "likes": r.get("like_count"),
        "comments": r.get("comment_count"),
        "upload_date": r.get("upload_date"),  # YYYYMMDD
        "duration_sec": r.get("duration"),
        "url": r.get("webpage_url"),
        "description": (r.get("description") or "")[:2000],
    }


def within_days(upload_date, days):
    if not upload_date:
        return False
    try:
        d = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return d >= datetime.now(timezone.utc) - timedelta(days=days)


def srt_to_text(path):
    """SRT / VTT からタイムコードと重複行を落としてプレーンテキストにする。"""
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.isdigit() or "-->" in line or line.startswith("WEBVTT"):
            continue
        line = re.sub(r"<[^>]+>", "", line)          # <c> などのタグを除去
        line = re.sub(r"\[[^\]]*\]", "", line).strip()  # [音楽] などを除去
        if not line:
            continue
        if lines and lines[-1] == line:              # 自動字幕にありがちな重複
            continue
        lines.append(line)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=180, help="何日以内の投稿に絞るか")
    ap.add_argument("--max-subs", type=int, default=30000, help="登録者数の上限")
    ap.add_argument("--min-views", type=int, default=10000, help="再生数の下限")
    ap.add_argument("--min-ratio", type=float, default=1.0,
                    help="再生数 / 登録者数 の下限（1.0 = 登録者と同数以上再生された）")
    ap.add_argument("--top", type=int, default=10, help="最終的に選ぶ本数")
    ap.add_argument("--no-subs", action="store_true", help="字幕をダウンロードしない")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)

    # 1) 検索して候補 ID を集める
    ids = []
    for q in QUERIES:
        print(f"[検索] {q}")
        found = search_ids(q, PER_QUERY)
        print(f"  → {len(found)} 件")
        ids.extend(found)
    ids = list(dict.fromkeys(ids))  # 重複除去（順序は保つ）
    print(f"\n候補 {len(ids)} 本のメタデータを取得します\n")

    # 2) 1 本ずつ詳細を取る
    metas = []
    for i, vid in enumerate(ids, 1):
        m = fetch_meta(vid)
        if m:
            metas.append(m)
        print(f"  [{i}/{len(ids)}] {vid} {'ok' if m else 'skip'}")

    with open(os.path.join(OUT, "candidates.json"), "w", encoding="utf-8") as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)

    # 3) 条件で絞って「登録者のわりに伸びている順」に並べる
    picked = []
    for m in metas:
        subs, views = m.get("subscribers"), m.get("views")
        if not subs or not views:
            continue
        if not within_days(m.get("upload_date"), args.days):
            continue
        if subs > args.max_subs or views < args.min_views:
            continue
        ratio = views / subs
        if ratio < args.min_ratio:
            continue
        m["ratio"] = round(ratio, 2)
        picked.append(m)

    picked.sort(key=lambda x: x["ratio"], reverse=True)
    picked = picked[:args.top]

    with open(os.path.join(OUT, "selected.json"), "w", encoding="utf-8") as f:
        json.dump(picked, f, ensure_ascii=False, indent=2)

    cols = ["ratio", "views", "subscribers", "upload_date", "duration_sec",
            "likes", "comments", "channel", "title", "url"]
    with open(os.path.join(OUT, "selected.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(picked)

    print(f"\n条件を満たした動画: {len(picked)} 本")
    for m in picked:
        print(f"  x{m['ratio']:>6}  {m['views']:>9,}再生 / 登録{m['subscribers']:>7,}  "
              f"{m['upload_date']}  {m['title'][:50]}")

    if args.no_subs or not picked:
        return

    # 4) 字幕を落として文字起こしに整形する
    subs_dir = os.path.join(OUT, "subs")
    tr_dir = os.path.join(OUT, "transcripts")
    os.makedirs(subs_dir, exist_ok=True)
    os.makedirs(tr_dir, exist_ok=True)

    print("\n字幕を取得します")
    for m in picked:
        subprocess.run([
            "yt-dlp", "--skip-download",
            "--write-subs", "--write-auto-subs",
            "--sub-langs", "ja,ja-orig,en",
            "--convert-subs", "srt",
            "--sleep-requests", "1",
            "--ignore-errors", "--no-warnings",
            "-o", os.path.join(subs_dir, "%(id)s.%(ext)s"),
            m["url"],
        ], capture_output=True, text=True)

        got = [n for n in os.listdir(subs_dir) if n.startswith(m["id"]) and n.endswith(".srt")]
        if not got:
            print(f"  - {m['id']} 字幕なし")
            continue
        text = srt_to_text(os.path.join(subs_dir, sorted(got)[0]))
        header = (f"# {m['title']}\n\n"
                  f"- チャンネル: {m['channel']}\n"
                  f"- URL: {m['url']}\n"
                  f"- 投稿日: {m['upload_date']}\n"
                  f"- 再生: {m['views']:,} / 登録: {m['subscribers']:,}（比率 x{m['ratio']}）\n\n"
                  f"---\n\n")
        with open(os.path.join(tr_dir, f"{m['id']}.md"), "w", encoding="utf-8") as f:
            f.write(header + text)
        print(f"  + {m['id']} {len(text):,} 文字")

    print(f"\n完了。文字起こし: {tr_dir}")


if __name__ == "__main__":
    main()
