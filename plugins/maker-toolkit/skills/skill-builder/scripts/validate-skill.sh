#!/usr/bin/env bash
#
# Skill Validation Script
# Validates a Claude Code skill structure against requirements
#
# Usage: ./validate-skill.sh <skill-path>
# Example: ./validate-skill.sh /path/to/.claude/skills/my-skill

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Status symbols
PASS="${GREEN}✅${NC}"
FAIL="${RED}❌${NC}"
WARN="${YELLOW}⚠️ ${NC}"

# Validation counters
ERRORS=0
WARNINGS=0
PASSES=0

# Get skill path from argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <skill-path>"
    echo "Example: $0 ~/.claude/skills/my-skill"
    exit 1
fi

SKILL_PATH="$1"
SKILL_NAME=$(basename "$SKILL_PATH")
SKILL_FILE="$SKILL_PATH/SKILL.md"

# Header
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Skill Validation Report: $SKILL_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

#
# 1. File Structure Checks
#
echo "1. File Structure:"

if [ -f "$SKILL_FILE" ]; then
    echo -e "  $PASS SKILL.md exists"
    ((PASSES++))
else
    echo -e "  $FAIL SKILL.md missing"
    ((ERRORS++))
    exit 1
fi

# Check directory name matches YAML name
YAML_NAME=$(head -20 "$SKILL_FILE" | grep "^name:" | cut -d: -f2 | tr -d ' ' || echo "")
if [ "$YAML_NAME" = "$SKILL_NAME" ]; then
    echo -e "  $PASS Name matches directory: $SKILL_NAME"
    ((PASSES++))
else
    echo -e "  $WARN Name mismatch: directory='$SKILL_NAME' yaml='$YAML_NAME'"
    ((WARNINGS++))
fi

#
# 2. YAML Frontmatter Validation
#
echo ""
echo "2. YAML Frontmatter:"

