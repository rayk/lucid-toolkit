<overview>
Best practices for handling API credentials and sensitive data in skills.
</overview>

<core_problem>
**Raw curl commands with environment variables expose credentials** when Claude executes them, making API keys visible in chat conversations.

Skills that interact with external APIs need credentials, but:
1. **Credentials in chat = security breach**: API keys exposed in conversation history
2. **Hardcoded credentials = version control leak**: Secrets committed to git
3. **User prompts for keys = poor UX**: Interrupts workflow, keys visible in chat
4. **Environment vars in commands = exposure**: `curl -H "Authorization: Bearer $API_KEY"` exposes the key
</core_problem>

<secure_api_wrapper_solution>
<primary_solution>
**Use `~/.claude/scripts/secure-api.sh`**

This wrapper script loads credentials internally rather than exposing them in commands.

**DO NOT:**
- Use raw curl commands with `$API_KEY` environment variables
- Include API keys directly in skills or chat
- Ask user to paste API keys in chat
- Store credentials in skill files

**DO:**
- Use `~/.claude/scripts/secure-api.sh` as a wrapper
- Store credentials in `~/.claude/.env`
- Reference credentials internally within the wrapper
- Validate credential availability before operations
</primary_solution>

<implementation_steps_for_new_services>
<step_1_add_operations>
**Add operations to secure-api.sh wrapper**

Implement service cases with curl calls that reference environment variables internally:

```bash
# Inside ~/.claude/scripts/secure-api.sh

case "$service" in
  "stripe")
    case "$operation" in
      "get-customer")
        customer_id="$1"
        curl -s "https://api.stripe.com/v1/customers/$customer_id" \
          -H "Authorization: Bearer $STRIPE_API_KEY"
        ;;
      "create-subscription")
        # Read JSON from stdin for POST
        curl -s -X POST "https://api.stripe.com/v1/subscriptions" \
          -H "Authorization: Bearer $STRIPE_API_KEY" \
          -H "Content-Type: application/json" \
          -d @-
        ;;
    esac
    ;;
esac
```
</step_1_add_operations>

<step_2_enable_profile_support>
Add profile remapping logic for multiple accounts:

```bash
# Profile naming convention: SERVICENAME_PROFILENAME_APIKEY

if [ -n "$profile" ]; then
  # Remap environment variables for selected profile
  eval "STRIPE_API_KEY=\$STRIPE_${profile}_API_KEY"
fi
```
</step_2_enable_profile_support>

<step_3_create_credential_placeholders>
Create credential placeholders in ~/.claude/.env:

```bash
# ~/.claude/.env

# Stripe credentials
STRIPE_MAIN_API_KEY=
STRIPE_TEST_API_KEY=

# Add entries so users know what to configure
```
</step_3_create_credential_placeholders>

<step_4_document_workflow>
Document workflow in SKILL.md:

```xml
<api_workflow>
<check_profiles>
Check if user has saved a profile preference:

```bash
profile-state get stripe-profile
```

If profile is set, use it. Otherwise, discover available profiles.
</check_profiles>

<discover_profiles>
List available Stripe profiles:

```bash
list-profiles stripe
```

Output example:
```
Available Stripe profiles:
- main
- test
```

If multiple profiles exist, prompt user to select one.
</discover_profiles>

<save_selection>
After user selects profile, save it:

```bash
profile-state set stripe-profile main
```

This persists the selection for future operations.
</save_selection>

<make_api_call>
Always announce which profile before API calls:

```
Using Stripe profile: main
```

Then execute operation via secure wrapper:

```bash
~/.claude/scripts/secure-api.sh stripe get-customer cus_123
```
</make_api_call>
</api_workflow>
```
</step_4_document_workflow>

<step_5_common_api_patterns>
**Simple GET request:**
```bash
# Inside secure-api.sh
"get-resource")
  resource_id="$1"
  curl -s "https://api.service.com/v1/resources/$resource_id" \
    -H "Authorization: Bearer $SERVICE_API_KEY"
  ;;
```

**POST with JSON body (accepts piped input):**
```bash
"create-resource")
  curl -s -X POST "https://api.service.com/v1/resources" \
    -H "Authorization: Bearer $SERVICE_API_KEY" \
    -H "Content-Type: application/json" \
    -d @-  # Read from stdin
  ;;
```

**Form data submission:**
```bash
"upload-file")
  file_path="$1"
  curl -s -X POST "https://api.service.com/v1/upload" \
    -H "Authorization: Bearer $SERVICE_API_KEY" \
    -F "file=@$file_path"
  ;;
```
</step_5_common_api_patterns>
</implementation_steps_for_new_services>
</secure_api_wrapper_solution>

<key_security_patterns>
<never_demonstrate_raw_credentials>
❌ **WRONG - exposes credentials:**
```xml
<examples>
Call the API with your key:

```bash
curl -H "Authorization: Bearer $STRIPE_API_KEY" https://api.stripe.com/v1/customers
```
</examples>
```

