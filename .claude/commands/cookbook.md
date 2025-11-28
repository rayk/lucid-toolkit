---
description: Look up examples from Claude Cookbooks for implementation patterns
arguments:
  - name: topic
    description: What to look up (e.g., "tool use", "skills", "agents", "multimodal")
    required: true
allowed_tools: WebFetch, Read, Grep, Glob
---

<task>
Look up examples and implementation patterns from the official Anthropic Claude Cookbooks repository for: **$ARGUMENTS.topic**
</task>

<instructions>
1. **Identify the category** based on the topic:
   - "tool", "tools", "function calling" → tool_use/
   - "skill", "skills", "command" → skills/
   - "agent", "agents", "multi-agent" → agents/
   - "image", "vision", "pdf", "multimodal" → multimodal/
   - "prompt", "prompting", "system prompt" → prompt_engineering/
   - "bedrock", "vertex", "aws", "gcp" → third_party/

2. **Fetch the category listing**:
   ```
   WebFetch: https://github.com/anthropics/claude-cookbooks/tree/main/{category}
   ```

3. **List available examples** and identify the most relevant ones

4. **Fetch specific example(s)** using raw URLs:
   ```
   WebFetch: https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/{path}
   ```

5. **Present findings**:
   - What examples are available
   - Key implementation patterns from the most relevant example
   - How to apply these patterns
</instructions>

<output_format>
## Available Examples
[List of relevant notebooks/files found]

## Key Patterns from [Most Relevant Example]
[Code snippets and explanations]

## How to Apply
[Guidance on adapting for user's needs]
</output_format>
