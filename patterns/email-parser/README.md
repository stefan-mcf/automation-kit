# Pattern 2: Email Parser + AI

Classify incoming emails by intent using a deterministic keyword-based
classifier, then route each email to the appropriate queue:
`support`, `sales`, `billing`, `spam`, or `human_review`.

---

## How it works

1. **Email Trigger** polls an IMAP inbox (or reads from `input.json` in
   test/fixture mode).
2. **AI Classify** (DeterministicClassifier) scores the email subject + body
   against keyword lists for each intent category.
   - Each matching keyword adds to the category's score.
   - Confidence = `min(1.0, score × 0.35)`.
   - Emails with confidence below 0.6 (or zero matches) are routed to
     `human_review`.
   - Spam keywords always route to the `spam` queue, regardless of other
     matches.
3. **Route Switch** dispatches the email to the appropriate queue based on
   the `queue` field.
4. **Output** returns the classified email data in JSON format.

---

## Files

```
patterns/email-parser/
├── fixtures/
│   ├── input.json              # Sample emails (support, sales, billing, spam, low-conf)
│   └── expected_output.json    # Expected classification results
├── python/
│   ├── main.py                 # DeterministicClassifier + run() entry point
│   └── test_main.py            # Unit tests + integration test
├── workflow.json               # n8n-compatible workflow definition
└── README.md                   # This file
```

---

## Running

```bash
# Activate venv
source .venv/bin/activate

# Run the pattern's tests
python -m pytest patterns/email-parser/python/test_main.py -v

# Run the pattern directly
python -c "
from patterns.email_parser.python.main import run
import json
result = run()
print(json.dumps(result, indent=2))
"
```

---

## Pitfalls & production considerations

### Hallucination guardrails (for LLM-based variants)

If you swap the deterministic classifier for an LLM call, be aware:

- LLMs may invent intents not in the defined list. Always constrain the
  output with a strict system prompt and parse via structured output
  (JSON mode / tool calls).
- Re-prompt or fall back to `human_review` if the LLM response does not
  contain a valid intent field.
- Rate-limit the LLM to avoid runaway costs during email bursts.

### Confidence thresholds

- The 0.6 threshold is a reasonable starting point. Tune it against your
  historical email data using precision/recall on the `human_review` queue.
- A higher threshold (e.g., 0.8) reduces false positives but increases
  manual review volume.
- A lower threshold (e.g., 0.4) automates more emails but risks
  misclassification.

### Human review workflow

- `human_review` emails should be surfaced in a shared queue (e.g., Slack
  channel, HelpScout, Zendesk) for manual triage.
- Track review-to-resolution time as a key metric. If too many emails land
  in `human_review`, adjust thresholds or expand keyword coverage.
- Consider a feedback loop: manually-corrected classifications can be used
  to retrain or expand the keyword lists (or fine-tune an embedding model).

### Keyword coverage

- The current keyword lists are minimal. In production, expand them by
  analyzing real email traffic for the first few weeks.
- Watch out for false positives: e.g., "I need help with pricing" contains
  both `help` (support) and `pricing` (sales). The classifier picks the
  highest-scoring category, which may not always be correct. The
  `human_review` fallback catches edge cases.

### Spam detection

- Simple keyword matching is easily bypassed by sophisticated spam. For
  production, layer in domain reputation checks, SPF/DKIM validation, and
  optionally an ML-based spam filter (e.g., SpamAssassin integration) before
  the intent classifier.
- Never delete spam automatically; file it in a quarantine folder for
  periodic review.

### Performance

- Classifying 50 emails with the deterministic classifier takes < 10 ms.
- For LLM-based variants, batch emails or use async I/O to keep up with
  inbound volume.
- The pattern is designed to be idempotent: re-running on the same input
  produces identical output.
