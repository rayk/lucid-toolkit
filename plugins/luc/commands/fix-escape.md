---
description: Diagnose and fix IdeaVim escape key conflicts with Claude Code CLI in IntelliJ terminal
allowed-tools: [Read, Edit, Write, Bash, AskUserQuestion]
---

<objective>
Diagnose and fix the common escape key conflict when running Claude Code CLI in IntelliJ IDEA's terminal with IdeaVim enabled on macOS.

The escape key has five competing handlers that can intercept it before reaching Claude Code:
1. IdeaVim `sethandler` directive
2. GitHub Copilot "Hide Completions" binding
3. IntelliJ "Focus Editor" action
4. IntelliJ Reworked Terminal (2025)
5. vim_settings.xml state reset

This command checks each potential cause and applies fixes where possible.
</objective>

<context>
## Current State

**IdeaVim config:**
!`cat ~/.ideavimrc 2>/dev/null | grep -A5 -B2 "sethandler.*Esc\|sethandler.*C-\[" || echo "No sethandler directives found"`

**vim_settings.xml enabled state:**
!`find ~/Library/Application\ Support/JetBrains/*/options/vim_settings.xml -exec grep -l 'enabled=' {} \; -exec grep 'enabled=' {} \; 2>/dev/null | head -10 || echo "No vim_settings.xml found"`

**JetBrains IDE versions:**
!`ls -d ~/Library/Application\ Support/JetBrains/*Idea* 2>/dev/null | head -5 || echo "No IntelliJ IDEA found"`
</context>

<process>
## Step 1: Analyze Current Configuration

Check ~/.ideavimrc for the escape key sethandler directive:
- **Problem pattern**: `sethandler <Esc> a:ide` or missing directive
- **Fixed pattern**: `sethandler <Esc> n:vim v:vim i:vim`

The fix limits IdeaVim's ESC handling to editor modes only, allowing terminal to receive ESC directly.

## Step 2: Check vim_settings.xml State

Scan all JetBrains IDE vim_settings.xml files for `enabled="false"`:
- This state persists when IdeaVim is toggled off/on
- Fix by changing to `enabled="true"`

## Step 3: Apply Fixes

**For ~/.ideavimrc:**
If sethandler is misconfigured, update to:
```vim
" ESCAPE KEY HANDLING FOR CLAUDE CODE COMPATIBILITY
" Only handle ESC in vim editing modes - terminal gets ESC directly
sethandler <Esc> n:vim v:vim i:vim

" CRITICAL: These must always reach terminal/Claude Code
sethandler <C-[> a:ide
sethandler <C-c> a:ide
```

**For vim_settings.xml:**
Replace `enabled="false"` with `enabled="true"` in all JetBrains IDE settings.

## Step 4: Report Manual Steps

Some fixes require manual action in IntelliJ:

1. **GitHub Copilot binding** (Settings > Keymap > Plugins > GitHub Copilot > Hide Completions):
   - Remove: `Escape`
   - Add: `Cmd+Escape` or `Cmd+.`

2. **Focus Editor binding** (Settings > Keymap > Other > Focus Editor):
   - Remove the ESC binding or add terminal exclusion

3. **Restart IntelliJ** after changes

## Step 5: Provide Fallback

If ESC continues to have issues, inform user about `Ctrl+[`:
- Equivalent to ESC in terminal applications
- Bypasses IdeaVim entirely via `sethandler <C-[> a:ide`
</process>

<verification>
After applying fixes:
1. Check ~/.ideavimrc contains correct sethandler directives
2. Verify no vim_settings.xml files have enabled="false"
3. List any remaining manual steps for user
</verification>

<success_criteria>
**Automated fixes applied:**
- ~/.ideavimrc has correct sethandler for ESC, C-[, and C-c
- All vim_settings.xml files have enabled="true"

**User informed of:**
- What was changed automatically
- What manual steps remain (Copilot, Focus Editor bindings)
- Fallback option (Ctrl+[) if issues persist
- Need to restart IntelliJ IDEA

**Output format:**
Clear summary with:
- Diagnosis results (what conflicts were found)
- Fixes applied (what was changed)
- Manual steps (numbered list for user action)
- Verification checklist
</success_criteria>

<output>
Files potentially modified:
- `~/.ideavimrc` - Updated sethandler directives
- `~/Library/Application Support/JetBrains/*/options/vim_settings.xml` - Fixed enabled state
</output>

<reference>
For full documentation of the problem and solution, see:
- Root cause analysis of five competing ESC handlers
- Detailed keymap action IDs (EditorEscape, Terminal.SwitchFocusToEditor, copilot.nes.escape)
- Related issues: Claude Code #39, JetBrains VIM-3543
</reference>
