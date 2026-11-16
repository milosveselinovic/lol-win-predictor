"""Download match timelines of top EUNE players from the Riot API.

Usage:  python src/collect.py 200      (200 = how many matches to download)
Each timeline is saved as data/raw/<match_id>.json. Already downloaded
matches are skipped, so the script can be stopped and restarted any time.
"""
import truststore; truststore.inject_into_ssl()  # use Windows certificates (needed behind antivirus HTTPS scanning)

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PLATFORM = "https://eun1.api.riotgames.com"   # EUNE server: player rankings
REGION = "https://europe.api.riotgames.com"    # match data for EU servers
RANKED_SOLO = 420                              # Riot's queue id for Ranked Solo/Duo
RAW_DIR = Path("data/raw")

load_dotenv()
session = requests.Session()
session.headers["X-Riot-Token"] = os.environ["RIOT_API_KEY"]


def get(url, **params):
    """GET a Riot API url, waiting and retrying when we hit the rate limit."""
    while True:
        # shortcut: fixed 1.2 s pause fits the dev key limit (100 requests / 2 min); upgrade with a production key
        time.sleep(1.2)
        r = session.get(url, params=params, timeout=30)
        if r.status_code == 429:  # too many requests: Riot tells us how long to wait
            wait = int(r.headers.get("Retry-After", 10))
            print(f"  rate limited, waiting {wait}s")
            time.sleep(wait)
            continue
        r.raise_for_status()  # stop on any other error (e.g. 401/403 = expired key)
        return r.json()


def top_players():
    """PUUIDs of all Challenger and Grandmaster players on EUNE."""
    puuids = []
    for tier in ["challengerleagues", "grandmasterleagues"]:
        league = get(f"{PLATFORM}/lol/league/v4/{tier}/by-queue/RANKED_SOLO_5x5")
        puuids += [entry["puuid"] for entry in league["entries"]]
    return puuids


def main(target):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    have = {p.stem for p in RAW_DIR.glob("*.json")}
    print(f"Already downloaded: {len(have)} matches, target: {target}")

    for puuid in top_players():
        if len(have) >= target:
            break
        match_ids = get(f"{REGION}/lol/match/v5/matches/by-puuid/{puuid}/ids", queue=RANKED_SOLO, count=20)
        for match_id in match_ids:
            if len(have) >= target:
                break
            if match_id in have:  # top players often share games, don't download twice
                continue
            timeline = get(f"{REGION}/lol/match/v5/matches/{match_id}/timeline")
            (RAW_DIR / f"{match_id}.json").write_text(json.dumps(timeline))
            have.add(match_id)
            print(f"[{len(have)}/{target}] {match_id}")

    print("Done.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
