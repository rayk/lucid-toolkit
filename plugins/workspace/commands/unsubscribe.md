---
description: Unsubscribe current project from a shared workspace
argument-hint: [workspace-id]
---

<objective>
Remove the current project's subscription from a shared workspace, disconnecting from cross-project coordination.

This command:
- Removes this plugin instance as a subscriber
- Preserves workspace and its projects (only removes subscription)
- Updates the shared registry
</objective>

<context>
Shared registry: @../../shared/workspaces/workspaces.json
Schema validation: @../../shared/workspaces/workspaces_schema.json
</context>

<process>
1. **Load Shared Registry**:
   - Read `shared/workspaces/workspaces.json`
   - If registry doesn't exist: Inform user no workspaces configured
   - Parse available workspaces

2. **Find Current Subscriptions**:
   - Generate instance ID for current project
   - Find all workspaces where current project is subscribed
   - If not subscribed to any: Inform user and exit

3. **Identify Target Workspace**:
   - If $ARGUMENTS provided: Match against workspace IDs
   - If no match found: Suggest similar workspace names
   - If no $ARGUMENTS and subscribed to multiple: Present selector
   - If no $ARGUMENTS and subscribed to one: Confirm that workspace

4. **Confirm Unsubscription**:
   - Display workspace name and project count
   - Ask for confirmation before proceeding
   - Warn if user is the only subscriber (workspace may become orphaned)

5. **Remove Subscription**:
   - Remove subscriber entry from workspace's subscribers array
   - Update workspace's `updated` timestamp
   - Update registry's `metadata.updated` timestamp
   - Save to shared registry

6. **Display Confirmation**:
   ```
   Unsubscribed from: [workspace-name]

   Remaining subscriptions: [count]
   - [workspace-1]
   - [workspace-2]

   To rejoin: workspace:subscribe [workspace-id]
   ```
</process>

<success_criteria>
- Current subscriptions identified
- Target workspace confirmed
- Subscriber entry removed from workspace
- Registry updated and saved
- Workspace preserved (not deleted)
- Confirmation displayed
</success_criteria>

<output_format>
## TOON Format (for machine consumption)

```toon
@type: Action
actionStatus: CompletedActionStatus
@id: workspace/{workspace-id}
name: unsubscribe
object: {workspace-name}
result: Unsubscribed from {workspace-name}

instanceId: {generated-id}
remainingSubscriptions[N]: {workspace-1},{workspace-2}
filesUpdated[1]: workspaces.json
x-workspacePreserved: true
```

**Use TOON when:**
- Returning unsubscription results to subagents
- Automated workspace leaving workflows
- Token efficiency is critical

**Use markdown when:**
- Final user-facing output with remaining subscriptions
- Interactive unsubscription confirmation
</output_format>

<output>
Updated file:
- `shared/workspaces/workspaces.json` - Updated with subscriber removed

Displayed to user:
- Unsubscription confirmation
- Remaining subscriptions (if any)
- Instructions to rejoin if needed
</output>

<verification>
Before completing, verify:
- [ ] Current project was subscribed to target workspace
- [ ] User confirmed unsubscription
- [ ] Subscriber entry removed from workspace
- [ ] Workspace itself NOT deleted (only subscription removed)
- [ ] Registry saved successfully
- [ ] Schema validation passes
</verification>