✅ **RIGHT - uses secure wrapper:**
```xml
<examples>
Get customer information:

```bash
~/.claude/scripts/secure-api.sh stripe get-customer cus_123
```

Credentials loaded internally from ~/.claude/.env
</examples>
```
</never_demonstrate_raw_credentials>

<auto_generate_credential_placeholders>
When adding a new service, immediately create placeholder in `~/.claude/.env`:

```bash
# ServiceName credentials
SERVICENAME_MAIN_API_KEY=
SERVICENAME_MAIN_API_SECRET=
```

This documents what needs to be configured without committing actual keys.
</auto_generate_credential_placeholders>

<centralized_credential_storage>
**One credential file** (`~/.claude/.env`), not scattered across:
- ❌ Multiple `.env` files
- ❌ Individual skill directories
- ❌ Script files
- ❌ Configuration files

**Rationale:** Single source of truth, easier to audit, consistent permissions.
</centralized_credential_storage>

<document_each_operation>
For each API operation in the wrapper, document:

**Operation purpose:**
```bash
# get-customer: Retrieve customer details by ID
# Args: customer_id
# Returns: JSON customer object
"get-customer")
  customer_id="$1"
  curl -s "https://api.stripe.com/v1/customers/$customer_id" \
    -H "Authorization: Bearer $STRIPE_API_KEY"
  ;;
```
</document_each_operation>
</key_security_patterns>

<environment_variable_pattern>
<description>
Alternative approach using environment variables.
</description>

<step_1_set_environment_variables>
```bash
# ~/.bashrc or ~/.zshrc
export STRIPE_API_KEY="sk_live_..."
export OPENAI_API_KEY="sk-..."
```
</step_1_set_environment_variables>

<step_2_access_in_scripts>
```python
import os

api_key = os.environ.get("STRIPE_API_KEY")
if not api_key:
    print("ERROR: STRIPE_API_KEY environment variable not set")
    print("Add to ~/.bashrc: export STRIPE_API_KEY='sk_live_...'")
    exit(1)

# Use api_key without printing
```
</step_2_access_in_scripts>

<step_3_skill_documents_requirement>
```xml
<prerequisites>
<environment_setup>
Set environment variable before using this skill:

```bash
export STRIPE_API_KEY="sk_live_YOUR_KEY_HERE"
```

Verify:
```bash
echo $STRIPE_API_KEY
```

**Security note**: Never commit .bashrc/.zshrc with actual keys. Use placeholders in docs.
</environment_setup>
</prerequisites>
```
</step_3_skill_documents_requirement>
</environment_variable_pattern>

<api_key_validation>
Always validate credentials before attempting operations.

**Good validation pattern:**

```python
def validate_stripe_credentials():
    """Validate Stripe API key without exposing it."""
    api_key = get_credential("stripe", "api_key")

    if not api_key:
        return False, "Stripe API key not configured"

    if not api_key.startswith("sk_"):
        return False, "Invalid Stripe API key format (must start with 'sk_')"

    # Test key with minimal API call
    try:
        import stripe
        stripe.api_key = api_key
        stripe.Account.retrieve()  # Lightweight validation
        return True, "Credentials valid"
    except stripe.error.AuthenticationError:
        return False, "Invalid Stripe API key (authentication failed)"
    except Exception as e:
        return False, f"Credential validation error: {type(e).__name__}"

# In skill workflow
valid, message = validate_stripe_credentials()
if not valid:
    print(f"ERROR: {message}")
    exit(1)
```

**Benefits:**
- Fails fast if credentials missing/invalid
- Clear error messages for user
- No credential values in output
</api_key_validation>

<multi_service_credentials>
<description>
For skills using multiple APIs.
</description>

<credential_file_structure>
```json
{
  "stripe_api_key": "sk_live_...",
  "stripe_webhook_secret": "whsec_...",
  "openai_api_key": "sk-...",
  "github_token": "ghp_...",
  "sendgrid_api_key": "SG_..."
}
```
</credential_file_structure>

<helper_function>
```python
def get_all_credentials(*required_keys):
    """
    Get multiple credentials at once.

    Args:
        *required_keys: Tuples of (service, key_name)

    Returns:
        dict of credentials or None if any missing
    """
    creds = {}
    missing = []

    for service, key_name in required_keys:
        cred = get_credential(service, key_name)
        if not cred:
            missing.append(f"{service}_{key_name}")
        else:
            creds[f"{service}_{key_name}"] = cred

    if missing:
        print(f"ERROR: Missing credentials: {', '.join(missing)}")
        return None

    return creds

# Usage
creds = get_all_credentials(
    ("stripe", "api_key"),
    ("stripe", "webhook_secret"),
    ("sendgrid", "api_key")
)

if not creds:
    exit(1)

stripe_key = creds["stripe_api_key"]
webhook_secret = creds["stripe_webhook_secret"]
sendgrid_key = creds["sendgrid_api_key"]
```
</helper_function>
</multi_service_credentials>

<preventing_credential_leaks>
<ask_user_question_tool_safety>
**❌ WRONG - credential in chat:**

