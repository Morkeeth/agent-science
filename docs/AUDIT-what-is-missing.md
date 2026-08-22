---
date: 2026-08-22
lens: a judge · a human user · a VC
verdict: we built a JUDGE. We did not build a COLLEAGUE.
---

# What is missing

## The uncomfortable measurement

Powered leg A: **10 claims, 0 CLEARED.** Seven found real documents and were demoted.

We have been calling that rigour. **Look at it as the user.** A researcher pastes a
script and gets back ten rows, none cleared, seven saying *"a human must judge whether
this is independent support."* They still have to do every piece of the work — and now
they also have to read our report.

**We added a step. We did not remove one.** That is not a product, and no amount of
honesty about it makes it one.

## As a judge — Design is 25% of the score and it is our worst axis

Four criteria, equally weighted: Technological Implementation · **Design** · Potential
Impact · Quality of Idea.

The rubric says Design means *"a complete, coherent product experience."* We have a CLI
and a markdown file. A judge who opens the hosted URL sees a paste box and gets back a
wall of text with almost nothing cleared. **Tech and Idea are strong; Design is a C, and
it is a quarter of the marks.**

## As a human user — the refusals are a wall, not a work list

Every UNVERIFIED INDEPENDENCE row is the product saying *"I found something, I will not
count it, you figure it out."* The researcher's actual question is **"so what do I do
now?"** and we never answer it. A refusal without a next action is a complaint.

## As a VC — three things break the investment case

**1. The unit of value is wrong.** We sell *claims checked*. Nobody buys a checked
claim. They buy **insurability**: the E&O submission that lets a film be distributed.
The gap report is an input to that document; it is not the document.

**2. The moat is per-user, and it should be per-market.** Our corpus compounds inside
one customer's subject. The real network effect is across customers — every production
that establishes "Directive 2012/28/EU was adopted 25 October 2012, primary source
EUR-Lex" makes that claim free for every subsequent production, forever. **That is the
company. We have not built it and we have not claimed it.**

**3. It does not do the work.** An agent that grades a researcher's homework is a
feature. An agent that *does the research and hands back a signed pack* is a company.

---

# The three things to build, in order

## 1 · ESCALATION — try harder before refusing

When the first search returns only derived or unclassified origins, **go and look for a
primary source.** Re-query targeting registries, legislation, official publishers. The
product should exhaust the search a human would do before it declines.

This is the honest fix for 0-of-10 — not a bigger allowlist, not a looser rule. **The
allowlist stays strict; the effort goes up.** Measurable: cleared count before vs after,
on the same script.

## 2 · THE RESOLUTION QUEUE — every refusal gets a next action

- `UNVERIFIED INDEPENDENCE` → *"we found it at eifl.net; the primary source is likely
  EUR-Lex 32012L0028 — confirm the article"*
- `search_found_no_admissible_source` → *"nothing on the open web states this; it may
  need a rightsholder enquiry or a paywalled database"*
- `DISPUTED` → *"the document says 2012, the script says 2013 — the script is wrong"*

**A refusal becomes a task. The gap report becomes a work list.**

## 3 · THE DOSSIER — the artifact that is actually bought

One document per production: every claim, its verdict, its source, its verbatim quote,
its next action, and the denominator. The thing a clearance attorney signs and an
underwriter prices. **That is what makes this insurable, and insurability is the sale.**
