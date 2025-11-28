# Specificity Trap

CRITICAL: Specific user input creates FALSE confidence.

When user input contains literal strings (error messages, paths, variable names):
- You know WHAT to search for
- You do NOT know WHERE it is or HOW MANY locations
- Specific problem ≠ simple solution
- This is EXPLORATION, not LOOKUP

## Examples of the Trap

- "I got error 'path /foo/bar not found'" → Still need to find which config references it
- "Fix the getUserById function" → Still need to find where it's defined
- "The luon path is wrong" → Still need to grep, read, understand, then fix

Count operations assuming multiple locations until proven otherwise.

## Exception

LOOKUP queries ("where is [named module/service]") should check index files
first—see critical rule 7. This trap applies to MUTATION operations (fix, update, change).
