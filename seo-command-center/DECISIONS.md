# DECISIONS.md — decision & learnings log

A short running note of the real choices you made: what you tried, what failed and why, what
you changed. This is your engineering judgement on the record — it is what separates a builder
from a button-presser, and it is graded (challenge brief section 08).

Append a 1–2 line entry whenever you make a real decision or hit/fix a wall. Add a timestamp.

Format:
`[HH:MM] <decision or problem> → <what you did and why>`

---

## Example (replace with your own)
- `[10:20]` Chose plain-csv parsing over pandas → fewer deps, fast enough for 5k rows, model
  quota saved for the fixer.
- `[11:05]` Title detector over-counted duplicates → realized non-indexable pages were
  included; added an indexable+200 filter (per rulebook).
- `[12:40]` Dashboard wasn't updating live → MCP tool wasn't emitting the SSE event; added
  `_emit("issue", row)` in extract.

---

## My log
- `[10:15]` extracted starter bundle and run first test -> pipeline works end to end, 12 issue      types were detected on sample export.
- `[10:30]` I reviewed detector.py -> starter only had 7 rules, completed all rulebook rules in plain Python/csv.
- `[10:45]` I chose not to use pandas -> as standard csv library is faster, fewer dependencies, and also saves quota for model fixes.
- `[13:30]` I Added title fixer using Ollama API -> targets first 5 missing_title URLs, uses H1 or slug as context, validates 30 - 60 char length.
- `[14:00]` The full pipeline is tested end to end -> report.json, report.html, report.pptx all were generated successfully from sample export. 
- `[14:05]` All the 3 required output formats are working -> ready for hidden export test. 