```xml
<workflow>
1. Use AskUserQuestion to ask user for API key
2. Use the provided key for operations
</workflow>
```

**Problem:** API key appears in conversation history (security breach).

**✅ RIGHT - credential not in chat:**

```xml
<workflow>
1. Check if credentials configured using `verify_credentials.py`
2. If not configured, provide setup instructions
3. User sets up credentials outside of chat
4. Verify and proceed with operations
</workflow>
```
</ask_user_question_tool_safety>

<log_safety>
**❌ WRONG - credential in logs:**

```python
print(f"Connecting to Stripe with key: {api_key}")
```

**✅ RIGHT - no credential in logs:**

```python
print("Connecting to Stripe with configured credentials")
```
</log_safety>

<error_message_safety>
**❌ WRONG - credential in error:**

```python
raise Exception(f"Authentication failed for key {api_key}")
```

**✅ RIGHT - no credential in error:**

```python
raise Exception("Authentication failed (check API key configuration)")
```
</error_message_safety>
</preventing_credential_leaks>

<setup_instructions_for_users>
<first_time_credential_setup>
**What to include in skill:**

```xml
<first_time_setup>
**One-time credential configuration:**

1. **Create secure credentials directory:**
   ```bash
   mkdir -p ~/.config/claude
   chmod 700 ~/.config/claude
   ```

2. **Create credentials file:**
   ```bash
   touch ~/.config/claude/api-credentials.json
   chmod 600 ~/.config/claude/api-credentials.json
   ```

3. **Add your ServiceName API key:**

   Edit `~/.config/claude/api-credentials.json`:
   ```json
   {
     "servicename_api_key": "YOUR_ACTUAL_KEY_HERE"
   }
   ```

4. **Verify setup:**
   ```bash
   python scripts/verify_credentials.py servicename
   ```

   Expected output: "✓ ServiceName credentials configured correctly"

**Important:**
- Replace `YOUR_ACTUAL_KEY_HERE` with your actual API key
- Never commit this file to version control
- File permissions (600) ensure only you can read it
- Credentials never appear in Claude Code chat

**Where to get API keys:**
- ServiceName Dashboard → API Keys → Create new key
- Copy the key starting with `sk_...`
</first_time_setup>
```
</first_time_credential_setup>

<verification_script>
**Include in `scripts/verify_credentials.py`:**

```python
#!/usr/bin/env python3
"""Verify API credentials are configured correctly."""

import sys
from get_credential import get_credential

def verify_service(service_name, key_name="api_key"):
    """Verify service credentials without exposing them."""
    key = get_credential(service_name, key_name)

    if not key:
        print(f"✗ {service_name} {key_name} not configured")
        print(f"  Add to ~/.config/claude/api-credentials.json:")
        print(f'  "{service_name}_{key_name}": "YOUR_KEY_HERE"')
        return False

    # Show only first 7 chars for verification
    masked = key[:7] + "..." if len(key) > 10 else "***"
    print(f"✓ {service_name} {key_name} configured ({masked})")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_credentials.py <service_name>")
        sys.exit(1)

    service = sys.argv[1]
    success = verify_service(service)
    sys.exit(0 if success else 1)
```
</verification_script>
</setup_instructions_for_users>

<git_ignore_pattern>
**Always add to `.gitignore`:**

```gitignore
# API credentials
.config/claude/api-credentials.json
**/api-credentials.json
**/*credentials.json
.env
.env.local

# Environment files with secrets
*.secret
*.key
```
</git_ignore_pattern>

<security_checklist>
Before finalizing an API integration skill:

- [ ] **No hardcoded credentials**: Search for `api_key`, `secret`, `token` in skill files
- [ ] **Credential helper used**: Scripts use `get_credential()` or env vars
- [ ] **Validation before operations**: Check credentials exist and valid format
- [ ] **No credentials in output**: Print statements don't include credential values
- [ ] **No credentials in errors**: Exception messages don't expose keys
- [ ] **Setup instructions clear**: User knows how to configure credentials securely
- [ ] **Verification script provided**: User can test setup without using skill
- [ ] **Gitignore configured**: Credentials files excluded from version control
- [ ] **File permissions documented**: Instructions include `chmod 600` for cred files
</security_checklist>

<example_complete_secure_api_skill>
See the example skill showing all security patterns:

```
skills/manage-stripe/
├── SKILL.md (references credential setup)
├── scripts/
│   ├── get_credential.py (secure credential retrieval)
│   ├── verify_credentials.py (test setup without exposing)
│   ├── stripe_create_subscription.py (uses get_credential)
│   ├── stripe_get_subscription.py (uses get_credential)
│   └── stripe_cancel_subscription.py (uses get_credential)
└── references/
    ├── api-reference.md (API docs, no credentials)
    └── security.md (this document)
```

**Key principle:** Credentials configured once by user, stored securely outside version control, accessed by name (not value) in skills, never exposed in chat or logs.
</example_complete_secure_api_skill>