# Extract and validate YAML using Python (if pyyaml available)
YAML_RESULT=""
if python3 -c "import yaml" 2>/dev/null; then
    YAML_RESULT=$(head -20 "$SKILL_FILE" | python3 -c "
import yaml, sys
errors = []
warnings = []
passes = []

try:
    doc = yaml.safe_load(sys.stdin)
    passes.append('YAML syntax valid')

    # Check name field
    if 'name' in doc:
        passes.append(f'Name field present: {doc[\"name\"]}')
        if len(doc['name']) <= 64:
            passes.append(f'Name length OK: {len(doc[\"name\"])} chars')
        else:
            warnings.append(f'Name too long: {len(doc[\"name\"])} chars (max 64)')
    else:
        errors.append('Name field missing')

    # Check description field
    if 'description' in doc:
        desc_len = len(doc['description'])
        passes.append(f'Description field present: {desc_len} chars')
        if desc_len <= 1024:
            passes.append('Description length OK')
        else:
            warnings.append(f'Description too long: {desc_len} chars (max 1024)')
    else:
        errors.append('Description field missing')

except yaml.YAMLError as e:
    errors.append(f'YAML parse error: {e}')

# Output results
print('PASSES:' + '|'.join(passes))
print('WARNINGS:' + '|'.join(warnings))
print('ERRORS:' + '|'.join(errors))
" 2>&1)
else
    # Fallback: basic YAML checks without python yaml module
    echo -e "  $WARN Python yaml module not available, using basic checks"
    ((WARNINGS++))

    # Check name field exists
    if grep -q "^name:" "$SKILL_FILE"; then
        YAML_NAME_VALUE=$(head -20 "$SKILL_FILE" | grep "^name:" | cut -d: -f2- | tr -d ' ')
        echo -e "  $PASS Name field present: $YAML_NAME_VALUE"
        ((PASSES++))
    else
        echo -e "  $FAIL Name field missing"
        ((ERRORS++))
    fi

    # Check description field exists
    if grep -q "^description:" "$SKILL_FILE"; then
        echo -e "  $PASS Description field present"
        ((PASSES++))
    else
        echo -e "  $FAIL Description field missing"
        ((ERRORS++))
    fi

    YAML_PASSES=""
    YAML_WARNINGS=""
    YAML_ERRORS=""
fi

if [ -n "$YAML_RESULT" ]; then
    # Parse Python output
    YAML_PASSES=$(echo "$YAML_RESULT" | grep "^PASSES:" | cut -d: -f2 | tr '|' '\n')
    YAML_WARNINGS=$(echo "$YAML_RESULT" | grep "^WARNINGS:" | cut -d: -f2 | tr '|' '\n')
    YAML_ERRORS=$(echo "$YAML_RESULT" | grep "^ERRORS:" | cut -d: -f2 | tr '|' '\n')

    while IFS= read -r line; do
        [ -z "$line" ] && continue
        echo -e "  $PASS $line"
        ((PASSES++))
    done <<< "$YAML_PASSES"

    while IFS= read -r line; do
        [ -z "$line" ] && continue
        echo -e "  $WARN $line"
        ((WARNINGS++))
    done <<< "$YAML_WARNINGS"

    while IFS= read -r line; do
        [ -z "$line" ] && continue
        echo -e "  $FAIL $line"
        ((ERRORS++))
    done <<< "$YAML_ERRORS"
fi

#
# 3. Line Count Check
#
echo ""
echo "3. Line Count:"

LINE_COUNT=$(wc -l < "$SKILL_FILE")
REMAINING=$((500 - LINE_COUNT))

if [ $LINE_COUNT -lt 500 ]; then
    PERCENT=$((LINE_COUNT * 100 / 500))
    echo -e "  $PASS Line count: $LINE_COUNT / 500 limit (${PERCENT}%, $REMAINING remaining)"
    ((PASSES++))
else
    OVER=$((LINE_COUNT - 500))
    echo -e "  $WARN Line count exceeds limit: $LINE_COUNT / 500 ($OVER over)"
    ((WARNINGS++))
fi

#
# 4. XML Structure Checks
#
echo ""
echo "4. XML Structure:"

# Check for markdown headings
if grep -q '^#' "$SKILL_FILE" 2>/dev/null; then
    HEADING_COUNT=$(grep -c '^#' "$SKILL_FILE")
else
    HEADING_COUNT=0
fi

if [ "$HEADING_COUNT" -eq 0 ]; then
    echo -e "  $PASS No markdown headings found"
    ((PASSES++))
else
    echo -e "  $WARN Found $HEADING_COUNT markdown headings (should use XML tags)"
    ((WARNINGS++))
    grep -n '^#' "$SKILL_FILE" | head -5 | while read line; do
        echo -e "       Line: $line"
    done
fi

# Check required tags
for TAG in "objective" "quick_start" "success_criteria"; do
    if grep -q "<$TAG>" "$SKILL_FILE"; then
        echo -e "  $PASS Required tag <$TAG> present"
        ((PASSES++))
    else
        if [ "$TAG" = "success_criteria" ]; then
            if grep -q "<when_successful>" "$SKILL_FILE"; then
                echo -e "  $PASS Alternative tag <when_successful> present"
                ((PASSES++))
            else
                echo -e "  $FAIL Missing required tag: <$TAG> or <when_successful>"
                ((ERRORS++))
            fi
        else
            echo -e "  $FAIL Missing required tag: <$TAG>"
            ((ERRORS++))
        fi
    fi
done

#
# 5. Progressive Disclosure Check
#
echo ""
echo "5. Progressive Disclosure:"

if [ "$LINE_COUNT" -gt 300 ]; then
    if [ -d "$SKILL_PATH/references" ]; then
        REF_COUNT=$(find "$SKILL_PATH/references" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$REF_COUNT" -gt 0 ]; then
            echo -e "  $PASS Progressive disclosure: $REF_COUNT reference files"
            ((PASSES++))
        else
            echo -e "  $WARN SKILL.md is $LINE_COUNT lines but references/ is empty"
            ((WARNINGS++))
        fi
    else
        echo -e "  $WARN SKILL.md is $LINE_COUNT lines but no references/ directory"
        ((WARNINGS++))
    fi
else
    echo -e "  $PASS SKILL.md is concise ($LINE_COUNT lines), references optional"
    ((PASSES++))
fi

#
# 6. Reference Link Validation
#
echo ""
echo "6. Reference Links:"

BROKEN_LINKS=0
VALID_LINKS=0

while IFS= read -r link; do
    [ -z "$link" ] && continue
    FILE=$(echo "$link" | sed 's/.*(\([^)]*\))/\1/')
    if [ -f "$SKILL_PATH/$FILE" ]; then
        ((VALID_LINKS++))
    else
        if [ $BROKEN_LINKS -eq 0 ]; then
            echo -e "  $WARN Broken reference links found:"
        fi
        echo -e "       $FILE"
        ((BROKEN_LINKS++))
    fi
done < <(grep -oE '\[.*\]\([^)]+\.md\)' "$SKILL_FILE" 2>/dev/null || true)

if [ $BROKEN_LINKS -eq 0 ] && [ $VALID_LINKS -gt 0 ]; then
    echo -e "  $PASS All $VALID_LINKS reference links valid"
    ((PASSES++))
elif [ $VALID_LINKS -eq 0 ]; then
    echo -e "  $PASS No reference links (optional)"
    ((PASSES++))
else
    ((WARNINGS++))
fi

#
# 7. Naming Convention Check
#
echo ""
echo "7. Naming Convention:"

SKILL_FIRST_WORD=$(echo "$SKILL_NAME" | cut -d- -f1)
COMMON_VERBS="create manage setup generate analyze process coordinate build handle configure deploy execute extract transform validate parse render compile"

if echo "$COMMON_VERBS" | grep -qw "$SKILL_FIRST_WORD"; then
    echo -e "  $PASS Naming follows verb-noun pattern: '$SKILL_FIRST_WORD-...'"
    ((PASSES++))
else
    echo -e "  $WARN First word '$SKILL_FIRST_WORD' is not a common verb (verify action-oriented)"
    ((WARNINGS++))
fi

#
# 8. XML Tags Summary
#
echo ""
echo "8. XML Tags Found:"
echo ""

grep -oE '<[a-z_]+>' "$SKILL_FILE" | sort | uniq -c | sort -rn | head -10 | while read count tag; do
    echo "       $count × $tag"
done

#
# Summary
#
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}Passed:${NC}   $PASSES"
echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "  ${RED}Errors:${NC}   $ERRORS"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ PASS - All validations passed!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  PASS WITH WARNINGS - Skill is valid but has $WARNINGS warning(s)${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ FAIL - Skill has $ERRORS critical error(s)${NC}"
    exit 1
fi
