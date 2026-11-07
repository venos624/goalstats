"""Refresh the site's data from football-data.co.uk.

Writes:
  matches.csv   every played match of the current season (22 leagues)
  fixtures.csv  upcoming fixtures with average odds
  updated.txt   date of the last refresh (UTC)

Run:  python update_data.py
Test with local files instead of downloading:
      python update_data.py --results-xlsx all-euro-data.xlsx --fixtures-csv fixtures.csv
"""
import argparse
import datetime as dt
import io
import sys
import time
from pathlib import Path

import pandas as pd
import requests

LEAGUES = ["E0", "E1", "E2", "E3", "EC", "SC0", "SC1", "SC2", "SC3", "D1", "D2",
           "SP1", "SP2", "I1", "I2", "F1", "F2", "B1", "N1", "P1", "T1", "G1"]
BASE = "https://www.football-data.co.uk"
# Check this link once on https://www.football-data.co.uk/matches.php ("Upcoming fixtures")
FIXTURES_URL = BASE + "/fixtures.csv"
OUT = Path(__file__).resolve().parent  # files live next to index.html
HEADERS = {"User-Agent": "Mozilla/5.0 (site data refresh)"}


def season_code(today: dt.date) -> str:
    """'2627' for the 2026/27 season (seasons start in July)."""
    start = today.year if today.month >= 7 else today.year - 1
    return f"{start % 100:02d}{(start + 1) % 100:02d}"


def read_csv_bytes(content: bytes) -> pd.DataFrame:
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(content), encoding=enc, on_bad_lines="skip")
        except UnicodeDecodeError:
            continue
    raise ValueError("could not decode CSV")


def get(url: str) -> bytes:
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
            r.raise_for_status()
            return r.content
        except requests.RequestException as e:
            if attempt == 2:
                raise
            print(f"  retry {url}: {e}", file=sys.stderr)
            time.sleep(5)


def clean_matches(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=lambda c: str(c).strip().lstrip("﻿"))
    df = df.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"])
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["Date"])
    df["FTHG"] = df["FTHG"].astype(int)
    df["FTAG"] = df["FTAG"].astype(int)
    return df[["Div", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]]


def load_results(args) -> pd.DataFrame:
    if args.results_xlsx:
        sheets = pd.read_excel(args.results_xlsx, sheet_name=None)
        return pd.concat([clean_matches(s) for k, s in sheets.items() if k in LEAGUES], ignore_index=True)
    code = season_code(dt.date.today())
    frames = []
    for div in LEAGUES:
        url = f"{BASE}/mmz4281/{code}/{div}.csv"
        try:
            frames.append(clean_matches(read_csv_bytes(get(url))))
            print(f"  {div}: ok")
        except Exception as e:  # one league failing should not stop the rest
            print(f"  {div}: skipped ({e})", file=sys.stderr)
    if not frames:
        raise SystemExit("No results downloaded; keeping the old data.")
    return pd.concat(frames, ignore_index=True)


def load_fixtures(args) -> pd.DataFrame:
    raw = Path(args.fixtures_csv).read_bytes() if args.fixtures_csv else get(FIXTURES_URL)
    f = read_csv_bytes(raw).rename(columns=lambda c: str(c).strip().lstrip("﻿"))
    f = f[f["Div"].isin(LEAGUES)].copy()
    f["Date"] = pd.to_datetime(f["Date"], dayfirst=True, errors="coerce").dt.strftime("%Y-%m-%d")
    f = f.dropna(subset=["Date", "HomeTeam", "AwayTeam"])
    keep = {"AvgH": "AvgH", "AvgD": "AvgD", "AvgA": "AvgA", "Avg>2.5": "AvgOver25", "Avg<2.5": "AvgUnder25"}
    for src in keep:
        if src not in f.columns:
            f[src] = None
    f = f[["Div", "Date", "Time", "HomeTeam", "AwayTeam", *keep]].rename(columns=keep)
    f = f.sort_values(["Date", "Time"]).reset_index(drop=True)
    f.insert(0, "id", range(1, len(f) + 1))
    return f


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results-xlsx")
    p.add_argument("--fixtures-csv")
    args = p.parse_args()
    OUT.mkdir(exist_ok=True)

    print("Results…")
    m = load_results(args).sort_values(["Date", "Div"])
    print("Fixtures…")
    try:
        f = load_fixtures(args)
    except Exception as e:
        print(f"Fixtures not updated ({e}); keeping the old file.", file=sys.stderr)
        f = None

    known = set(m.HomeTeam) | set(m.AwayTeam)
    if f is not None:
        missing = sorted((set(f.HomeTeam) | set(f.AwayTeam)) - known)
        if missing:
            print("Teams in fixtures with no results yet (shown with no stats):", ", ".join(missing))
        f.to_csv(OUT / "fixtures.csv", index=False)
    m.to_csv(OUT / "matches.csv", index=False)
    (OUT / "updated.txt").write_text(dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y") + "\n")
    print(f"Done: {len(m)} matches, {0 if f is None else len(f)} fixtures.")


if __name__ == "__main__":
    main()
