---
description: Subscribe current project to an existing shared workspace
argument-hint: [workspace-id]
---

<objective>
Subscribe the current project to an existing shared workspace, enabling cross-project coordination and navigation.

This command:
- Connects current project to a workspace in the shared registry
- Registers this plugin instance as a subscriber
- Enables access to all workspace projects and settings
</objective>

<context>
Shared registry: @../../shared/workspaces/workspaces.json
Schema validation: @../../shared/workspaces/workspaces_schema.json
</context>

<process>
1. **Load Shared Registry**:
   - Read `shared/workspaces/workspaces.json`
   - If registry doesn't exist or is empty: Inform user no workspaces available
   - Parse available workspaces

2. **Identify Target Workspace**:
   - If $ARGUMENTS provided: Match against workspace IDs
   - If no match found: Suggest similar workspace names
   - If no $ARGUMENTS: Present interactive workspace selector showing:
     - Workspace name and description
     - Number of projects
     - Current subscriber count

3. **Check Existing Subscription**:
   - Generate instance ID for current project (hash of absolute path)
   - Check if already subscribed to target workspace
   - If already subscribed: Inform user and show current subscription details

4. **Validate Access**:
   - Check if workspace allows new subscribers
   - Verify current project path is valid
   - Determine appropriate access level (default: write)

5. **Create Subscription**:
   - Add subscriber entry to workspace:
     ```json
     {
       "instanceId": "[generated-id]",
       "projectPath": "[current-project-path]",
       "projectName": "[project-name]",
       "subscribedAt": "[ISO-datetime]",
       "lastAccess": "[ISO-datetime]",
       "accessLevel": "write"
     }
     ```
   - Update workspace's `updated` timestamp
   - Update registry's `metadata.updated` timestamp
   - Save to shared registry

6. **Display Confirmation**:
   ```
   Subscribed to: [workspace-name]

   Workspace Projects ([count]):
   - [project-1] ([type])
   - [project-2] ([type])

   Your access level: [access-level]

   Available commands:
   - workspace:list - View all workspace projects
   - workspace:switch [name] - Switch to a project
   - workspace:unsubscribe - Leave this workspace
   ```
</process>

<success_criteria>
- Shared registry loaded successfully
- Workspace found and selected
- No duplicate subscription created
- Subscriber entry added to workspace
- Registry updated and saved
- Confirmation displayed with workspace overview
</success_criteria>

<output_format>
## TOON Format (for machine consumption)

```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: workspace/{workspace-id}
name: subscribe
object: {workspace-name}
x-projects: {count}
x-accessLevel: {read|write|admin}
result: Subscribed to {workspace-name}

instanceId: {generated-id}
subscribedAt: {ISO-datetime}
filesUpdated[1]: workspaces.json
```

**Use TOON when:**
- Returning subscription results to subagents
- Automated workspace joining workflows
- Token efficiency is critical

**Use markdown when:**
- Final user-facing output with workspace overview
- Interactive subscription process
</output_format>

<output>
Updated file:
- `shared/workspaces/workspaces.json` - Updated with new subscriber

Displayed to user:
- Subscription confirmation
- Workspace project list
- Access level granted
- Available navigation commands
</output>

<verification>
Before completing, verify:
- [ ] Shared registry exists and is valid
- [ ] Target workspace identified
- [ ] Not already subscribed to this workspace
- [ ] Subscriber entry created with all required fields
- [ ] Instance ID is unique and deterministic
- [ ] Registry saved successfully
- [ ] Schema validation passes
</verification>
