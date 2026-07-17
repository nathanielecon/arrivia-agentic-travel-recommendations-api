---
owner: P_portfolio and P_integration
status: failed visual assertion; repair required
candidate: 1a24156e381bdad09de8c554448cab6a17b320ec
detected_at: 2026-07-17
claim_impact: portfolio visual evidence only; certified runtime D5/E6 remains unchanged
---

# Walkthrough terminal-row overlap defect

User review of the current 160-second walkthrough exposed unreadable terminal rows at global
timestamp `00:01:17`, inside the dependency-failure scene. The four requests are intentional: the
first three qualify as circuit failures and the fourth proves fail-fast circuit-open behavior. The
white response text painted through green command text is not intentional.

The defect is present in both the final mux and source `partner-fault.mp4`: the recorder joins a
Python `-c` argument containing embedded newlines, gives the resulting string to Pillow as one draw
item, and advances the vertical cursor by only one `LINE_H`. Pillow renders the embedded newlines as
multiple rows, so later items overwrite them. The CLI footage separately clips its unwrapped command
at the right edge. The final-slot footage is clean.

The previously appended `EVID-POSTMERGE-PORTFOLIO-REFRESH` event is retained unchanged, including its
now-contradicted no-overlap assertion. This failure must be appended and later superseded by a new
candidate-bound media repair; it does not alter the production runtime source, image, interfaces, or
the already-earned D5/E6 boundary.

Artifact: `walkthrough-row-overlap-t77.png`, extracted from the tracked MP4 at exactly 77 seconds.
