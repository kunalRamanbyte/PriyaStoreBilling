# AGENTS.md

**Read [CLAUDE.md](CLAUDE.md) instead — it is the single authoritative guide for
this repository, for every agent and for humans.**

This file used to be a hand-copied duplicate of CLAUDE.md. It drifted, and the
stale copy actively taught patterns the codebase now forbids — most dangerously
that bill numbers should be claimed with `next_bill_number()` and then bumped by
a post-commit `increment_bill_number()`, which lets two tills issue the same
bill number. `database._claim_number()` now does it inside the document's own
`BEGIN IMMEDIATE` transaction.

Nothing is documented here any more, so there is nothing left to drift. Add
project guidance to CLAUDE.md.
