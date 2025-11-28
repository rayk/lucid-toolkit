# TOON Format Reference

Token-Oriented Object Notation - ~40% token savings vs JSON for structured data.

---

## Syntax

### Array with Header
```toon
items[N]{field1,field2,field3}:
  value1,value2,value3
  value1,value2,value3
```

| Element | Syntax | Example |
|---------|--------|---------|
| Array header | `name[N]{fields}:` | `results[5]{id,name}:` |
| Count | `[N]` | `[10]` = 10 items |
| Fields | `{f1,f2}` | `{position,path,desc}` |
| Row | Comma-separated | `1,src/file.ts,Desc` |

### Nested Object
```toon
config:
  host: localhost
  port: 8080
  items[2]{key,value}:
    timeout,30
    retries,3
```

---

## When to Use

| Use TOON (40% savings) | Use JSON (no savings) |
|------------------------|----------------------|
| File search results | Yes/no answers |
| Process steps | Complex nested objects |
| Config lookups | Non-uniform structures |
| Any uniform array | Deep hierarchies (>2 levels) |

---

## Quoting Rules

Quote values containing: `,` `:` or leading/trailing whitespace

```toon
# Unquoted
items[2]{name,desc}:
  Widget,Simple item
  Gadget,Another item

# Quoted
items[2]{name,desc}:
  "Widget, Pro",Has comma
  Tool,"Description: colon"
```

---

## Token Comparison

| Pattern | JSON | TOON | Savings |
|---------|------|------|---------|
| 10-item file list | 3000 | 1800 | 40% |
| 7-step flow | 2500 | 1500 | 40% |
| 10 config values | 2000 | 1200 | 40% |
| Yes/no answer | 1000 | 1000 | 0% |

---

## Common Mistakes

1. **Different fields per row** → Use JSON instead
2. **Row count ≠ header count** → Match fields exactly
3. **Unquoted special chars** → Quote commas/colons
