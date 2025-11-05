#!/usr/bin/env python3
"""
github_time_series_metrics_csv.py
Collects GitHub traffic and release download metrics, with options to:
  1. Get 14-day time series for clones, visitors, and downloads
  2. Fetch only yesterday’s clones/visitors data

Usage:
    python github_time_series_metrics_csv.py OWNER REPO [--outdir PATH] [--yesterday]
Environment:
    GITHUB_TOKEN must be set to a token with repo (push) access.
Requires:
    pip install requests pandas
"""

import os
import argparse
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta

def get_json(url, headers):
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def get_clone_timeseries(owner, repo, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/traffic/clones"
    data = get_json(url, headers)
    rows = []
    for c in data.get("clones", []):
        ts = datetime.fromisoformat(c["timestamp"].replace("Z", "+00:00"))
        rows.append({
            "date": ts.date().isoformat(),
            "clone_count": c["count"],
            "clone_uniques": c["uniques"]
        })
    return rows

def get_visitor_timeseries(owner, repo, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/traffic/views"
    data = get_json(url, headers)
    rows = []
    for v in data.get("views", []):
        ts = datetime.fromisoformat(v["timestamp"].replace("Z", "+00:00"))
        rows.append({
            "date": ts.date().isoformat(),
            "visitor_count": v["count"],
            "visitor_uniques": v["uniques"]
        })
    return rows

def get_release_download_snapshot(owner, repo, headers):
    today = datetime.now(timezone.utc).date().isoformat()
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    all_downloads = []
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        for rel in r.json():
            tag = rel.get("tag_name") or rel.get("name") or str(rel.get("id"))
            for a in rel.get("assets", []):
                all_downloads.append({
                    "date": today,
                    "release_tag": tag,
                    "asset_name": a["name"],
                    "asset_download_count": a["download_count"]
                })
        url = r.links.get("next", {}).get("url")
    return all_downloads

def append_csv(path, df):
    if os.path.exists(path):
        df.to_csv(path, mode="a", header=False, index=False)
    else:
        df.to_csv(path, index=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("owner")
    parser.add_argument("repo")
    parser.add_argument("--outdir", default=".", help="Output directory (default: current)")
    parser.add_argument("--yesterday", action="store_true",
                        help="Only save yesterday’s clones and visitors instead of the full 14-day window")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Environment variable GITHUB_TOKEN not set — required for traffic endpoints.")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }

    # --- Fetch traffic metrics
    clone_rows = get_clone_timeseries(args.owner, args.repo, headers)
    visitor_rows = get_visitor_timeseries(args.owner, args.repo, headers)
    dl_rows = get_release_download_snapshot(args.owner, args.repo, headers)

    # --- Filter to yesterday if requested
    if args.yesterday:
        yest = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        clone_rows = [r for r in clone_rows if r["date"] == yest]
        visitor_rows = [r for r in visitor_rows if r["date"] == yest]
        dl_rows = [r for r in dl_rows if r["date"] == yest]

    # --- Convert to DataFrames
    df_clones = pd.DataFrame(clone_rows)
    df_visitors = pd.DataFrame(visitor_rows)
    df_downloads = pd.DataFrame(dl_rows)

    os.makedirs(args.outdir, exist_ok=True)
    clones_path = os.path.join(args.outdir, "clones_timeseries.csv")
    visitors_path = os.path.join(args.outdir, "visitors_timeseries.csv")
    downloads_path = os.path.join(args.outdir, "downloads_snapshot.csv")

    if not df_clones.empty: append_csv(clones_path, df_clones)
    if not df_visitors.empty: append_csv(visitors_path, df_visitors)
    if not df_downloads.empty: append_csv(downloads_path, df_downloads)

    print(f"Clones → {clones_path} ({len(df_clones)} rows)")
    print(f"Visitors → {visitors_path} ({len(df_visitors)} rows)")
    print(f"Downloads → {downloads_path} ({len(df_downloads)} rows)")
    if args.yesterday:
        print("📆 Mode: yesterday only")

if __name__ == "__main__":
    main()
