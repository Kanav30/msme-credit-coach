# Phase 5 — Real User Testing Kit

## Outreach message templates

**For a warm contact (family/friend running a business):**
> "Hi [Name], I'm building a college project — an app that helps small businesses understand their credit score and what to do to improve it. Would you be open to a 15-minute chat where I ask a few general questions and show you what it says? No documents or sensitive info needed, just your general sense of a few things."

**For a CA/consultant:**
> "Hi [Name], I'm a [year] engineering student building a tool that helps MSMEs understand their CIBIL MSME Rank and get a concrete action plan to improve it. Since you work with MSME clients regularly, I'd really value 15-20 minutes of your perspective — either based on a typical client profile from memory, or an introduction to a client open to a short chat. Nothing sensitive needed on either side."

## The interview script (15-20 minutes)

**Opening (1 min):** Introduce yourself, explain it's a college prototype (not a real financial product), and explicitly say you won't ask for any documents or account access — just their general sense of a few things.

**Plain-language inputs (5 min)** — map directly to the diagnostic engine's fields:
- "Roughly, in the last year, what % of your loan or credit card payments would you say were on time?"
- "Have you had any late payment in the last 2-3 months, even a small one?"
- "Roughly how much of your available credit limit are you using — more than half, about half, or well under half?"
- "How many years have you had a business loan or credit line?"
- "How many years has your business been operating?"
- "Would you describe your industry as generally stable, or more seasonal/volatile?"
- Optional, only if they're comfortable: "Do you happen to know your CIBIL MSME Rank or a rough score range?" — purely to sanity-check, never required.

**Run it live (5 min):** Feed their answers into the demo tool (`ml/notebooks/demo_cli.py`), and walk through the output with them.

**Feedback questions (5-8 min):**
- "Does this explanation match what you understand about your own situation?"
- "Would this specific advice be something you'd actually act on?"
- "Does the priority order make sense to you, or would you have expected something else first?"
- "If you've been rejected for a loan before, does this help explain why, looking back?"
- "Would you actually use an app like this? What would stop you?"
- "Was anything confusing or did any term need explaining?"

## Feedback log — copy this block for every session

```
Date:
Tester type (business owner / CA / other):
Sector:
Inputs given: payment%=__  recent_delinquency=__  utilization=__  tenure=__  age=__  risk=__
App's estimated rank:
Did it match their own sense of their situation? (Y/N + notes):
Which recommendation did they react to most?
Would they act on it? (Y/N + why):
Confusing terms/moments:
Best quote from the session:
One thing to change before the next session:
```

Even 2-3 real sessions like this is a meaningful, genuine Phase 5 result for a student project — don't feel like you need dozens to have something worth reporting.
