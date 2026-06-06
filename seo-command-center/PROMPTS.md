# PROMPTS.md — my key prompts log

Keep the handful of prompts that actually moved the build. Not every message — the ones that
mattered: the system/sub-agent prompts, the ones you iterated on, the "this finally worked"
moment. This shows how you direct an AI, which is graded (challenge brief section 08).

Format per entry:
- **Prompt** (paste it)
- **For:** what you were trying to do
- **Revised?** did you have to change it, and why

---

## Example (replace with your own)

- **Prompt:** "Extend seo/detector.py to detect redirect chains: build a map of {Address ->
  Redirect URL} for all 3xx rows, then a chain exists when a Redirect URL is itself a key in
  that map. Add a redirect_chain issue (High). Run python seo/detector.py and show counts."
- **For:** adding the redirect-chain detector
- **Revised?** Yes — first version flagged single redirects as chains; added the "target is
  also a redirecting URL" condition.

---

## My prompts
1. **Prompt:** "Read Claude.md, seo/detector.py, and run.py. Then run python run.py ../     sample-export/ and show me the output." 
   **For:** "Understanding the full pipeline and confirming it runs end to end.
   **Revised?** No - worked first time. 12 issue types detected.

2. **Prompt:** "Complete all 18 rulebook detectors in seo/detector.py - add title_too_short, missing_meta_description, duplicate_meta_description, meta_description_too_long, missing_h1, duplicate_h1, redirect_chain, thin _content, non_indexable_but_linked, slow_page."
   **For:** Getting full rulebook coverage for maximum accuracy score. 
   **Revised?** No - all the detectors were added successfullyin one pass. 
