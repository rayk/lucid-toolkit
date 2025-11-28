# Pre-Response Protocol

MANDATORY: Execute this protocol BEFORE responding to ANY user request.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 0: TRANSITION CHECK (Do this FIRST)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Was your previous turn research (WebSearch, WebFetch, exploratory Read)?
Does the current request ask you to ACT on that research?

If YES to both → You are in a RESEARCH→ACTION TRANSITION.
This is the highest-risk moment for protocol violation.
Output this marker before proceeding:

[MODE: research → action]

Then continue to Step 1 with extra scrutiny.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 1: DECOMPOSE COMPOUND REQUESTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Does the request contain "AND", "then", or multiple action verbs?

If YES → Decompose before counting:
```
Request: "add X to evidence AND update the outcome"
├─ Add to evidence: Write (1 op)
├─ Update outcome: Read + Edit (track) + Edit (statement) = 3 ops
└─ Total: 4 ops
```

If NO → Proceed to Step 2.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 2: COUNT OPERATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tool calls needed to complete request: ___

Count rules:
- "Find where X is" = 1+ Grep/Glob + 1+ Read = 2+ minimum (often more)
- "Fix X" = Find + Read + Edit = 3+ minimum
- "Find and fix X" = Grep + Read (multiple?) + Edit = 3+ minimum
- Unknown locations = assume multiple reads needed
- File already in context = 0 ops to read it

THE UNCERTAINTY RULE: If you cannot state the count with certainty,
write "?" — and "?" ALWAYS means delegate.

IF count ≥ 3 → Delegate. Skip to Step 4.
IF count = "?" → Delegate. Skip to Step 4.
IF count < 3 AND certain → Continue to Step 3.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 3: VERIFY SIMPLICITY (Only if count < 3 with certainty)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALL must be true for direct execution:
☐ Single known file path (not "find where X is configured")
☐ Operation count certain, not estimated
☐ No exploration/search component
☐ Output size predictable and <500 tokens

If ANY checkbox is unclear → Delegate.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STEP 4: VISIBLE CHECKPOINT (Required before first tool — NON-NEGOTIABLE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before your FIRST tool call, output this line:

[N ops → direct|delegate]: rationale

Examples:
[2 ops → direct]: Known file path, single edit
[5 ops → delegate]: Multi-file outcome update
[? ops → delegate]: Unknown scope, need exploration

CHECKPOINT RULES:
- If N ≥ 3 but you wrote "direct" → STOP, you made an error
- If N = "?" but you wrote "direct" → STOP, you made an error
- Missing checkpoint before first tool = protocol violation
- Checkpoint creates COMMITMENT — you must follow what you wrote

SELF-AUDIT: If your first tool call is Grep/Glob for unknown location,
but your checkpoint said "direct" → you violated the protocol. Stop,
acknowledge, delegate remaining work.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
