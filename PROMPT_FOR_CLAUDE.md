# Prompt: set up a relocation model for me

**How to use this file.** Open this repository in an AI coding assistant (e.g.
Claude Code) and say *"Set up a relocation model for my situation — follow
PROMPT_FOR_CLAUDE.md."* The assistant should then follow the instructions below.
Everything the assistant needs to know about the mechanics is in `README.md` and
`score.py`; this file is the interview + fill-in workflow.

---

## Your role (assistant, read this)

You are helping a human turn their relocation decision into a weighted
multi-criteria model that `score.py` can rank. You will:

1. **Interview** them to understand their situation and priorities.
2. **Write** `config/criteria.yaml` (domains, weights, anchors, knockouts,
   sensitivity presets) from their answers.
3. **Help populate** `config/scores.csv` (country × criterion, 1–10) using public
   data sources, being explicit about which scores are researched vs. estimated.
4. **Run** `python score.py` and walk them through `output/report.md`.

Work in the `config/` directory (it holds a blank template). Do **not** edit
`examples/` — that is a frozen reference case. Keep the whole thing in the user's
language if they prefer, but code, YAML keys and CSV headers stay in English.

---

## Step 1 — Interview

Ask these in small batches, not all at once. Adapt follow-ups to their answers.
The goal is enough signal to choose *criteria* and *weights*, then to *score*.

**Situation**
- Who is moving (solo / couple / family; kids now or later)?
- Passport(s) — this usually drives the hardest visa constraints.
- Languages and level.
- Work: remote, local job hunt, freelance, retired, studying? For whom?
- Monthly budget, and whether it must cover visa income thresholds.
- Timeline and whether this is "settle for good" vs. "base for a few years".

**Priorities & deal-breakers**
- What are the non-negotiables? (These become **knockout filters**, not weighted
  criteria — e.g. "must have a legal visa route", "within 24h of home", "no active
  conflict".)
- What matters most day-to-day: money, safety, climate, career, community,
  proximity to home? Push them to rank, because weights must sum to 100.
- Any strong favorites or biases to test against the data?

**Climate / lifestyle specifics**
- Preferred climate (define what a 10 looks like for them — Mediterranean? cool?
  tropical?).
- Food, nature, city size, density preferences.

## Step 2 — Write `config/criteria.yaml`

- Group criteria into **domains** (Visa, Money, Quality of life, Society, Career,
  Logistics, Lifestyle — adapt to them).
- Assign **weights in percent that sum to 100**. Reflect the priority ranking from
  the interview; don't split evenly by default.
- For **every criterion**, write three **anchors** (low 1–3 / mid 4–6 / high 7–10)
  describing what that score means for *this* person. Anchors are what make scoring
  reproducible — don't skip them. Score inverted metrics (cost, distance) so 10 = best.
- Turn non-negotiables into the **knockouts** section (id + human label).
- Define 3–5 **sensitivity presets** that stress the biggest tensions in their
  priorities (e.g. `Visa-first`, `Money-first`, `Safety-first`, `Lifestyle-first`).
  Each preset overrides only a few weights on top of the baseline.
- Fill `report.title` and, optionally, a `leader_note`.

Use `examples/eu-relocation-couple/criteria.yaml` as a structural reference.

## Step 3 — Build the candidate list and score it

- Draft a **broad** candidate list, not just their favorites — the point is to let
  the real winner surface. Include the favorites as reference points.
- If any candidate clearly fails a knockout, put it in `config/knockouts.csv`
  (columns: `country`, then one column per knockout id with `pass`/`fail`, plus an
  optional `reason`). It will be excluded before scoring.
- Populate `config/scores.csv`: one row per surviving country, every criterion
  scored **1–10 (10 = best for this person)**. Header must be
  `country,region,<criterion ids…>`.
  - Pull raw numbers from the sources in the README table (Numbeo, PwC, Global
    Peace Index, EF EPI, WHO, etc.).
  - **Be transparent about confidence.** When a score is a judgement call or based
    on a regional proxy rather than a direct data point, tell the user and note it
    (e.g. in a `report.disclaimers` line). Never present an estimate as a hard
    figure.
  - Consider normalizing index-based criteria across your candidate set so weights
    express their full range (see the README "Design decisions" note); or just
    score directly on 1–10 if that's simpler for the user. Be consistent.

## Step 4 — Run and interpret

```bash
pip install -r requirements.txt
python score.py
```

Then open `config/output/report.md` and `config/output/ranking.xlsx` and explain:
- The **baseline ranking** and the gap between the top few (is the leader robust or
  a coin-flip?).
- The **sensitivity table**: which countries stay top under every preset, and where
  the leader flips. This is usually the most decision-relevant insight — surface it.
- Any **knocked-out** favorites and why.
- The **caveats** — especially that visa rules change and index data is imperfect.

Encourage the user to open the xlsx and edit the yellow weight row to feel the
trade-offs themselves. Close by stating what the model does *not* decide for them:
it structures the trade-off, it doesn't remove the judgement call.
