# Social Listening Triage

This pattern models a fixture-safe social monitoring workflow:

1. Load a batch of exported social mentions.
2. Match configured keywords across mention text.
3. Score engagement from likes plus reposts.
4. Return a review queue with priority follow-ups.

The fixture uses Xquik-style social API output, but the pattern never calls a live
service. It is useful when a team wants to prototype monitoring rules before
connecting real social data, Slack delivery, or CRM enrichment.

## Inputs

- `monitor.name`: human-readable monitor name.
- `monitor.keywords`: keywords matched case-insensitively.
- `monitor.min_engagement`: threshold for priority review.
- `mentions[]`: exported mention records with `id`, `author`, `text`, `likes`,
  `reposts`, and `url`.

## Output

The pattern returns:

- matched mention count
- priority follow-up count
- matched keywords per mention
- engagement score per mention
- a concise summary for downstream review

## Automation Fit

Keep the matching and scoring rules in tested Python when the review queue needs
repeatable behavior. Keep notification delivery in low-code tools when
non-developers own channel routing or escalation rules.
