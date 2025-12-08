# Runtime Debugging with MCP Tools

Advanced patterns for debugging running Flutter applications.

## Prerequisites

The Flutter app must be running in debug mode with the Dart tooling daemon connected:

```bash
# Start app in debug mode
flutter run --debug

# The daemon URI appears in output:
# Dart VM Service Protocol available at ws://127.0.0.1:12345/abcdef=/ws
```

## Connection Verification

Before any debugging, verify the app is connected:

```
get_runtime_errors
```

- If returns results (or empty): Connected
- If fails with error: App not running or daemon not connected

## Error Classification

### Layout Errors

**RenderFlex Overflow:**
```
A RenderFlex overflowed by 42 pixels on the right.
```

Diagnosis via `get_widget_tree`:
- Look for Row/Column without Expanded/Flexible
- Check for unbounded constraints

Fix patterns:
- Wrap child in `Expanded` or `Flexible`
- Add `SingleChildScrollView` for scrollable content
- Use `ConstrainedBox` for explicit limits

**RenderBox Not Laid Out:**
```
RenderBox was not laid out: RenderFlex#abc12 NEEDS-PAINT
```

Usually means widget accessed before layout complete.

### State Errors

**setState After Dispose:**
```
setState() called after dispose()
```

Diagnosis:
- Async operation completing after widget unmounted
- Missing `if (mounted)` check

Fix pattern:
```dart
if (mounted) {
  setState(() { ... });
}
```

### Null Safety Errors

**Null Check Operator:**
```
Null check operator used on a null value
```

Diagnosis via `get_runtime_errors`:
- Stack trace shows file:line
- Check for `!` operator usage

Fix:
- Use null-aware operators (`?.`, `??`)
- Add explicit null checks
- Use `Option<T>` from fpdart for domain logic

## Widget Tree Analysis

When `get_widget_tree` returns:

```
MaterialApp
  └─ Scaffold
      └─ Column
          └─ Row
              └─ Text("Hello")
              └─ Icon(...)
```

Look for:
- **Unexpected nesting**: Extra widgets from bad composition
- **Missing constraints**: Row/Column without bounded children
- **Key issues**: Duplicate or missing keys in lists

## Hot Reload Strategy

### When to Use hot_reload

- Method body changes
- Build method changes
- Adding/removing widgets
- Changing widget properties

### When to Use hot_restart

- Static field changes
- Class structure changes
- Main function changes
- Adding new dependencies
- When hot_reload fails

### Debugging Hot Reload Failures

If `hot_reload` fails:

1. Run `dart_analyzer`:
   - Syntax errors prevent reload
   - Type errors prevent reload

2. Check for structural changes:
   - Did you change static initializers?
   - Did you modify the main function?
   - Did you add new imports?

3. If analyzer passes but reload fails:
   - Try `hot_restart`
   - If still fails, full app restart needed

## Systematic Debugging Protocol

```
1. GATHER
   get_runtime_errors → capture current state
   get_widget_tree → understand structure

2. ANALYZE
   - Identify error type from message
   - Locate source from stack trace
   - Check widget tree for context

3. HYPOTHESIZE
   - Form theory about root cause
   - Plan minimal fix

4. FIX
   - Make targeted change
   - Use mcp__ide__writeFile

5. VERIFY
   hot_reload → apply change
   get_runtime_errors → should be resolved

6. REPEAT if needed
   - If new errors, return to step 1
   - If same error, theory was wrong
```

## Common Debugging Patterns

### Pattern: Isolate the Problem

When error is unclear:

1. `get_widget_tree` to find error location
2. Simplify affected widget (remove children)
3. `hot_reload` and check if error persists
4. Add back children one by one
5. When error returns, you found the culprit

### Pattern: State Inspection

When state seems wrong:

1. Add temporary debug print in build method
2. `hot_reload` to apply
3. Trigger the action
4. Check console output
5. Remove debug print when done

### Pattern: Constraint Debugging

For layout issues:

1. Wrap problematic widget in `Container(color: Colors.red)`
2. `hot_reload` to see bounds
3. Check if constraints match expectations
4. Add `LayoutBuilder` to log constraints
