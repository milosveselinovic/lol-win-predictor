# When Is a League of Legends Game Actually Lost?

A minute-by-minute **win probability model** for League of Legends, built on match data collected from the Riot Games API.

> Work in progress.

## Questions
- How does a gold deficit at minute 15 compare to the same deficit at minute 30?
- How much do objectives (Dragon, Baron, towers) actually move win probability?
- Which comebacks were the most unlikely?

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and add your Riot API key.

## Data
Match timelines of EUNE Challenger and Grandmaster players (Ranked Solo/Duo), collected with:
```bash
python src/collect.py 1000
```
Raw timelines are saved to `data/raw/` (not committed).
