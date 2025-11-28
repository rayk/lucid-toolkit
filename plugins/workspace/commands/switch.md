---
description: Switch context to a specific project within the workspace
argument-hint: [project-name]
---

<objective>
Switch the working context to a specific project within the workspace for focused development.

This command:
- Changes working directory to the project
- Loads project-specific configurations
- Updates context for subsequent commands
- Displays project overview
</objective>

<context>
Workspace file: @workspace.json
</context>

<process>
1. **Load Workspace Configuration**:
   - Find `workspace.json` in current directory or parent directories
   - If not found: Inform user no workspace is configured
   - Parse workspace configuration

2. **Identify Target Project**:
   - If $ARGUMENTS provided: Match against project names (fuzzy match supported)
   - If no match found: Suggest similar project names
   - If no $ARGUMENTS: Present interactive project selector
   - Confirm project selection

3. **Validate Project Path**:
   - Check if project directory exists
   - If missing: Offer to remove from workspace or clone if URL available
   - Verify project is accessible

4. **Switch Context**:
   - Change working directory to project path
   - Inform user of directory change
   - Load project-specific CLAUDE.md if present

5. **Display Project Overview**:
   ```
   Switched to: [project-name]
   Path: [absolute-path]
   Type: [project-type] | Role: [role]

   Dependencies: [list or "none"]
   Dependents: [list or "none"]

   Quick commands:
   - workspace:list - View all workspace projects
   - workspace:switch [name] - Switch to another project
   ```

6. **Update Session Context**:
   - Note the current project in session for reference
   - Enable project-relative path resolution
</process>

<success_criteria>
- Target project identified correctly
- Working directory changed to project path
- Project overview displayed
- Project-specific configs loaded if present
- User can navigate to other projects easily
</success_criteria>

<output>
Displayed to user:
- Confirmation of project switch
- Project path and metadata
- Related projects (dependencies/dependents)
- Available navigation commands
</output>

<verification>
Before completing, verify:
- [ ] Project exists in workspace
- [ ] Project path is accessible
- [ ] Directory change executed
- [ ] Project overview displayed
- [ ] Context updated for subsequent commands
</verification>
